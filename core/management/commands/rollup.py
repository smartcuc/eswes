########################################
# core/management/commands/rollup.py
########################################

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Run core rollup + balance pipeline"

    def handle(self, *args, **opts):

        with connection.cursor() as cur:

            # ✅ 1. Aggregation
            cur.execute("SELECT rollup_15min();")

            # ✅ 2. Balance computation
            cur.execute("SELECT process_dirty_balance();")

        self.stdout.write(
            self.style.SUCCESS("✅ Rollup + balance pipeline executed")
        )
        