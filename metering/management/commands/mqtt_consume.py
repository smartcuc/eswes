##############################################
# metering/management/commands/mqtt_consume.py
##############################################


import json
import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from metering.models import Meter, IntervalReading
from energy.models import Device, DeviceMetric

logger = logging.getLogger("metering.mqtt")

TOPIC_RE = re.compile(r"^energy/(?P<device_type>[^/]+)/(?P<device_id>[^/]+)/telemetry$")
OBIS_RE = re.compile(r"^\d+\.\d+\.\d+$")  # z.B. 1.8.0


def parse_ts(ts_str: str):
    dt = parse_datetime(ts_str)
    if dt is None:
        raise ValueError(f"Invalid ts format: {ts_str}")
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_decimal(v: Any) -> Decimal:
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Invalid numeric value: {v!r}")


def guess_unit(metric: str) -> str:
    m = metric.lower()
    if m.endswith("_w"):
        return "W"
    if m.endswith("_wh"):
        return "Wh"
    if m.endswith("_kwh"):
        return "kWh"
    if m.endswith("_eur_kwh"):
        return "EUR/kWh"
    if m.endswith("_soc"):
        return "%"
    if m.endswith("_v"):
        return "V"
    if m.endswith("_a"):
        return "A"
    return ""


class Command(BaseCommand):
    help = "Run MQTT consumer for telemetry ingestion (meter + devices)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--host", default=getattr(settings, "MQTT_HOST", "127.0.0.1")
        )
        parser.add_argument(
            "--port", type=int, default=getattr(settings, "MQTT_PORT", 1883)
        )
        parser.add_argument(
            "--topic", default=getattr(settings, "MQTT_TOPIC", "energy/+/+/telemetry")
        )
        parser.add_argument("--qos", type=int, default=getattr(settings, "MQTT_QOS", 1))

    def handle(self, *args, **opts):
        host = opts["host"]
        port = opts["port"]
        topic = opts["topic"]
        qos = opts["qos"]

        username = getattr(settings, "MQTT_USERNAME", "")
        password = getattr(settings, "MQTT_PASSWORD", "")
        use_tls = getattr(settings, "MQTT_TLS", False)
        auto_prov = getattr(settings, "MQTT_AUTO_PROVISION", False)

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        if username:
            client.username_pw_set(username, password)

        if use_tls:
            client.tls_set()

        # LWT für Ops
        client.will_set(
            "energy/system/mqtt_consumer/status",
            payload="offline",
            qos=1,
            retain=True,
        )

        def on_connect(c, userdata, flags, reason_code, properties):
            logger.info("MQTT connected rc=%s", reason_code)
            c.publish(
                "energy/system/mqtt_consumer/status", "online", qos=1, retain=True
            )
            c.subscribe(topic, qos=qos)
            logger.info("Subscribed %s qos=%s", topic, qos)

        def on_disconnect(c, userdata, reason_code, properties):
            logger.warning("MQTT disconnected rc=%s", reason_code)

        def on_message(c, userdata, msg):
            try:
                self.ingest(topic=msg.topic, payload=msg.payload, auto_prov=auto_prov)
            except Exception as e:
                # production-ready: nicht crashen
                logger.exception("Ingest failed topic=%s err=%s", msg.topic, e)

        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message

        logger.info("Connecting to MQTT %s:%s ...", host, port)
        client.connect(host, port, keepalive=45)
        client.loop_forever(retry_first_connection=True)

    def ingest(self, topic: str, payload: bytes, auto_prov: bool):
        m = TOPIC_RE.match(topic)
        if not m:
            raise ValueError(f"Invalid topic: {topic}")

        device_type = m.group("device_type").strip()
        device_id = m.group("device_id").strip()

        data = json.loads(payload.decode("utf-8"))
        ts = parse_ts(data.get("ts"))
        metrics: Dict[str, Any] = data.get("metrics") or {}
        state: Dict[str, Any] = data.get("state") or {}
        meta: Dict[str, Any] = data.get("meta") or {}

        source = str(meta.get("source") or "mqtt")[:64]

        # --- Device Lookup / Provision ---
        device = Device.objects.filter(device_type=device_type, name=device_id).first()

        if device is None:
            if not auto_prov:
                raise ValueError(f"Device not provisioned: {device_type}/{device_id}")
            device = Device.objects.create(
                name=device_id,
                device_type=(
                    device_type
                    if device_type in dict(Device.DEVICE_TYPE).keys()
                    else "other"
                ),
                controllable=False,
            )
            logger.info("Auto-provisioned device=%s/%s", device_type, device_id)

        # --- Meter special: OBIS -> IntervalReading ---
        if device_type == "meter":
            meter = self._resolve_meter(device_id)
            if meter is None:
                raise ValueError(f"Meter not found (id/serial): {device_id}")

            # Speichere OBIS als IntervalReading; Non-OBIS als DeviceMetric
            for k, v in metrics.items():
                key = str(k)
                if OBIS_RE.match(key):
                    self._upsert_intervalreading(
                        meter=meter,
                        ts=ts,
                        obis_code=key,
                        value=v,
                        source=source,
                    )
                else:
                    self._upsert_devicemetric(
                        device, ts, key, v, unit=guess_unit(key), source=source
                    )

            # optional: state.* ebenfalls speichern
            for k, v in state.items():
                self._upsert_devicemetric(
                    device, ts, f"state.{k}", v, unit="", source=source
                )

            return

        # --- All other device types: store everything in DeviceMetric ---
        for k, v in metrics.items():
            key = str(k)
            self._upsert_devicemetric(
                device, ts, key, v, unit=guess_unit(key), source=source
            )

        for k, v in state.items():
            self._upsert_devicemetric(
                device, ts, f"state.{k}", v, unit="", source=source
            )

    def _resolve_meter(self, device_id: str) -> Optional[Meter]:
        # device_id kann UUID (Meter.id) oder serial_number sein
        meter = Meter.objects.filter(id=device_id).first()
        if meter:
            return meter
        return Meter.objects.filter(serial_number=device_id).first()

    def _upsert_intervalreading(
        self, meter: Meter, ts, obis_code: str, value: Any, source: str
    ):
        # Steady-State: value ist kWh im Intervall
        # ts_end: optional 15min (Konvention)
        ts_end = ts + timezone.timedelta(minutes=15)

        with transaction.atomic():
            try:
                IntervalReading.objects.update_or_create(
                    meter=meter,
                    ts_start=ts,
                    obis_code=obis_code,
                    defaults={
                        "tenant": getattr(meter, "tenant", None),
                        "ts_end": ts_end,
                        "value": to_decimal(value),
                        "unit": "kWh",
                        "source": source,
                    },
                )
            except IntegrityError:
                # Bei Parallelität: idempotent
                pass

    def _upsert_devicemetric(
        self, device: Device, ts, metric: str, value: Any, unit: str, source: str
    ):
        with transaction.atomic():
            try:
                DeviceMetric.objects.update_or_create(
                    device=device,
                    ts=ts,
                    metric=metric[:64],
                    defaults={
                        "value": to_decimal(value),
                        "unit": (unit or "")[:16],
                        "source": source[:64],
                    },
                )
            except IntegrityError:
                pass
