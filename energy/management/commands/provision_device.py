################################################
# energy/management/commands/provision_device.py
################################################


from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from energy.models import Device

User = get_user_model()


class Command(BaseCommand):
    help = "Provision a device for MQTT ingestion."

    def add_arguments(self, parser):
        parser.add_argument(
            "--type", required=True, help="device_type (meter/pv/battery/ev/shelly/...)"
        )
        parser.add_argument("--id", required=True, help="device_id (topic segment)")
        parser.add_argument(
            "--user", required=False, help="owner username (standalone)"
        )
        parser.add_argument(
            "--controllable", action="store_true", help="mark device controllable"
        )

    def handle(self, *args, **opts):
        device_type = opts["type"]
        device_id = opts["id"]
        username = opts.get("user")
        controllable = opts.get("controllable", False)

        owner_user = None
        if username:
            owner_user = User.objects.get(username=username)

        device, created = Device.objects.get_or_create(
            device_type=device_type,
            name=device_id,
            defaults={
                "owner_user": owner_user,
                "controllable": controllable,
            },
        )
        if not created:
            if owner_user and device.owner_user_id != owner_user.id:
                device.owner_user = owner_user
                device.save(update_fields=["owner_user"])
        self.stdout.write(
            self.style.SUCCESS(f"Provisioned: {device.device_type}/{device.name}")
        )
