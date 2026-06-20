##############################################
# core/management/commands/mqtt_consume.py
##############################################

# ============================================================
# MQTT CONSUMER – INGEST PIPELINE
# ============================================================

import json
import logging
import os

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from devices.models import Home, Device, DeviceMetric

import paho.mqtt.client as mqtt


logger = logging.getLogger(__name__)


# ============================================================
# ✅ TIMESTAMP PARSER (robust)
# ============================================================

def parse_ts(ts_str):
    if not ts_str:
        return timezone.now()

    dt = parse_datetime(ts_str)
    if dt is None:
        return timezone.now()

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone=timezone.utc)

    return dt.astimezone(timezone.utc)


# ============================================================
# ✅ INGEST ENTRYPOINT
# ============================================================

def ingest(topic: str, payload: bytes, auto_prov: bool):
    parts = topic.split("/")

    if len(parts) != 4:
        raise ValueError(f"Invalid topic: {topic}")

    prefix, token, kind, device_id = parts

    if prefix != "home" or kind != "device":
        raise ValueError(f"Invalid topic: {topic}")

    # ========================================================
    # ✅ HOME LOOKUP
    # ========================================================

    home = Home.objects.get(mqtt_token=token)

    # ========================================================
    # ✅ DEVICE LOOKUP / AUTO-PROVISION
    # ========================================================

    device = Device.objects.filter(
        home=home,
        identifier=device_id
    ).first()

    if device is None:
        if not auto_prov:
            raise ValueError(f"Device not provisioned: {device_id}")

        device = Device.objects.create(
            home=home,
            identifier=device_id,
            name=device_id,
        )

        logger.info("Auto-provisioned device=%s", device_id)

    # ========================================================
    # ✅ PAYLOAD PARSING
    # ========================================================

    data = json.loads(payload.decode("utf-8"))

    ts = parse_ts(data.get("ts"))
    metrics = data.get("metrics") or {}
    state = data.get("state") or {}
    meta = data.get("meta") or {}

    source = str(meta.get("source") or "mqtt")[:64]

    # ========================================================
    # ✅ DEVICE ACTIVITY UPDATE
    # ========================================================

    device.last_seen = ts
    device.save(update_fields=["last_seen"])

    # ========================================================
    # ✅ METRICS INGEST (clean format)
    # ========================================================

    for key, value in metrics.items():
        DeviceMetric.objects.create(
            device=device,
            timestamp=ts,
            metric=str(key),
            value=_to_float(value),
            unit=_guess_unit(key),
            data={"source": source},
        )

    # ========================================================
    # ✅ STATE → also store as metrics
    # ========================================================

    for key, value in state.items():
        DeviceMetric.objects.create(
            device=device,
            timestamp=ts,
            metric=f"state.{key}",
            value=_to_float(value),
            unit="",
            data={"source": source},
        )


# ============================================================
# ✅ HELPERS
# ============================================================

def _to_float(val):
    try:
        return float(val)
    except Exception:
        return None


def _guess_unit(metric: str) -> str:
    m = metric.lower()

    if "power" in m:
        return "W"
    if "energy" in m:
        return "kWh"
    if "voltage" in m:
        return "V"
    if "current" in m:
        return "A"

    return ""

# ============================================================
# ✅ DJANGO MANAGEMENT COMMAND ENTRYPOINT
# ============================================================


class Command(BaseCommand):
    help = "MQTT Consumer"

    def handle(self, *args, **options):
        print("Starting MQTT consumer...")

        host = os.getenv("MQTT_HOST", "127.0.0.1")
        port = int(os.getenv("MQTT_PORT", 1883))
        user = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")
        use_tls = os.getenv("MQTT_TLS", "False") == "True"

        client_id = os.getenv("MQTT_CLIENT_ID", "django-mqtt")

        print(f"Connecting to MQTT {host}:{port} ...")

        import ssl
        client = mqtt.Client(client_id=client_id)
                
        if use_tls:
            client.tls_set(cert_reqs=ssl.CERT_NONE)
            client.tls_insecure_set(True)


        if user and password:
            client.username_pw_set(user, password)

        if use_tls:
            client.tls_set()
            client.tls_insecure_set(True)

        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(host, port)
        client.loop_forever()


    # ---------------------------
    # MQTT
    # ---------------------------

    def on_connect(self, client, userdata, flags, rc):
        print(f"MQTT connected rc={rc}")
        client.subscribe("home/+/device/+")

    def on_message(self, client, userdata, msg):
        try:
            ingest(
                topic=msg.topic,
                payload=msg.payload,
                auto_prov=True
            )
        except Exception as e:
            print(f"Ingest failed topic={msg.topic} err={e}")
