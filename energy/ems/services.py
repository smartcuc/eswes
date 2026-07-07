########################
# energy/ems/services.py
########################

from devices.models import Device
from devices.services.metrics import get_latest_powers
from energy.models import EMSSignalSource


def build_device_signals(user):

    signals = {
        "grid": {
            "import": 0,
            "export": 0,
        },
        "load": {
            "consumption": None,
        },
        "pv": {
            "production": 0,
        },
        "battery": {
            "charge": None,
            "discharge": None,
        },
    }


    all_devices = list(
        Device.objects.filter(
            home__user=user,
            active=True,
            pending_delete=False,
        )
    )

    powers = get_latest_powers(
        [device.id for device in all_devices]
    )

    #
    # PV
    #

    pv_sources = (
        EMSSignalSource.objects
        .filter(
            home__user=user,
            signal_type="pv",
        )
        .select_related("device")
    )

    pv_power = sum(
        max(
            powers.get(src.device_id, 0),
            0,
        )
        for src in pv_sources
    )

    signals["pv"]["production"] = pv_power

    #
    # GRID
    #

    grid_sources = (
        EMSSignalSource.objects
        .filter(
            home__user=user,
            signal_type="grid",
        )
        .select_related("device")
    )

    
    grid_power = sum(
        powers.get(src.device_id, 0)
        for src in grid_sources
    )


    if grid_power >= 0:

        signals["grid"]["import"] = grid_power
        signals["grid"]["export"] = 0

    else:

        signals["grid"]["import"] = 0
        signals["grid"]["export"] = abs(grid_power)


    #
    # BATTERY
    #

    battery_devices = (
        Device.objects
        .filter(
            home__user=user,
            active=True,
            pending_delete=False,
            config__role__key="battery",
        )
    )

    battery_power = sum(
        powers.get(device.id, 0)
        for device in battery_devices
    )

    if battery_power >= 0:

        signals["battery"]["discharge"] = battery_power
        signals["battery"]["charge"] = 0

    else:

        signals["battery"]["discharge"] = 0
        signals["battery"]["charge"] = abs(battery_power)


    #
    # LOAD
    #

    consumption = (
        signals["pv"]["production"]
        + signals["battery"]["discharge"]
        + signals["grid"]["import"]
        - signals["battery"]["charge"]
        - signals["grid"]["export"]
    )

    signals["load"]["consumption"] = max(
        consumption,
        0,
    )

    return signals

