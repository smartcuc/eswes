#
#
#

# integrations/mqtt_normalizer.py
import json
import re
from datetime import datetime, timezone as dt_timezone

DEFAULT_OBIS = "1.8.0"
DEFAULT_UNIT = "kWh"


def _iso_from_unix(ts: int) -> str:
    return (
        datetime.fromtimestamp(ts, tz=dt_timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _iso_from_any(value) -> str:
    # akzeptiert ISO-String oder Unix-Sekunden (int)
    if isinstance(value, int):
        return _iso_from_unix(value)
    if isinstance(value, str):
        return (
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            .isoformat()
            .replace("+00:00", "Z")
        )
    # fallback: "jetzt"
    return datetime.now(tz=dt_timezone.utc).isoformat().replace("+00:00", "Z")


def serial_from_topic(topic: str) -> str | None:
    """
    Unterstützt z.B.:
      - meter/<SN>/readings
      - device/<SN>/realtime  (häufig) 【3-9d97a7】
    """
    m = re.match(r"^(meter|device)/([^/]+)/", topic)
    return m.group(2) if m else None


def normalize_message(
    topic: str, payload_bytes: bytes, profile: str = "generic"
) -> tuple[str | None, dict | None]:
    """
    Returns: (meter_serial, normalized_payload_for_InboundWebhookEvent)
    normalized_payload shape:
      {"readings": [ {meter_serial, ts_start, obis, value_kwh, unit}, ... ]}
    """
    try:
        msg = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None, None

    sn = (
        msg.get("meter_serial")
        or msg.get("sn")
        or msg.get("serial")
        or serial_from_topic(topic)
    )

    # -------- Profile: iammeter-like (topic device/{SN}/realtime) --------
    # Viele Systeme nutzen Topic device/{SN}/realtime. 【3-9d97a7】
    # Beispielhafte Felder: time/unix_seconds, und Messwerte in Keys.
    if profile == "iammeter":
        if not sn:
            sn = serial_from_topic(topic)

        ts_start = _iso_from_any(
            msg.get("ts_start")
            or msg.get("time")
            or msg.get("unix_seconds")
            or msg.get("timestamp")
        )
        readings = []

        # Mappe typische Keys -> OBIS (du kannst erweitern)
        key_map = {
            "kwh_import": ("1.8.0", "kWh"),
            "kwh_export": ("2.8.0", "kWh"),
            "power_w": ("16.7.0", "W"),
        }
        for k, (obis, unit) in key_map.items():
            if k in msg:
                readings.append(
                    {
                        "meter_serial": sn,
                        "ts_start": ts_start,
                        "obis": obis,
                        "value_kwh": msg[
                            k
                        ],  # bei W ist es eigentlich "value", wir nutzen trotzdem value_kwh Feld aus deinem bisherigen Schema
                        "unit": unit,
                    }
                )

        # Falls Gateway schon arrays liefert:
        if "readings" in msg and isinstance(msg["readings"], list):
            for r in msg["readings"]:
                readings.append(
                    {
                        "meter_serial": r.get("meter_serial", sn),
                        "ts_start": _iso_from_any(
                            r.get("ts_start") or r.get("time") or r.get("timestamp")
                        ),
                        "obis": r.get("obis", DEFAULT_OBIS),
                        "value_kwh": r.get("value_kwh", r.get("value")),
                        "unit": r.get("unit", DEFAULT_UNIT),
                    }
                )

        return sn, {"readings": readings} if readings else (sn, None)

    # -------- Profile: generic --------
    # 1) payload hat readings[]
    if isinstance(msg, dict) and isinstance(msg.get("readings"), list):
        readings = []
        for r in msg["readings"]:
            r_sn = r.get("meter_serial") or r.get("sn") or sn
            readings.append(
                {
                    "meter_serial": r_sn,
                    "ts_start": _iso_from_any(
                        r.get("ts_start") or r.get("timestamp") or r.get("time")
                    ),
                    "obis": r.get("obis", DEFAULT_OBIS),
                    "value_kwh": r.get("value_kwh", r.get("value")),
                    "unit": r.get("unit", DEFAULT_UNIT),
                }
            )
        return sn or (readings[0]["meter_serial"] if readings else None), {
            "readings": readings
        }

    # 2) payload ist single-reading
    if (
        sn
        and ("ts_start" in msg or "timestamp" in msg or "time" in msg)
        and ("value" in msg or "value_kwh" in msg)
    ):
        return sn, {
            "readings": [
                {
                    "meter_serial": sn,
                    "ts_start": _iso_from_any(
                        msg.get("ts_start") or msg.get("timestamp") or msg.get("time")
                    ),
                    "obis": msg.get("obis", DEFAULT_OBIS),
                    "value_kwh": msg.get("value_kwh", msg.get("value")),
                    "unit": msg.get("unit", DEFAULT_UNIT),
                }
            ]
        }

    return None, None
