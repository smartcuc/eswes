############################
# integrations/views_live.py
############################

from rest_framework.decorators import api_view
from rest_framework.response import Response

from integrations.live_state import LIVE_STATE


@api_view(["GET"])
def live_data(request):
    """
    Unified Live API:

    - Devices (MQTT, Sungrow etc.) → user scope
    - Meter (iMSys, Tibber) → tenant scope + user visibility

    Rückgabe:
    {
        "devices": [],
        "meters": []
    }
    """

    user = request.user
    is_authenticated = user and user.is_authenticated

    devices = []
    meters = []

    for key, value in LIVE_STATE.items():

        if not isinstance(value, dict):
            continue

        entry_type = value.get("type")

        # -------------------------
        # DEVICE (User-EMS)
        # -------------------------
        if entry_type == "device":
            if not is_authenticated:
                continue

            if value.get("user_id") != user.id:
                continue

            devices.append({
                "id": key,
                "power": value.get("power"),
                "energy": value.get("energy"),
                "timestamp": value.get("timestamp"),
            })

        # -------------------------
        # METER (Tenant / EMS)
        # -------------------------
        elif entry_type == "meter":

            # User-Zugriff (EMS Sicht)
            if is_authenticated and value.get("user_id") == user.id:
                meters.append({
                    "id": key,
                    "power": value.get("power"),
                    "energy": value.get("energy"),
                    "timestamp": value.get("timestamp"),
                })
                continue

            # Optional: Tenant-Zugriff (Admin / später)
            # if request.user.is_staff and value.get("tenant_id") == request.tenant.id:
            #     meters.append(...)

            continue

    return Response({
        "devices": devices,
        "meters": meters,
    })
