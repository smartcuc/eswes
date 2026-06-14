######################
# providers/device.py
######################

from providers.base import BaseProvider
from devices.models import DeviceMetric


class DeviceProvider(BaseProvider):
    id = "devices"
    label = "Device MQTT"
    category = "device"

    def fetch_signals(self, user):
        metrics = (
            DeviceMetric.objects
            .select_related("device")
            .filter(device__user=user)
            .order_by("-created_at")
        )

        signals = {
            "pv": {"production": None},
            "load": {"consumption": None},
            "battery": {"charge": None, "discharge": None},
            "grid": {"import": None, "export": None},
        }

        seen_roles = set()

        for m in metrics:
            device = m.device
            role = device.role

            # ❗ nur konfigurierte Geräte
            if not device.configured:
                continue

            if not role or role in seen_roles:
                continue

            power = m.data.get("power")
            if power is None:
                continue

            if role == "pv":
                signals["pv"]["production"] = power

            elif role == "load":
                signals["load"]["consumption"] = power

            elif role == "battery":
                if power >= 0:
                    signals["battery"]["charge"] = power
                else:
                    signals["battery"]["discharge"] = abs(power)

            elif role == "grid":
                if power >= 0:
                    signals["grid"]["import"] = power
                else:
                    signals["grid"]["export"] = abs(power)

            seen_roles.add(role)

        return signals
    