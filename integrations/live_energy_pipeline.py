######################################
# integrations/live_energy_pipeline.py
######################################

from datetime import datetime, timedelta
from collections import defaultdict
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_naive, make_aware
from datetime import timezone as dt_timezone
from django.utils import timezone

from integrations.tasks import insert_interval_reading
from asgiref.sync import sync_to_async

METER_STATE = {}
SLOT_BUFFER = defaultdict(
    lambda: {
        "consumption": 0.0,
        "production": 0.0,
    }
)


def process_live_measurement(meter_id, measurement):

    ts = parse_datetime(measurement["timestamp"])

    if is_naive(ts):
        ts = make_aware(ts, dt_timezone.utc)
    else:
        ts = ts.astimezone(dt_timezone.utc)

    consumption = measurement.get("accumulatedConsumption")
    production = measurement.get("accumulatedProduction")

    if consumption is None:
        return

    state = METER_STATE.get(meter_id)

    if not state:
        METER_STATE[meter_id] = {
            "last_consumption": consumption,
            "last_production": measurement.get("accumulatedProduction"),
            "last_timestamp": ts,
        }
        return

    last_c = state["last_consumption"]
    last_p = state.get("last_production")

    delta_c = (
        consumption - last_c if consumption is not None and last_c is not None else 0
    )
    delta_p = (
        production - last_p if production is not None and last_p is not None else 0
    )

    if delta_c < -1:
        print(f"🔄 reset consumption {meter_id}")
        state["last_consumption"] = consumption
        delta_c = 0

    if delta_p is not None and delta_p < -1:
        print(f"🔄 reset production {meter_id}")
        state["last_production"] = production
        delta_p = 0

    if delta_c < 0:
        delta_c = 0

    if delta_p is not None and delta_p < 0:
        delta_p = 0

    slot = floor_to_15min(ts)

    SLOT_BUFFER[(meter_id, slot)]["consumption"] += float(delta_c)

    if production is not None:
        SLOT_BUFFER[(meter_id, slot)]["production"] += float(delta_p)

    # ✅ IMMER STATE UPDATE
    state["last_consumption"] = consumption
    state["last_production"] = production
    state["last_timestamp"] = ts

    print(f"⚡ {meter_id[:6]} ΔC {delta_c:.4f} ΔP {delta_p:.4f} → {slot}")


async def flush_ready_slots():

    now = timezone.now()
    to_delete = []

    for (meter_id, slot), values in SLOT_BUFFER.items():

        consumption = values["consumption"]
        production = values["production"]
        net = consumption - production

        if now - slot < timedelta(minutes=15):
            continue

        await sync_to_async(insert_interval_reading)(
            {
                "meter_id": meter_id,
                "ts_start": slot,
                "obis_code": "1.8.0",
                "value": round(consumption, 6),
                "unit": "kWh",
                "source": "tibber_live",
            }
        )

        await sync_to_async(insert_interval_reading)(
            {
                "meter_id": meter_id,
                "ts_start": slot,
                "obis_code": "2.8.0",
                "value": round(production, 6),
                "unit": "kWh",
                "source": "tibber_live",
            }
        )

        await sync_to_async(insert_interval_reading)(
            {
                "meter_id": meter_id,
                "ts_start": slot,
                "obis_code": "1.8.0-NET",
                "value": round(net, 6),
                "unit": "kWh",
                "source": "tibber_live",
            }
        )

        print(
            f"✅ FLUSH {meter_id[:6]} {slot} → C:{consumption:.4f} P:{production:.4f} NET:{net:.4f}"
        )

        to_delete.append((meter_id, slot))

    for key in to_delete:
        del SLOT_BUFFER[key]


def floor_to_15min(ts: datetime):
    minutes = (ts.minute // 15) * 15
    return ts.replace(
        minute=minutes, second=0, microsecond=0, tzinfo=ts.tzinfo  # ✅ wichtig!
    )
