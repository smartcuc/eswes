########################
# energy/ems/services.py
########################

from devices.models import DeviceMetric, Device
from energy.models import EMSSignalSource


def get_latest_power(device):

    metric = (
        DeviceMetric.objects
        .filter(
            device=device,
            metric_key="value",
        )
        .order_by("-timestamp")
        .first()
    )

    return metric.value if metric else 0


def get_latest_powers(device_ids):

    latest_metrics = (
        DeviceMetric.objects
        .filter(
            device_id__in=device_ids,
            metric_key="value",
        )
        .order_by(
            "device_id",
            "-timestamp",
        )
        .distinct("device_id")
    )

    return {
        metric.device_id: metric.value
        for metric in latest_metrics
    }


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
            get_latest_power(src.device),
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
        get_latest_power(src.device)
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
        get_latest_power(device)
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

