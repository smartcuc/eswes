#####################################
# demo/services/metric_replication.py
#####################################

import logging

from devices.models import DeviceMetric
from demo.models import DemoDeviceMap

logger = logging.getLogger(__name__)


def sync_latest_metrics():
    """
    Synchronisiert genau die aktuellste Metric
    jedes Quellgerätes auf das Demo-Gerät.
    """

    mappings = {
        m.source_device_id: m.demo_device_id
        for m in DemoDeviceMap.objects.all()
    }

    if not mappings:
        logger.info("Keine Demo-Mappings gefunden.")
        return 0

    replicated = 0

    for source_device_id, demo_device_id in mappings.items():

        latest_metric = (
            DeviceMetric.objects
            .filter(device_id=source_device_id)
            .order_by("-timestamp")
            .first()
        )

        if not latest_metric:
            continue

        DeviceMetric.objects.filter(
            device_id=demo_device_id
        ).delete()

        DeviceMetric.objects.create(
            device_id=demo_device_id,
            metric_key=latest_metric.metric_key,
            unit=latest_metric.unit,
            value=latest_metric.value,
            data=latest_metric.data,
            timestamp=latest_metric.timestamp,
        )

        replicated += 1

    logger.info(
        "Synced latest metrics for %s devices",
        replicated,
    )

    return replicated
