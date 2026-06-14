##########################
# energy/api/views_fake.py
##########################

import random
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny



@api_view(["GET"])
@permission_classes([AllowAny])
def fake_dashboard(request):
    pv = random.uniform(0, 8000)
    load = random.uniform(1000, 5000)
    battery = random.uniform(-2000, 2000)

    pv_to_load = min(pv, load)
    pv_to_battery = max(0, pv - load)
    battery_to_load = max(0, -battery)
    grid_to_load = max(0, load - pv + battery_to_load)

    return Response({
        "signals": {
            "pv": {
                "production": round(pv, 2),
            },
            "load": {
                "consumption": round(load, 2),
            },
            "battery": {
                "charge": round(max(0, battery), 2),
                "discharge": round(max(0, -battery), 2),
            },
            "grid": {
                "import": round(grid_to_load, 2),
                "export": 0,
            },
        },
        "flow": {
            "pv_to_load": round(pv_to_load, 2),
            "pv_to_battery": round(pv_to_battery, 2),
            "battery_to_load": round(battery_to_load, 2),
            "grid_to_load": round(grid_to_load, 2),
        },
        "devices": {
            "unconfigured": []
        }
    })
