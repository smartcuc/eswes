###########################
# energy/services/energy.py
###########################

from devices.models import Device

from energy.services.signals import get_ems_signals
from energy.flow_engine import calculate_energy_flow
from energy.services.sankey import build_live_sankey


def get_energy_data(user):

    
    return {
            "test": "ICH BIN ENERGY.PY"
        }
