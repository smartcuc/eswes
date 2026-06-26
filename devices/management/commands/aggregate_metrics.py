#
# management/commands/aggregate_metrics.py
#

from django.core.management.base import BaseCommand
from devices.services.aggregation import aggregate_1m, aggregate_5m


class Command(BaseCommand):
    help = "Run metric aggregation"

    def handle(self, *args, **kwargs):
        aggregate_1m()
        aggregate_5m()
        self.stdout.write(self.style.SUCCESS("Aggregation done"))


