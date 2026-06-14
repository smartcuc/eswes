########################
# providers/api/views.py
########################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .providers.aggregator import aggregate_signals
from .providers.flow_engine import calculate_energy_flow


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_me(request):
    user = request.user

    # ✅ Schritt 1: Signale sammeln
    signals = aggregate_signals(user)

    # ✅ OPTIONAL: MQTT/Device Testdaten injizieren
    # Beispiel: +2.5 kW zusätzlicher Verbrauch (z.B. TV)
    # Kannst du später entfernen
    load = signals.setdefault("load", {})
    load["consumption"] = (load.get("consumption") or 0) + 2.5

    # ✅ Schritt 2: Flüsse berechnen
    flow = calculate_energy_flow(signals)

    return Response({
        "signals": signals,
        "flow": flow,
    })

