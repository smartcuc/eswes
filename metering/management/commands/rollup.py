########################################
# metering/management/commands/rollup.py
########################################


from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "Run Timescale rollups into metering_aggregatedreading"

    def add_arguments(self, parser):
        parser.add_argument("--hours", type=int, default=48)

    def handle(self, *args, **opts):
        hours = opts["hours"]
        end = timezone.now()
        start = end - timedelta(hours=hours)

        with connection.cursor() as cur:
            cur.execute("CALL metering_rollup_window(%s, %s);", [start, end])

        self.stdout.write(self.style.SUCCESS(f"Rollup done for last {hours} hours"))
