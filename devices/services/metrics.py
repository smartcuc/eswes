#############################
# devices/services/metrics.py
#############################

from django.utils import timezone

from devices.models import DeviceMetric
from devices.services.device_health import ONLINE_TIMEOUT

# devices/services/metrics.py
import logging
from django.core.cache import cache
from django.utils import timezone
from devices.models import DeviceMetric

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

    # 3. Fallback: Nur wenn Redis leer ist, direkt das Neueste aus der DB holen
    if missing_ids:
        logger.warning(f"[CACHE_MISS] Hole {len(missing_ids)} Geräte aus der SQL-DB")
        for d_id in missing_ids:
            # Schnelle Einzelabfrage pro fehlendem Gerät verhindert die PostgreSQL Distinct-Falle
            last_metric = (
                DeviceMetric.objects
                .filter(device_id=d_id, metric_key="value")
                .order_by("-timestamp")
                .first()
            )
            if last_metric:
                val = float(last_metric.value)
                result[d_id] = val
                # Direkt für das nächste Mal im Cache sichern
                try:
                    cache.set(f"device:{d_id}:latest_power", val, timeout=3600)
                except Exception:
                    pass
            else:
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
