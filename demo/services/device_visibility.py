####################################
# demo/services/device_visibility.py
####################################

from django.utils import timezone


def is_demo_device_visible(device):

    simulation = getattr(
        device,
        "demodevicesimulation",
        None,
    )

    if not simulation:
        return True

    if not simulation.hidden_until:
        return True

    return simulation.hidden_until <= timezone.now()
