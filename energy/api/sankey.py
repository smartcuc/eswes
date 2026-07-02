###########################
# energy/services/sankey.py
###########################

from devices.models import Device


def build_live_sankey(user):

    devices = (
        Device.objects
        .filter(
            home__user=user,
            configured=True,
            active=True,
            pending_delete=False,
        )
        .select_related(
            "config",
            "config__role",
            "config__floor",
            "config__room",
        )
    )

    return {
        "nodes": [],
        "links": [],
        "device_count": devices.count(),
    }
