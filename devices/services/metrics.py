#############################
# devices/services/metrics.py
#############################

from devices.models import DeviceMetric


def get_latest_powers(device_ids):

    latest_metrics = (
        DeviceMetric.objects
        .filter(
            device_id__in=device_ids,
            metric_key="value",
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
