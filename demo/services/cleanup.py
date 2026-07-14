##########################
# demo/services/cleanup.py
##########################

from datetime import timedelta
from django.utils import timezone
from demo.models import DemoDeviceMap
from devices.models import DeviceMetric


def cleanup_demo_metrics(days=28):

    cutoff = timezone.now() - timedelta(days=days)

    demo_ids = DemoDeviceMap.objects.values_list(
        "demo_device_id",
        flat=True,
    )

    deleted, _ = DeviceMetric.objects.filter(
        device_id__in=demo_ids,
        timestamp__lt=cutoff,
    ).delete()

    return deleted
