#####################################
# demo/services/metric_replication.py
#####################################

import logging

from devices.models import DeviceMetric
from demo.models import DemoDeviceMap

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
