###################################
# devices/services/device_health.py
###################################

from django.utils import timezone
from datetime import timedelta


ONLINE_TIMEOUT = timedelta(minutes=2)
OFFLINE_TIMEOUT = timedelta(minutes=10)


def device_is_online(device):
    if not device.last_seen:
        return False

    return device.last_seen > (
        timezone.now() - ONLINE_TIMEOUT
    )


def device_status(device):

    if not device.last_seen:
        return "never_seen"

    now = timezone.now()
    age = now - device.last_seen

    if age <= ONLINE_TIMEOUT:
        return "online"

    if age <= OFFLINE_TIMEOUT:
        return "offline"

    return "stale"

