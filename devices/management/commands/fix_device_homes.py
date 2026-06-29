################################################
#devices/management/commands/fix_device_homes.py
################################################

from django.core.management.base import BaseCommand
from devices.models import DeviceConfig


class Command(BaseCommand):
    help = "Fix missing home on DeviceConfig"

    def handle(self, *args, **options):

        fixed = 0
        skipped = 0

        configs = DeviceConfig.objects.filter(home__isnull=True)

        self.stdout.write(f"🔧 Finde {configs.count()} Configs ohne Home...")

        for config in configs:

            home = None

            # ✅ 1. über room → floor → home
            if config.room and config.room.floor and config.room.floor.home:
                home = config.room.floor.home

            # ✅ 2. fallback über floor
            elif config.floor and config.floor.home:
                home = config.floor.home

            # ✅ 3. fallback über user (default home)
            elif config.device and config.device.home:
                home = config.device.home

            # ✅ anwenden
            if home:
                config.home = home
                config.save(update_fields=["home"])
                fixed += 1
            else:
                skipped += 1
                self.stdout.write(
                    f"⚠️ Kein Home ableitbar für Config {config.id}"
                )

        self.stdout.write("--------------------------------------------------")
        self.stdout.write(f"✅ Gefixt: {fixed}")
        self.stdout.write(f"⚠️ Übersprungen: {skipped}")

