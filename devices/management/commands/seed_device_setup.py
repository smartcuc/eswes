##################################################
# devices/management/commands/seed_device_setup.py
##################################################
""" 
from django.core.management.base import BaseCommand
from devices.models import (
    DeviceRole,
    MetricDefinition,
    DeviceType,
    DeviceTypeMetric
)


class Command(BaseCommand):
    help = "Seed device setup data (roles, metrics, device types)"

    def handle(self, *args, **kwargs):

        # =====================================================
        # ✅ ROLES (für Sankey!)
        # =====================================================
        roles = {
            "consumer": "Verbraucher",
            "producer": "Erzeuger",
            "both": "Beides"
        }

        role_objs = {}
        for key, label in roles.items():
            obj, _ = DeviceRole.objects.get_or_create(
                key=key,
                defaults={"label": label}
            )
            role_objs[key] = obj

        # =====================================================
        # ✅ METRICS
        # =====================================================
        metrics = {
            "power": ("Leistung", "W"),
            "energy": ("Energie", "kWh"),
            "temperature": ("Temperatur", "°C"),
            "soc": ("Ladezustand", "%"),
            "status": ("Status", "")
        }

        metric_objs = {}
        for key, (name, unit) in metrics.items():
            obj, _ = MetricDefinition.objects.get_or_create(
                key=key,
                defaults={
                    "name": name,
                    "unit": unit
                }
            )
            metric_objs[key] = obj

        # =====================================================
        # ✅ DEVICE TYPES
        # =====================================================
        device_types = [
            # key, name, role, metrics
            ("pv", "PV Anlage", "producer", ["power", "energy"]),
            ("battery", "Batterie", "both", ["power", "energy", "soc"]),
            ("heatpump", "Wärmepumpe", "consumer", ["power", "temperature"]),
            ("ev", "Elektroauto", "consumer", ["power", "energy", "soc"]),
            ("meter", "Zähler", "both", ["power", "energy"]),
            ("smart_plug", "Smart Plug", "consumer", ["power", "energy"]),
        ]

        for key, name, role_key, metric_keys in device_types:

            device_type, _ = DeviceType.objects.get_or_create(
                key=key,
                defaults={
                    "name": name,
                    "role": role_objs[role_key]
                }
            )

            # Metrics zuweisen
            for m_key in metric_keys:
                DeviceTypeMetric.objects.get_or_create(
                    device_type=device_type,
                    metric=metric_objs[m_key]
                )

        self.stdout.write(self.style.SUCCESS("✅ Device setup seeded"))
 """