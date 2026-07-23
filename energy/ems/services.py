########################
# energy/ems/services.py
########################

from devices.models import Device
from devices.services.metrics import get_latest_values
from energy.models import EMSSignalSource


def build_device_signals(user):
    signals = {
        "grid": {"import": 0, "export": 0},
        "load": {"consumption": None},
        "pv": {"production": 0},
        "battery": {"charge": None, "discharge": None},
    }

    # 1. Holt alle Geräte UND lädt die Konfiguration sowie die Rolle direkt mit (1 Query)
    all_devices = list(
        Device.objects.filter(
            home__user=user,
            active=True,
            pending_delete=False,
        ).select_related("config__role")
    )

    values = get_latest_values([device.id for device in all_devices])

    # 2. PV und Grid Signalquellen einsammeln
    sources = EMSSignalSource.objects.filter(
        home__user=user,
        signal_type__in=["pv", "grid"]
    )

    pv_sources = [src for src in sources if src.signal_type == "pv"]
    grid_sources = [src for src in sources if src.signal_type == "grid"]

    # PV
    pv_power = sum(max(values.get(src.device_id, 0), 0) for src in pv_sources)
    signals["pv"]["production"] = pv_power

    # GRID
    grid_power = sum(values.get(src.device_id, 0) for src in grid_sources)
    if grid_power >= 0:
        signals["grid"]["import"] = grid_power
        signals["grid"]["export"] = 0
    else:
        signals["grid"]["import"] = 0
        signals["grid"]["export"] = abs(grid_power)

    #
    # BATTERY (KORRIGIERT FÜR RELATIONALE MODELLE)
    #
    battery_power = sum(
        values.get(device.id, 0)
        for device in all_devices
        if (config := getattr(device, "config", None)) is not None
        and (role := getattr(config, "role", None)) is not None
        and role.key == "battery"
    )

    if battery_power >= 0:
        signals["battery"]["discharge"] = battery_power
        signals["battery"]["charge"] = 0
    else:
        signals["battery"]["discharge"] = 0
        signals["battery"]["charge"] = abs(battery_power)

    # LOAD
    consumption = (
        signals["pv"]["production"]
        + signals["battery"]["discharge"]
        + signals["grid"]["import"]
        - signals["battery"]["charge"]
        - signals["grid"]["export"]
    )
    signals["load"]["consumption"] = max(consumption, 0)

    return signals
