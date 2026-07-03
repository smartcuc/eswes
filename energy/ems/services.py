########################
# energy/ems/services.py
########################

from devices.models import DeviceMetric
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

    return signals
