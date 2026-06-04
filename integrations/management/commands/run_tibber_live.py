#####################################################
# integrations/management/commands/run_tibber_live.py
#####################################################

from django.core.management.base import BaseCommand
import asyncio

from metering.models import Meter
from integrations.live_engine import run_live_engine


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        meters = list(
            Meter.objects.select_related("owner_user").filter(
                data_resolution="quarter_hourly"
            )
        )

        asyncio.run(run_live_engine(meters))
