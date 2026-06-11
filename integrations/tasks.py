##########################
# integrations/tasks.py
##########################

import logging
from decimal import Decimal
from datetime import datetime

from celery import shared_task
from django.utils import timezone

from integrations.models import InboundWebhookEvent
from integrations.services_tibber import (
    upsert_tibber_interval_readings,
)

from core.models import IntervalReading, MeterRegister

from core.models import Meter
from core.constants.obis import OBIS_MAP

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


############################################################
# 🔵 1. WEBHOOK PROCESSING (unverändert – nur leicht cleaner)
############################################################


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

            # ✅ 1. METER
            serial = r["meter_serial"]

            meter, _ = Meter.objects.get_or_create(
                serial_number=serial,
                defaults={"tenant": tenant},
            )

            # ✅ 2. ZEIT
            ts = datetime.fromisoformat(r["ts_start"].replace("Z", "+00:00"))
            received_at = timezone.now()

            # ✅ 3. OBIS
            obis = r.get("obis", "1.8.0")
            obis_meta = OBIS_MAP.get(obis, {})
            unit = r.get("unit", obis_meta.get("unit", "kWh"))

            # ✅ 4. VALUE
            value = Decimal(str(r["value_kwh"]))

            # ✅ 5. LATE LOGIC
            delay = (received_at - ts).total_seconds()
            is_late = delay > 60

            # ✅ 6. DUPLICATES
            existing = IntervalReading.objects.filter(
                meter=meter,
                ts_start=ts,
                obis_code=obis,
            ).first()

            if existing:
                if existing.value == value:
                    continue
                else:
                    existing.value = value
                    existing.received_at = received_at
                    existing.is_late = is_late
                    existing.ingestion_delay_seconds = int(delay)
                    existing.save()
                    continue

            # ✅ 7. REGISTER
            MeterRegister.objects.get_or_create(meter=meter, obis_code=obis)

            # ✅ 8. SAVE
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


############################################################
# 🔵 2. TIBBER SYNC (FINAL VERSION ✅)
############################################################


def get_hours_to_fetch(meter):
    """
    Dynamisches Fetch-Fenster:
    - kein Startwert → 72h
    - sonst delta + buffer
    """

    last = IntervalReading.objects.filter(meter=meter).order_by("-ts_start").first()

    if not last:
        return 72

    now = timezone.now()
    delta = now - last.ts_start

    hours = int(delta.total_seconds() / 3600) + 2  # buffer

    return min(max(hours, 2), 72)


@shared_task
def sync_tibber():
    """
    ✅ Stable Tibber Sync:
    - nur Meter mit tibber_home_id
    - dynamisches Zeitfenster
    - robust gegen Fehler
    """

    results = []

    meters = (
        Meter.objects.filter(integration_type="tibber")
        .exclude(tibber_home_id__isnull=True)
        .exclude(tibber_home_id="")
    )

    if not meters.exists():
        return {"status": "no_tibber_meters"}

    for meter in meters:
        user = getattr(meter, "owner_user", None)

        # ✅ HARTE VALIDIERUNG
        if not user:
            logger.warning(f"Skipping meter {meter.id} → missing owner_user")
            continue

        if not meter.tibber_home_id:
            logger.warning(f"Skipping meter {meter.id} → missing tibber_home_id")
            continue
        try:
            hours = get_hours_to_fetch(meter)

            result = upsert_tibber_interval_readings(
                meter=meter,
                home_id=meter.tibber_home_id,
                user=user,
                hours=hours,
            )

            written = result.get("written", 0)

            # ✅ optional tracking
            if written > 0:
                meter.last_tibber_sync = timezone.now()
                meter.save(update_fields=["last_tibber_sync"])

            results.append(
                {
                    "meter_id": str(meter.id),
                    "hours": hours,
                    "written": written,
                }
            )

        except Exception as e:
            logger.exception(
                f"tibber.sync.failed meter={meter.id} user={getattr(user, 'id', 'none')}"
            )
            results.append(
                {
                    "meter_id": str(meter.id),
                    "error": str(e),
                }
            )

    return {
        "status": "ok",
        "meters_processed": len(results),
        "results": results,
    }
