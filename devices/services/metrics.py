#############################
# devices/services/metrics.py
#############################

from django.utils import timezone
import logging
from django.core.cache import cache

from devices.models import DeviceMetric, DeviceLatestMetric
from devices.services.device_health import ONLINE_TIMEOUT

logger = logging.getLogger("django")


def get_latest_values(device_ids):
    if not device_ids:
        return {}

    # 1. Keys für Redis aufbauen
    cache_keys = {f"device:{d_id}:latest_power": d_id for d_id in device_ids}

    result = {}
    missing_ids = []

    # 2. Daten aus Redis laden
    try:
        cached_data = cache.get_many(cache_keys.keys())
        for key, d_id in cache_keys.items():
            if key in cached_data and cached_data[key] is not None:
                result[d_id] = float(cached_data[key])
            else:
                missing_ids.append(d_id)
    except Exception as e:
        logger.error(f"[REDIS_ERROR] Fehler beim Lesen aus dem Cache: {e}")
        missing_ids = list(device_ids)

    # 3. Fallback: Blitzschnelle 1-Query-Abfrage auf DeviceLatestMetric (O(1) Snapshot)
    if missing_ids:
        latest_rows = DeviceLatestMetric.objects.filter(
            device_id__in=missing_ids,
            metric_key__in=["power", "value"],
        ).values_list("device_id", "value")

        for d_id, val in latest_rows:
            if val is not None:
                float_val = float(val)
                result[d_id] = float_val
                try:
                    cache.set(f"device:{d_id}:latest_power", float_val, timeout=3600)
                except Exception:
                    pass

        for d_id in missing_ids:
            if d_id not in result:
                result[d_id] = 0.0

    return result


# def get_latest_powers(device_ids):

#     latest_metrics = (
#         DeviceMetric.objects
#         .filter(
#             device_id__in=device_ids,
#             metric_key="value",
#             device__last_seen__gt=(
#                 timezone.now() - ONLINE_TIMEOUT
#             ),
#         )
#         .order_by(
#             "device_id",
#             "-timestamp",
#         )
#         .distinct("device_id")
#     )

#     return {
#         metric.device_id: metric.value
#         for metric in latest_metrics
#     }
