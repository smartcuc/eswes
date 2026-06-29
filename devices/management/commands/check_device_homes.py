###################################################
# devices/management/commands/check_device_homes.py
###################################################

from django.core.management.base import BaseCommand
from devices.models import DeviceConfig


class Command(BaseCommand):
    help = "Check for inconsistent home assignments"

    def handle(self, *args, **options):

        mismatches = 0

        for config in DeviceConfig.objects.all():

            if not config.room or not config.room.floor:
                continue

            expected_home = config.room.floor.home

            if not expected_home:
                continue

            if config.home != expected_home:
                mismatches += 1
                self.stdout.write(
                    f"❌ Config {config.id}: home mismatch "
                    f"(config={config.home_id}, expected={expected_home.id})"
                )

        self.stdout.write("------------------------------------------")
        self.stdout.write(f"Gefundene Inkonsistenzen: {mismatches}")
