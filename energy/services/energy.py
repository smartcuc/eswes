###########################
# energy/services/energy.py
###########################

from devices.models import Device

from energy.services.signals import get_ems_signals
from energy.flow_engine import calculate_energy_flow
from energy.services.sankey import build_live_sankey
from user_settings.models import UserPreference

def get_energy_data(user):

    preference, _ = UserPreference.objects.get_or_create(
        user=user,
        key="sankey",
    )

    settings = preference.value or {}

    show_floors = settings.get(
        "showFloors",
        True,
    )

    show_rooms = settings.get(
        "showRooms",
        True,
    )

    signals = get_ems_signals(user)

    flow = calculate_energy_flow(signals)

    sankey = build_live_sankey(
        user,
        flow,
        signals,
        show_floors=show_floors,
        show_rooms=show_rooms,
    )

    return {
        "sankey": sankey,
    }

