#############################
# devices/services/metrics.py
#############################

from django.utils import timezone

from devices.models import DeviceMetric
from devices.services.device_health import ONLINE_TIMEOUT

from django.core.cache import cache

def get_latest_powers(device_ids):
    # Generiere einheitliche Cache-Keys für die Geräte
    cache_keys = [f"device:{d_id}:latest_power" for d_id in device_ids]
    
    # Holt alle Werte gleichzeitig aus Redis (< 1ms)
    cached_data = cache.get_many(cache_keys)
    
    # Rückgabe-Dictionary im exakt gleichen Format {device_id: value} aufbauen
    result = {}
    for key, value in cached_data.items():
        try:
            # Extrahiere die ID aus dem Key 'device:{id}:latest_power'
            device_id = int(key.split(":")[1])
            result[device_id] = value
        except (ValueError, IndexError):
            continue
            
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
