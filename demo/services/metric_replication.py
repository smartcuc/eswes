#####################################
# demo/services/metric_replication.py
#####################################

import logging

from devices.models import DeviceMetric
from demo.models import DemoDeviceMap

from django.core.cache import cache

SYNC_CACHE_KEY = "demo:last_metric_id"

logger = logging.getLogger(__name__)


def replicate_metric(metric):
    """
    Replicate a single metric from a master device
    to its demo clone using DemoDeviceMap.
    """
    return None
#     try:

#         mapping = DemoDeviceMap.objects.filter(source_device=metric.device).first()

#         if not mapping:
#             logger.warning(
#                 "No demo mapping found for device %s",
#                 metric.device_id,
#             )
#             return None

#         demo_device = mapping.demo_device

#         exists = DeviceMetric.objects.filter(
#             device=demo_device,
#             metric_key=metric.metric_key,
#             timestamp=metric.timestamp,
#         ).exists()

#         if exists:
#             return None

#         return DeviceMetric.objects.create(
#             device=demo_device,
#             metric_key=metric.metric_key,
#             unit=metric.unit,
#             value=metric.value,
#             data=metric.data,
#             timestamp=metric.timestamp,
#         )

#     except Exception:
#         logger.exception(
#             "Metric replication failed for metric %s",
#             getattr(metric, "id", "unknown"),
#         )
#         return None


# def replicate_recent_metrics(limit=100):
#     """
#     Replicate the most recent metrics.
#     Useful for testing before introducing
#     a scheduler/celery task.
#     """

#     metrics = DeviceMetric.objects.select_related("device").order_by("-timestamp")[
#         :limit
#     ]

#     replicated = 0

#     for metric in metrics:
#         if replicate_metric(metric):
#             replicated += 1

#     logger.info(
#         "Replicated %s metrics",
#         replicated,
#     )

#     return replicated


import logging
from devices.models import DeviceMetric
from demo.models import DemoDeviceMap
from django.core.cache import cache

SYNC_CACHE_KEY = "demo:last_metric_id"
logger = logging.getLogger(__name__)


def sync_new_metrics():
    """
    Repliziert neue Metriken blockweise (Bulk) ohne die DB oder den RAM zu blockieren.
    """
    # 1. Alle Mappings einmalig in den RAM laden
    mappings = {
        m.source_device_id: m.demo_device_id for m in DemoDeviceMap.objects.all()
    }

    if not mappings:
        logger.info("Keine Demo-Geräte-Mappings konfiguriert.")
        return 0

    source_ids = list(mappings.keys())
    last_metric_id = cache.get(SYNC_CACHE_KEY, 0)

    # 2. Neue Metriken holen - Streng limitiert auf 2.000 Stück pro Durchlauf
    new_metrics = list(
        DeviceMetric.objects.filter(
            device_id__in=source_ids, id__gt=last_metric_id
        ).order_by("id")[:2000]
    )

    if not new_metrics:
        return 0

    # ✅ KORREKTUR: Zeitstempel sicher aus dem ersten und letzten Element der Liste lesen
    min_ts = new_metrics[0].timestamp
    max_ts = new_metrics[-1].timestamp
    demo_device_ids = list(mappings.values())

    # 3. Existierende Einträge im Ziel-Zeitfenster ermitteln
    existing_pairs = set(
        DeviceMetric.objects.filter(
            device_id__in=demo_device_ids, timestamp__gte=min_ts, timestamp__lte=max_ts
        ).values_list("device_id", "metric_key", "timestamp")
    )

    # 4. Daten im RAM aufbereiten
    to_create = []
    highest_id = last_metric_id

    for metric in new_metrics:
        if metric.id > highest_id:
            highest_id = metric.id

        demo_device_id = mappings.get(metric.device_id)
        if not demo_device_id:
            continue

        # Dubletten-Check im Python-RAM (extrem schnell)
        check_key = (demo_device_id, metric.metric_key, metric.timestamp)
        if check_key in existing_pairs:
            continue

        to_create.append(
            DeviceMetric(
                device_id=demo_device_id,
                metric_key=metric.metric_key,
                unit=metric.unit,
                value=metric.value,
                data=metric.data,
                timestamp=metric.timestamp,
            )
        )

    # 5. Bulk-Insert
    replicated = 0
    if to_create:
        DeviceMetric.objects.bulk_create(to_create, batch_size=1000)
        replicated = len(to_create)

    # Cache aktualisieren
    if highest_id > last_metric_id:
        cache.set(SYNC_CACHE_KEY, highest_id, None)

    logger.info(
        "Erfolgreich %s Metriken per Bulk repliziert. (Höchste ID: %s)",
        replicated,
        highest_id,
    )
    return replicated
