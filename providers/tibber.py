#####################
# providers/tibber.py
#####################

from .base import BaseProvider


def get_tibber_data(user):
    # TODO: echte Tibber API Integration
    return {
        "consumption_kwh": 12.4,
        "grid_import_kwh": 8.2,
        "grid_export_kwh": 4.2,
    }


class TibberProvider(BaseProvider):
    id = "tibber"
    label = "Tibber"
    category = "system"  # NICHT abrechnungsfähig!

    def fetch_signals(self, user):
        raw = get_tibber_data(user)

        return {
            "grid": {
                "import": raw.get("grid_import_kwh"),
                "export": raw.get("grid_export_kwh"),
            },
            "load": {
                "consumption": raw.get("consumption_kwh"),
            },
            "pv": {},
            "battery": {},
        }
    