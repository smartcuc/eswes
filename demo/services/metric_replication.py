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

    try:

        mapping = DemoDeviceMap.objects.filter(source_device=metric.device).first()

        if not mapping:
            logger.warning(
                "No demo mapping found for device %s",
                metric.device_id,
            )
            return None

        demo_device = mapping.demo_device

        exists = DeviceMetric.objects.filter(
            device=demo_device,
            metric_key=metric.metric_key,
            timestamp=metric.timestamp,
        ).exists()

        if exists:
            return None

        return DeviceMetric.objects.create(
            device=demo_device,
            metric_key=metric.metric_key,
            unit=metric.unit,
            value=metric.value,
            data=metric.data,
            timestamp=metric.timestamp,
        )

    except Exception:
        logger.exception(
            "Metric replication failed for metric %s",
            getattr(metric, "id", "unknown"),
        )
        return None


def replicate_recent_metrics(limit=100):
    """
    Replicate the most recent metrics.
    Useful for testing before introducing
    a scheduler/celery task.
    """

    metrics = DeviceMetric.objects.select_related("device").order_by("-timestamp")[
        :limit
    ]

    replicated = 0

    for metric in metrics:
        if replicate_metric(metric):
            replicated += 1

    logger.info(
        "Replicated %s metrics",
        replicated,
    )

    return replicated


def sync_new_metrics():
    """
    Replicate only new metrics since the last run.
    """

    source_ids = list(
        DemoDeviceMap.objects.values_list(
            "source_device_id",
            flat=True,
        )
    )

    if not source_ids:
        return 0

    last_metric_id = cache.get(
        SYNC_CACHE_KEY,
        0,
    )

    metrics = (
        DeviceMetric.objects.select_related("device")
        .filter(
            device_id__in=source_ids,
            id__gt=last_metric_id,
        )
        .order_by("id")
    )

    replicated = 0
    highest_id = last_metric_id

    for metric in metrics:

        if metric.id > highest_id:
            highest_id = metric.id

        if replicate_metric(metric):
            replicated += 1

    if highest_id > last_metric_id:
        cache.set(
            SYNC_CACHE_KEY,
            highest_id,
            None,
        )

    logger.info(
        "Replicated %s metrics",
        replicated,
    )

    return replicated

