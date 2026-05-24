from datetime import date
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.db import connection

PARENTS = [
    # parent_table, partition_prefix, partition_key_column
    ("metering_intervalreading", "metering_intervalreading", "ts_start"),
    (
        "sharing_allocationintervalresult",
        "sharing_allocationintervalresult",
        "ts_start",
    ),
]


def month_range(d: date):
    start = d.replace(day=1)
    end = start + relativedelta(months=1)
    return start, end


class Command(BaseCommand):
    help = "Create monthly PostgreSQL range partitions for time-series tables."

    def add_arguments(self, parser):
        parser.add_argument("--months-ahead", type=int, default=6)
        parser.add_argument("--months-back", type=int, default=0)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        if connection.vendor != "postgresql":
            self.stdout.write(
                self.style.WARNING("Not PostgreSQL. Skipping partitions.")
            )
            return

        months_ahead = opts["months_ahead"]
        months_back = opts["months_back"]
        dry_run = opts["dry_run"]

        today = date.today().replace(day=1)
        start_month = today - relativedelta(months=months_back)
        end_month = today + relativedelta(months=months_ahead)

        with connection.cursor() as cur:
            for parent, prefix, key in PARENTS:
                self.stdout.write(
                    self.style.MIGRATE_HEADING(f"Parent: {parent} (key: {key})")
                )

                # Sanity: check parent exists
                cur.execute("SELECT to_regclass(%s);", (parent,))
                reg = cur.fetchone()[0]
                if not reg:
                    self.stdout.write(
                        self.style.WARNING(f"  Table '{parent}' not found. Skipping.")
                    )
                    continue

                m = start_month
                while m <= end_month:
                    p_from, p_to = month_range(m)
                    part_name = f"{prefix}_{p_from.year}_{p_from.month:02d}"

                    sql = f"""
CREATE TABLE IF NOT EXISTS {part_name}
PARTITION OF {parent}
FOR VALUES FROM (%s) TO (%s);
"""
                    if dry_run:
                        self.stdout.write(f"DRY-RUN: {part_name} {p_from} -> {p_to}")
                    else:
                        cur.execute(sql, (p_from.isoformat(), p_to.isoformat()))
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  OK: {part_name} ({p_from} -> {p_to})"
                            )
                        )

                    m = m + relativedelta(months=1)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Dry-run completed. No changes applied.")
            )
        else:
            self.stdout.write(self.style.SUCCESS("Partition creation completed."))
