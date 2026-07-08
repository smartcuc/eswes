###########################
# energy/services/energy.py
###########################

from energy.services.signals import get_ems_signals
from energy.flow_engine import calculate_energy_flow
from energy.services.sankey import build_live_sankey
from user_settings.models import UserPreference
from devices.models import DeviceConfig

from energy.services.kpis import ( get_today_consumption, )


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

    has_producer = DeviceConfig.objects.filter(
        device__home__user=user,
        role__key="producer",
    ).exists()

    has_consumer = DeviceConfig.objects.filter(
        device__home__user=user,
        role__key="consumer",
    ).exists()

    load = signals.get("load", {})
    pv = signals.get("pv", {})
    grid = signals.get("grid", {})

    today = get_today_consumption(user)

    kpis = {
        "load": load.get("consumption", 0),
        "pv": pv.get("production", 0),
        "grid": (
            grid.get("import", 0)
            - grid.get("export", 0)
        ),

        "today": (
            today["value"]
            if today
            else 0
        ),

        # Nur für Test und Debug - 
        "today_source": (
            today["source"]
            if today
            else None
        ),
    }

    return {
        "ready": has_producer and has_consumer,
        "sankey": sankey,
        "kpis": kpis,
    }

