######################
# providers/sungrow.py
######################

from datetime import timedelta
from django.utils import timezone
from devices.models import Device, DeviceMetric
from .base import BaseProvider


class SungrowProvider(BaseProvider):
    id = "sungrow"
    label = "Sungrow"
    category = "system"

    def fetch_signals(self, user):
        """
        Reads latest Sungrow-related metrics from DeviceMetric.

        Assumption:
        - Sungrow devices are stored as Device(device_type="pv" / "battery")
        - Metrics come via MQTT into DeviceMetric
        """

        since = timezone.now() - timedelta(minutes=5)

        devices = Device.objects.filter(
            owner_user=user,
            device_type__in=["pv", "battery"]
        )

        metrics = DeviceMetric.objects.filter(
            device__in=devices,
            ts__gte=since
        )

        def get_latest(metric_name):
            m = metrics.filter(metric_key=metric_name).order_by("-ts").first()
            return float(m.value) if m else None

        return {
            "grid": {
                "import": get_latest("grid_import_w"),
                "export": get_latest("grid_export_w"),
            },
            "load": {
                "consumption": get_latest("load_power_w"),
            },
            "pv": {
                "production": get_latest("pv_energy_wh"),
                "power": get_latest("pv_power_w"),
            },
            "battery": {
                "charge": get_latest("battery_charge_w"),
                "discharge": get_latest("battery_discharge_w"),
                "soc": get_latest("battery_soc"),
            },
        }
    
