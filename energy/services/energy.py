###########################
# energy/services/energy.py
###########################

from devices.models import Device

from energy.services.signals import get_ems_signals
from energy.flow_engine import calculate_energy_flow
from energy.services.sankey import build_live_sankey

def get_energy_data(user):

    signals = get_ems_signals(user)

    flow = calculate_energy_flow(signals)

    sankey = build_live_sankey(user, flow)

    return {
        "sankey": sankey,
    }
