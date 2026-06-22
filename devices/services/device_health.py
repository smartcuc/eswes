###################################
# devices/services/device_health.py
###################################

from django.utils import timezone
from datetime import timedelta


def device_is_online(device, timeout_seconds=120):
    if not device.last_seen:
        return False

    return device.last_seen > timezone.now() - timedelta(seconds=timeout_seconds)


def device_status(device):
    if not device.last_seen:
        return "never_seen"

    now = timezone.now()

    if device.last_seen > now - timedelta(minutes=2):
        return "online"

    if device.last_seen > now - timedelta(minutes=10):
        return "offline"

    return "stale"
