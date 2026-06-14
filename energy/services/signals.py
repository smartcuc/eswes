############################
# energy/services/signals.py
############################

from providers.aggregator import aggregate_signals


def pick(primary, fallback):
    return primary if primary is not None else fallback


def get_ems_signals(user):
    device = aggregate_signals(user, category="device")
    system = aggregate_signals(user, category="system")

    return {
        "pv": {
            "production": pick(
                device["pv"].get("production"),
                system["pv"].get("production"),
            ),
        },
        "load": {
            "consumption": pick(
                device["load"].get("consumption"),
                system["load"].get("consumption"),
            ),
        },
        "battery": {
            "charge": pick(
                device["battery"].get("charge"),
                system["battery"].get("charge"),
            ),
            "discharge": pick(
                device["battery"].get("discharge"),
                system["battery"].get("discharge"),
            ),
        },
        "grid": {
            "import": pick(
                device["grid"].get("import"),
                system["grid"].get("import"),
            ),
            "export": pick(
                device["grid"].get("export"),
                system["grid"].get("export"),
            ),
        },
    }

