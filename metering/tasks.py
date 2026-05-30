###################
# metering/tasks.py
###################

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from metering.models import IntervalReading, AggregatedReading


def _floor_to_15min(dt):
    # dt ist timezone-aware
    minute = (dt.minute // 15) * 15
    return dt.replace(minute=minute, second=0, microsecond=0)


def _is_energy_obis(obis: str) -> bool:
    # Wir aggregieren nur Energie-Register (1.8.* Verbrauch, 2.8.* Einspeisung/Erzeugung)
    return obis.startswith("1.8") or obis.startswith("2.8")


def aggregate_15min_range(start, end):
    """
    Aggregiert IntervalReading in 15-Minuten Slots und schreibt AggregatedReading(period_type='15min').

    Wichtig: Erwartet, dass IntervalReading.value bereits eine Intervall-Energie ist (kWh pro Intervall).
    """
    # Hole nur relevanten Zeitraum
    qs = IntervalReading.objects.filter(ts_start__gte=start, ts_start__lt=end)

    # Wir könnten das komplett in SQL machen, aber die Python-Variante ist robust und schnell genug für den Start.
    # Optimierung können wir später machen.
    buckets = {}

    for r in qs.iterator():
        if not _is_energy_obis(r.obis_code):
            continue

        slot = _floor_to_15min(r.ts_start)

        key = (
            r.tenant_id,
            r.member_id if hasattr(r.meter, "member_id") else None,
            r.meter_id,
            r.obis_code,
            slot,
        )

        if key not in buckets:
            buckets[key] = Decimal("0")

        buckets[key] += r.value

    # Upsert AggregatedReading
    for (tenant_id, member_id, meter_id, obis, slot), total in buckets.items():
        AggregatedReading.objects.update_or_create(
            tenant_id=tenant_id,
            member_id=member_id,
            meter_id=meter_id,
            obis_code=obis,
            period_start=slot,
            period_type="15min",
            defaults={"value": total},
        )


@shared_task
def aggregate_15min():
    """
    Läuft regelmäßig (z.B. jede Minute / alle 5 Minuten) und aggregiert die letzten 2 Stunden
    in 15-Minuten Slots. Das reicht, um Spätankommer (Late Data) zu erfassen.
    """
    now = timezone.now()
    start = now - timedelta(hours=2)
    aggregate_15min_range(start, now)
    return {
        "status": "ok",
        "range_start": start.isoformat(),
        "range_end": now.isoformat(),
    }


# Optional: weiterhin hour/day/week/month/year Aggregationen aus den 15min Aggregates bauen
def _period_start(dt, period_type: str):
    if period_type == "hour":
        return dt.replace(minute=0, second=0, microsecond=0)
    if period_type == "day":
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if period_type == "week":
        d = dt - timedelta(days=dt.weekday())
        return d.replace(hour=0, minute=0, second=0, microsecond=0)
    if period_type == "month":
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if period_type == "year":
        return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    raise ValueError("unknown period_type")


def aggregate_period_from_15min(period_type: str, start, end):
    """
    Aggregiert aus AggregatedReading(period_type='15min') in größere Zeiträume.
    """
    base = AggregatedReading.objects.filter(
        period_type="15min",
        period_start__gte=start,
        period_start__lt=end,
    )

    # Gruppiert nach (tenant, member, meter, obis, period_start_bucket)
    # Python-Bucketting ist ok; später kann man es SQL-seitig optimieren.
    buckets = {}

    for r in base.iterator():
        if not _is_energy_obis(r.obis_code):
            continue

        slot = _period_start(r.period_start, period_type)
        key = (r.tenant_id, r.member_id, r.meter_id, r.obis_code, slot)

        if key not in buckets:
            buckets[key] = Decimal("0")

        buckets[key] += r.value

    for (tenant_id, member_id, meter_id, obis, slot), total in buckets.items():
        AggregatedReading.objects.update_or_create(
            tenant_id=tenant_id,
            member_id=member_id,
            meter_id=meter_id,
            obis_code=obis,
            period_start=slot,
            period_type=period_type,
            defaults={"value": total},
        )


@shared_task
def aggregate_hourly():
    now = timezone.now()
    start = now - timedelta(days=2)
    aggregate_period_from_15min("hour", start, now)
    return {"status": "ok"}


@shared_task
def aggregate_daily():
    now = timezone.now()
    start = now - timedelta(days=40)
    aggregate_period_from_15min("day", start, now)
    return {"status": "ok"}


@shared_task
def aggregate_weekly():
    now = timezone.now()
    start = now - timedelta(days=120)
    aggregate_period_from_15min("week", start, now)
    return {"status": "ok"}


@shared_task
def aggregate_monthly():
    now = timezone.now()
    start = now - timedelta(days=400)
    aggregate_period_from_15min("month", start, now)
    return {"status": "ok"}


@shared_task
def aggregate_yearly():
    now = timezone.now()
    start = now - timedelta(days=365 * 5)
    aggregate_period_from_15min("year", start, now)
    return {"status": "ok"}
