##########################
# integrations/tasks.py
##########################
import logging

logger = logging.getLogger(__name__)

"""
Async Verarbeitung von Inbound Webhook Events.

- Idempotent: verarbeitet jeden Event nur 1x (processed_at)
- Robust: einzelne Reading-Fehler werden gesammelt
- Audit: schreibt Status + error_message zurück
"""
import logging
from decimal import Decimal
from datetime import datetime

from celery import shared_task
from django.utils import timezone

from integrations.models import InboundWebhookEvent
from metering.models import Meter, IntervalReading, MeterRegister

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# 🔥 NEU: OBIS Mapping
from metering.obis import OBIS_MAP

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def process_inbound_webhook_event(self, event_id: str):

    evt = InboundWebhookEvent.objects.select_related("tenant").get(id=event_id)

    if evt.processed_at:
        logger.info("event.already_processed")
        return {"status": "already_processed"}

    written = 0
    final_status = None
    final_error = ""

    try:
        payload = evt.payload or {}
        tenant = evt.tenant

        for r in payload.get("readings", []):

            # ✅ 1. METER MAPPING
            serial = r["meter_serial"]

            meter, _ = Meter.objects.get_or_create(
                serial_number=serial, defaults={"tenant": tenant}
            )

            if meter.tenant_id != tenant.id:
                logger.warning("Meter tenant mismatch")

            # ✅ 2. ZEITEN
            ts = datetime.fromisoformat(r["ts_start"].replace("Z", "+00:00"))
            received_at = timezone.now()

            # ✅ 3. OBIS
            obis = r.get("obis", "1.8.0")

            obis_meta = OBIS_MAP.get(obis, {})
            unit = r.get("unit", obis_meta.get("unit", "kWh"))

            # ✅ 4. VALUE
            value = Decimal(str(r["value_kwh"]))

            # ✅ 5. LATE DATA LOGIC
            delay = (received_at - ts).total_seconds()
            is_late = delay > 60  # ⚠️ anpassbar

            # ✅ 6. DUPLICATE DETECTION
            existing = IntervalReading.objects.filter(
                meter=meter, ts_start=ts, obis_code=obis
            ).first()

            if existing:
                if existing.value == value:
                    # echtes Duplicate → überspringen
                    logger.info("duplicate detected")
                    continue
                else:
                    # Korrektur → Update
                    logger.info("value correction detected")

                    existing.value = value
                    existing.received_at = received_at
                    existing.is_late = is_late
                    existing.ingestion_delay_seconds = int(delay)
                    existing.save()

                    continue

            # ✅ 7. OPTIONAL: REGISTER
            MeterRegister.objects.get_or_create(meter=meter, obis_code=obis)

            # ✅ 8. SPEICHERN
            IntervalReading.objects.create(
                tenant=tenant,
                meter=meter,
                ts_start=ts,
                received_at=received_at,
                obis_code=obis,
                value=value,
                unit=unit,
                is_late=is_late,
                is_duplicate=False,
                ingestion_delay_seconds=int(delay),
            )

            written += 1

        # ✅ SUCCESS
        final_status = InboundWebhookEvent.Status.OK

        evt.status = final_status
        evt.error_message = ""
        evt.processed_at = timezone.now()
        evt.save(update_fields=["status", "error_message", "processed_at"])

        logger.info("event.processing.succeeded")

        return {"status": "ok", "written": written}

    except Exception as e:
        logger.exception("event.processing.failed")

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2**self.request.retries)

        final_status = InboundWebhookEvent.Status.ERROR
        final_error = str(e)

        evt.status = final_status
        evt.error_message = final_error[:2000]
        evt.processed_at = timezone.now()
        evt.save(update_fields=["status", "error_message", "processed_at"])

        return {"status": "error"}

    finally:
        # ✅ REALTIME PUSH
        if final_status:
            try:
                channel_layer = get_channel_layer()

                async_to_sync(channel_layer.group_send)(
                    "events",
                    {
                        "type": "send_event",
                        "data": {
                            "event_id": str(evt.id),
                            "tenant_id": str(evt.tenant_id),
                            "status": final_status,
                            "written": written,
                            "error_message": final_error,
                            "processed_at": (
                                evt.processed_at.isoformat()
                                if evt.processed_at
                                else None
                            ),
                        },
                    },
                )
            except Exception:
                logger.exception("realtime.push.failed")
