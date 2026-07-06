#############################
# devices/services/metrics.py
#############################

from django.utils import timezone

from devices.models import DeviceMetric
from devices.services.device_health import ONLINE_TIMEOUT


def get_latest_powers(device_ids):

    latest_metrics = (
        DeviceMetric.objects
        .filter(
            device_id__in=device_ids,
            metric_key="value",
            device__last_seen__gt=(
                timezone.now() - ONLINE_TIMEOUT
            ),
        )
        .order_by(
            "device_id",
            "-timestamp",
        )
        .distinct("device_id")
    )

    return {
        metric.device_id: metric.value
        for metric in latest_metrics
    }
