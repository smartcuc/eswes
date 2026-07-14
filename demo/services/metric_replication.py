#####################################
# demo/services/metric_replication.py
#####################################

from django.contrib.auth import get_user_model

from devices.models import (
    Device,
    DeviceMetric,
)

User = get_user_model()

MASTER_EMAIL = "ruediger.koenen@web.de"
DEMO_EMAIL = "demo@sharegy.de"


def replicate_metric(metric):

    try:

        source_device = metric.device

        demo_user = User.objects.get(email=DEMO_EMAIL)

        demo_home = demo_user.homes.first()

        if not demo_home:
            return

        demo_device = Device.objects.filter(
            home=demo_home,
            identifier=source_device.identifier,
        ).first()

        if not demo_device:
            return

        DeviceMetric.objects.create(
            device=demo_device,
            metric_key=metric.metric_key,
            unit=metric.unit,
            value=metric.value,
            data=metric.data,
            timestamp=metric.timestamp,
        )

    except Exception:
        pass
