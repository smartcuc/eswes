##############################################
# core/management/commands/mqtt_consume.py
##############################################

# ============================================================
# MQTT CONSUMER – INGEST PIPELINE
# ============================================================

import json
import logging

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from devices.models import Home, Device, DeviceMetric

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
