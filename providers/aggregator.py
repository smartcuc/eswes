#########################
# providers/aggregator.py
#########################

from .registry import PROVIDERS

from energy.ems.services import build_device_signals


def merge_dicts(base, new):
    for key, value in new.items():

        if isinstance(value, dict):
            base[key] = merge_dicts(base.get(key, {}), value)
        else:
            if value is not None:
                base[key] = (base.get(key) or 0) + value

    return base


def aggregate_signals(user, category="system"):

    if category == "device":
        return build_device_signals(user)

    return {
        "grid": {},
        "load": {},
        "pv": {},
        "battery": {},
    }

