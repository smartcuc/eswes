##################################################
# devices/management/commands/seed_device_setup.py
##################################################

from django.core.management.base import BaseCommand
from devices.models import DeviceRole, MetricDefinition


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        roles = {
            "consumer": "Verbraucher",
            "producer": "Erzeuger",
            "both": "Beides"
        }

        for key, label in roles.items():
            DeviceRole.objects.get_or_create(
                key=key,
                defaults={"label": label}
            )

        metrics = {
            "power": ("Leistung", "W"),
            "energy": ("Energie", "kWh"),
            "temperature": ("Temperatur", "°C"),
            "soc": ("Ladezustand", "%"),
        }

        for key, (name, unit) in metrics.items():
            MetricDefinition.objects.get_or_create(
                key=key,
                defaults={"name": name, "unit": unit}
            )