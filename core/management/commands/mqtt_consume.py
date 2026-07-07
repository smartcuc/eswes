##############################################
# core/management/commands/mqtt_consume.py
##############################################

# ============================================================
# MQTT CONSUMER – INGEST PIPELINE
# ============================================================

import json
import logging
import os
import ssl

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from devices.models import Home, Device, DeviceMetric
from integrations.mqtt_profiles import get_parser

import paho.mqtt.client as mqtt


logger = logging.getLogger(__name__)

LAST_MESSAGE_TS = None


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

    if len(parts) != 3:
        raise ValueError("Invalid topic format")

    home_token = parts[1].strip()
    device_identifier = parts[2].strip()


    # ========================================================
    # ✅ HOME LOOKUP
    # ========================================================

    #home = Home.objects.get(mqtt_token=token)
    
    print(f"HOME TOKEN DEBUG: {home_token}")

    # ✅ DAS IST DIE KORREKTE ZEILE
    home = Home.objects.get(mqtt_token=home_token)


    # ========================================================
    # ✅ DEVICE LOOKUP / AUTO-PROVISION
    # ========================================================

    device = Device.objects.filter(
        home=home,
        identifier=device_identifier
    ).first()
##
    print(
    f"MQTT DEBUG | topic={topic} "
    f"device={device_identifier} "
    f"found={bool(device)} "
    f"auto_prov={auto_prov}"
)
##
    # ✅ AUTO-PROVISION FIRST
    if not device and auto_prov:
####
        print(
                f"MQTT DEBUG | creating device {device_identifier}"
            )  
####

        device = Device.objects.create(
            home=home,
            identifier=device_identifier
        )
        print(f"Auto-provisioned device={device_identifier}")
    
    # ✅ MAGIC MOMENT DANACH
    if device and not device.configured:
        device.configured = True
        device.save(update_fields=["configured"])
        print(f"✅ Device {device_identifier} connected")


    # ========================================================
    # ✅ PAYLOAD PARSING
    # ========================================================
    # raw payload kommt als bytes rein
    payload_str = payload.decode("utf-8")

    print(f"RAW PAYLOAD: {payload_str}")

    metrics = {}
    state = {}
    meta = {}

    # ========================================================
    # ✅ PAYLOAD PARSING (ROBUST)
    # ========================================================

    try:
        data = json.loads(payload_str)

        # ✅ Case 1: {"metrics": {...}}
        if isinstance(data, dict) and "metrics" in data:
            metrics = data.get("metrics", {})
            state = data.get("state", {})
            meta = data.get("meta", {})

        # ✅ Case 2: {"val": 229.8}
        elif isinstance(data, dict) and "val" in data:

            metric_name = data.get(
                "metric",
                "value"
            )

            metrics = {
                metric_name: data["val"]
            }

            meta = data


        # ✅ Case 3: ioBroker wrapper
        elif isinstance(data, dict) and "message" in data:
            try:
                val = float(data["message"])
                metrics = {"value": val}
                meta = data
            except:
                print("Invalid ioBroker message")
                return

        # ✅ Case 4: generic dict
        elif isinstance(data, dict):
            metrics = data

        else:
            metrics = {"value": float(data)}

    except Exception:
        # ✅ fallback plain string
        try:
            metrics = {"value": float(payload_str)}
        except:
            print(f"Invalid payload: {payload_str}")
            return

    # ========================================================
    # ✅ TIMESTAMP + SOURCE
    # ========================================================

    ts = None

    # ✅ try extract timestamp from meta
    if isinstance(meta, dict):
        if "ts" in meta:
            try:
                ts = timezone.datetime.fromtimestamp(meta["ts"] / 1000, tz=timezone.utc)
            except:
                ts = None
        elif "timestamp" in meta:
            ts = parse_ts(meta["timestamp"])

    if not ts:
        ts = timezone.now()

    source = str(meta.get("from") or "mqtt")[:64] if isinstance(meta, dict) else "mqtt"

    print(f"METRICS DEBUG: {metrics}")
    print(f"STATE DEBUG: {state}")
    print(f"SOURCE: {source}")

    # ========================================================
    # ✅ DEVICE ACTIVITY UPDATE
    # ========================================================

    device.last_seen = ts or timezone.now()
    device.save(update_fields=["last_seen"])
    
    profile_slug = (
        device.mqtt_profile.slug
        if device.mqtt_profile
        else "generic"
    )

    parser = get_parser(profile_slug)

    metrics = parser.normalize(metrics)

    # ========================================================
    # ✅ METRICS INGEST
    # ========================================================

    for key, value in metrics.items():
        DeviceMetric.objects.create(
            device=device,
            timestamp=ts,
            metric_key=str(key),
            value=_to_float(value),
            unit="",
            data={
                "source": source,
                "raw": meta,
            },
        )

    # ========================================================
    # ✅ STATE INGEST (separat gespeichert)
    # ========================================================

    for key, value in state.items():
        DeviceMetric.objects.create(
            device=device,
            timestamp=ts,
            metric_key=f"state.{key}",
            value=_to_float(value),
            unit="",
            data={
                "source": source,
                "raw": meta,
            },
        )


# ============================================================
# ✅ HELPERS
# ============================================================

def _to_float(val):
    try:
        return float(val)
    except Exception:
        return None


# ============================================================
# ✅ DJANGO MANAGEMENT COMMAND ENTRYPOINT
# ============================================================

class Command(BaseCommand):
    help = "MQTT Consumer"

    def handle(self, *args, **options):
        print("Starting MQTT consumer...")

        host = os.getenv("MQTT_HOST", "sharegy.de")
        port = int(os.getenv("MQTT_PORT", 8883))
        user = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")

        print(f"Connecting to MQTT {host}:{port} ...")

        # ✅ V2 Callback API verwenden (KRITISCH)
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        # ✅ Auth
        if user and password:
            client.username_pw_set(user, password)

        # ✅ TLS (DEV/TEST – PROD später härten)
        client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)

        # ✅ Callbacks setzen
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # ✅ Connect
        client.connect(host, port)

        print("MQTT loop starting ✅")

        try:
            client.loop_forever()
        except KeyboardInterrupt:
            print("MQTT stopped")
            client.disconnect()

    # ---------------------------
    # MQTT CALLBACKS (V2!)
    # ---------------------------

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("MQTT connected ✅")
            client.subscribe("h/+/+")

        else:
            print(f"MQTT failed rc={reason_code}")

    def on_message(self, client, userdata, msg):      
        global LAST_MESSAGE_TS

        LAST_MESSAGE_TS = timezone.now()

        try:
            ingest(
                topic=msg.topic,
                payload=msg.payload,
                auto_prov=True,
            )
        except Exception as e:
            print(f"Ingest failed topic={msg.topic} err={e}")


# ============================================================
# ✅ MQTT INGEST HEALTH
# ============================================================

def check_ingest_health(timeout_seconds=120):
    from django.utils import timezone
    from datetime import timedelta

    if not LAST_MESSAGE_TS:
        return False, "no_messages"

    if LAST_MESSAGE_TS < timezone.now() - timedelta(seconds=timeout_seconds):
        return False, "stalled"

    return True, "ok"
