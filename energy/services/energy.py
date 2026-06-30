###########################
# energy/services/energy.py
###########################

from devices.models import Device
from energy.services.signals import get_ems_signals
from energy.flow_engine import calculate_energy_flow


def get_energy_data(user):
    signals = get_ems_signals(user)
    flow = calculate_energy_flow(signals)

    
    unconfigured = Device.objects.filter(
        home__user=user,
        configured=False,
        active=True,
        pending_delete=False,
    )

    return {
    "signals": signals,
    "flow": flow,
    "devices": {
        "unconfigured": [
            {
                "id": d.id,
                "identifier": d.identifier,
                "name": (
                    d.config.name
                    if hasattr(d, "config") and d.config.name
                    else d.identifier
                ),
            }
            for d in unconfigured
        ]
    }
}
