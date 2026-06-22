###################################################
# devices/management/commands/mqtt_ingest_health.py
###################################################

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from core.management.commands.mqtt_consume import LAST_MESSAGE_TS


class Command(BaseCommand):
    help = "Check MQTT ingest health"

    def handle(self, *args, **options):

        if not LAST_MESSAGE_TS:
            self.stdout.write("❌ No MQTT messages received yet")
            return

        if LAST_MESSAGE_TS < timezone.now() - timedelta(minutes=2):
            self.stdout.write("❌ MQTT ingest stalled")
        else:
            self.stdout.write("✅ MQTT ingest healthy")
