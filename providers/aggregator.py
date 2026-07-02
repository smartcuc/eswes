#########################
# providers/aggregator.py
#########################

from .registry import PROVIDERS


def merge_dicts(base, new):
    for key, value in new.items():

        if isinstance(value, dict):
            base[key] = merge_dicts(base.get(key, {}), value)
        else:
            if value is not None:
                base[key] = (base.get(key) or 0) + value

    return base


def aggregate_signals(user, category="system"):
#    provider_ids = getattr(user.usersettings, "providers", [])

    result = {
        "grid": {},
        "load": {},
        "pv": {},
        "battery": {},
    }

    for pid in provider_ids:
        provider = PROVIDERS.get(pid)
        if not provider:
            continue

        if provider.category != category:
            continue

        data = provider.fetch_signals(user)
        result = merge_dicts(result, data)

    return result
