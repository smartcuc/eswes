###########################
# energy/services/energy.py
###########################

from devices.models import Device
from energy.services.signals import get_ems_signals
from energy.flow_engine import calculate_energy_flow


def get_energy_data(user):
    signals = get_ems_signals(user)
    flow = calculate_energy_flow(signals)

    unconfigured = Device.objects.filter(user=user, configured=False)

    return {
        "signals": signals,
        "flow": flow,
        "devices": {
            "unconfigured": [
                {
                    "id": d.id,
                    "identifier": d.identifier,
                    "name": d.name,
                }
                for d in unconfigured
            ]
        }
    }
