##########################################
# metering/management/commands/seed_dev.py
##########################################

from datetime import datetime, timezone as tz
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection, transaction

from metering.models import Meter, IntervalReading

User = get_user_model()


class Command(BaseCommand):
    help = "Seed dev data (user, meter, readings) and run rollup + balance."

    def handle(self, *args, **options):
        with transaction.atomic():
            # 1) User anlegen (ORM => alle Defaults/Constraints sauber)
            user, created = User.objects.get_or_create(
                username="testuser",
                defaults={
                    "email": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "is_active": True,
                    "is_verified": False,
                },
            )
            if created:
                user.set_password("testpass123")
                user.save()

            # 2) Standalone Meter (Owner-Pattern)
            meter, _ = Meter.objects.get_or_create(
                serial_number="TEST-METER-001",
                defaults={
                    "owner_user": user,
                    "owner_member": None,
                    "tenant": None,
                    "meter_type": "electricity",
                    "manufacturer": "TestVendor",
                },
            )

            # 3) 15-min Slot Testdaten (Consumption + Generation)
            start = datetime(2026, 1, 1, 10, 0, tzinfo=tz.utc)
            end = datetime(2026, 1, 1, 10, 15, tzinfo=tz.utc)

            IntervalReading.objects.get_or_create(
                meter=meter,
                ts_start=start,
                obis_code="1.8.0",
                defaults={
                    "tenant": None,
                    "ts_end": end,
                    "value": 1.5,
                    "unit": "kWh",
                    "source": "seed",
                },
            )
            IntervalReading.objects.get_or_create(
                meter=meter,
                ts_start=start,
                obis_code="2.8.0",
                defaults={
                    "tenant": None,
                    "ts_end": end,
                    "value": 0.8,
                    "unit": "kWh",
                    "source": "seed",
                },
            )

        # 4) Stored Functions ausführen
        with connection.cursor() as cur:
            cur.execute("SELECT metering_rollup_15min();")
            cur.execute("SELECT metering_calculate_balanceslot();")

        self.stdout.write(
            self.style.SUCCESS(
                "Seed done ✅  User=testuser/testpass123  Meter=TEST-METER-001  Rollup+Balance executed"
            )
        )
