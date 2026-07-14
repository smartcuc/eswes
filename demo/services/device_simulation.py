####################################
# demo/services/device_simulation.py
####################################

from datetime import timedelta
from django.utils import timezone
from demo.models import DemoDeviceSimulation


def hide_device(device, hours=4):

    simulation, _ = DemoDeviceSimulation.objects.get_or_create(
        device=device,
    )

    simulation.hidden_until = timezone.now() + timedelta(hours=hours)

    simulation.save()

    return simulation
