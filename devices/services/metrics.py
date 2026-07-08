#############################
# devices/services/metrics.py
#############################

from django.utils import timezone

from devices.models import DeviceMetric
from devices.services.device_health import ONLINE_TIMEOUT

# devices/services/metrics.py
from django.core.cache import cache
from devices.models import DeviceMetric

def get_latest_powers(device_ids):
    cache_keys = {f"device:{d_id}:latest_power": d_id for d_id in device_ids}
    cached_data = cache.get_many(cache_keys.keys())
    
    result = {}
    missing_ids = []
    
    for key, d_id in cache_keys.items():
        if key in cached_data and cached_data[key] is not None:
            result[d_id] = cached_data[key]
        else:
            missing_ids.append(d_id)
            
    # Falls der Cache für manche Geräte noch leer ist, hole die Werte einmalig aus der DB
    if missing_ids:
        latest_metrics = (
            DeviceMetric.objects
            .filter(device_id__in=missing_ids, metric_key="value")
            .order_by("device_id", "-timestamp")
            .distinct("device_id")
        )
        for metric in latest_metrics:
            result[metric.device_id] = metric.value
            cache.set(f"device:{metric.device_id}:latest_power", metric.value, timeout=3600)
            
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
