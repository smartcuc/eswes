###################
# metering/tasks.py
###################

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from metering.models import IntervalReading, AggregatedReading
from metering.obis import OBIS_MAP


def aggregate_period(period_type, start, end):

    readings = IntervalReading.objects.filter(ts_start__gte=start, ts_start__lt=end)

    for reading in readings:

        obis_meta = OBIS_MAP.get(reading.obis_code, {})

        # ✅ nur Energie (kein Power!)
        if obis_meta.get("type") not in ["energy_import", "energy_export"]:
            continue

        # ✅ Period Start berechnen
        if period_type == "hour":
            period_start = reading.ts_start.replace(minute=0, second=0, microsecond=0)

        elif period_type == "day":
            period_start = reading.ts_start.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        elif period_type == "week":
            period_start = reading.ts_start - timedelta(days=reading.ts_start.weekday())
            period_start = period_start.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        elif period_type == "month":
            period_start = reading.ts_start.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

        elif period_type == "year":
            period_start = reading.ts_start.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )

        else:
            return

        # ✅ Aggregation
        result = IntervalReading.objects.filter(
            meter=reading.meter,
            obis_code=reading.obis_code,
            ts_start__gte=period_start,
            ts_start__lt=end,
        ).aggregate(total=Sum("value"))

        AggregatedReading.objects.update_or_create(
            tenant=reading.tenant,
            meter=reading.meter,
            obis_code=reading.obis_code,
            period_start=period_start,
            period_type=period_type,
            defaults={"value": result["total"] or 0},
        )


@shared_task
def aggregate_hourly():
    now = timezone.now()
    start = now - timedelta(hours=1)
    aggregate_period("hour", start, now)


@shared_task
def aggregate_daily():
    now = timezone.now()
    start = now - timedelta(days=1)
    aggregate_period("day", start, now)


@shared_task
def aggregate_weekly():
    now = timezone.now()
    start = now - timedelta(days=7)
    aggregate_period("week", start, now)


@shared_task
def aggregate_monthly():
    now = timezone.now()
    start = now - timedelta(days=30)
    aggregate_period("month", start, now)


@shared_task
def aggregate_yearly():
    now = timezone.now()
    start = now - timedelta(days=365)
    aggregate_period("year", start, now)
