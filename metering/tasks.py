###################
# metering/tasks.py
###################
###################################.py
###################

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from metering.models import IntervalReading, AggregatedReading


def _slot_minutes() -> int:
    """
    Zielgranularität für Billing / Balance / Aggregation.
    Standard: 15 Minuten.
    """
    return int(getattr(settings, "BILLING_SLOT_MINUTES", 15))


def _floor_to_slot(dt, minutes: int | None = None):
    """
    Floort einen aware datetime auf das konfigurierte Slot-Intervall.
    """
    minutes = minutes or _slot_minutes()

    minute = (dt.minute // minutes) * minutes
    return dt.replace(minute=minute, second=0, microsecond=0)


def _slot_delta(minutes: int | None = None):
    minutes = minutes or _slot_minutes()
    return timedelta(minutes=minutes)


def _iter_slots(start_dt, end_dt, minutes: int | None = None):
    """
    Iteriert über alle Slots, die das Intervall [start_dt, end_dt) schneiden.
    """
    minutes = minutes or _slot_minutes()
    slot = _floor_to_slot(start_dt, minutes)

    while slot < end_dt:
        yield slot
        slot += timedelta(minutes=minutes)


def _is_energy_obis(obis: str) -> bool:
    """
    Aggregiert nur Energie-Register:
    - 1.8.* Verbrauch
    - 2.8.* Erzeugung / Einspeisung
    """
    return obis.startswith("1.8") or obis.startswith("2.8")


def _safe_ts_end(reading):
    """
    Liefert ein sinnvolles Enddatum für das Rohintervall.

    Erwartung:
    - Idealerweise ist reading.ts_end gesetzt (wie bei Tibber)
    - Fallback: 1 Slot weiter
    """
    if getattr(reading, "ts_end", None):
        return reading.ts_end

    # Fallback, falls ts_end fehlt
    return reading.ts_start + _slot_delta()


def _decimal_fraction(overlap_seconds: float, duration_seconds: float) -> Decimal:
    if duration_seconds <= 0 or overlap_seconds <= 0:
        return Decimal("0")

    return (Decimal(str(overlap_seconds)) / Decimal(str(duration_seconds))).quantize(
        Decimal("0.0000001"),
        rounding=ROUND_HALF_UP,
    )


def aggregate_15min_range(start, end):
    """
    Normalisiert IntervalReading auf 15‑Minuten-Slots (bzw. BILLING_SLOT_MINUTES).

    WICHTIG:
    - IntervalReading.value wird als Intervallenergie interpretiert (kWh pro Intervall)
    - Stündliche Werte werden proportional auf 4x15min verteilt
    - 15‑Minuten-Werte bleiben 1:1 in einem Slot
    - Später 10min möglich, ohne Business‑Logik neu zu bauen
    """
    minutes = _slot_minutes()

    qs = (
        IntervalReading.objects.filter(
            ts_start__lt=end,
            ts_end__gt=start,
        )
        .select_related("meter")
        .order_by("ts_start")
    )

    buckets = defaultdict(Decimal)

    for r in qs.iterator():
        if not _is_energy_obis(r.obis_code):
            continue

        src_start = r.ts_start
        src_end = _safe_ts_end(r)
        value = r.value or Decimal("0")

        if src_end <= src_start:
            continue

        duration_seconds = (src_end - src_start).total_seconds()

        # Alle Slots durchlaufen, die dieses Intervall schneiden
        for slot_start in _iter_slots(src_start, src_end, minutes):
            slot_end = slot_start + _slot_delta(minutes)

            overlap_start = max(src_start, slot_start)
            overlap_end = min(src_end, slot_end)

            overlap_seconds = (overlap_end - overlap_start).total_seconds()

            if overlap_seconds <= 0:
                continue

            fraction = _decimal_fraction(overlap_seconds, duration_seconds)

            # Falls dein Meter-Modell owner_member verwendet:
            member_id = getattr(r.meter, "owner_member_id", None)

            key = (
                r.tenant_id,
                member_id,
                r.meter_id,
                r.obis_code,
                slot_start,
            )

            buckets[key] += value * fraction

    written = 0

    for (tenant_id, member_id, meter_id, obis, slot_start), total in buckets.items():
        lookup = {
            "tenant_id": tenant_id,
            "meter_id": meter_id,
            "obis_code": obis,
            "period_start": slot_start,
            "period_type": f"{minutes}min",
        }

        # Nur setzen, wenn dein AggregatedReading-Modell member_id wirklich hat
        if member_id is not None:
            lookup["member_id"] = member_id

        AggregatedReading.objects.update_or_create(
            **lookup,
            defaults={
                "value": total.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP),
            },
        )
        written += 1

    return {
        "status": "ok",
        "range_start": start.isoformat(),
        "range_end": end.isoformat(),
        "slot_minutes": minutes,
        "rows": written,
    }


@shared_task
def aggregate_15min():
    """
    Aggregiert die letzten 48 Stunden in Billing-Slots.
    Das ist robust genug für Late Data / Re-Runs.
    """
    now = timezone.now()
    start = now - timedelta(hours=48)

    return aggregate_15min_range(start, now)


def _period_start(dt, period_type: str):
    """
    Leitet größere Perioden aus 15‑Minuten-Slots ab.
    """
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

    raise ValueError(f"unknown period_type: {period_type}")


def aggregate_period_from_15min(period_type: str, start, end):
    """
    Aggregiert aus AggregatedReading(period_type='<slot>min') in größere Zeiträume.
    """
    base = AggregatedReading.objects.filter(
        period_type=f"{_slot_minutes()}min",
        period_start__gte=start,
        period_start__lt=end,
    )

    buckets = defaultdict(Decimal)

    for r in base.iterator():
        if not _is_energy_obis(r.obis_code):
            continue

        slot = _period_start(r.period_start, period_type)
        member_id = getattr(r, "member_id", None)

        key = (
            r.tenant_id,
            member_id,
            r.meter_id,
            r.obis_code,
            slot,
        )

        buckets[key] += r.value or Decimal("0")

    written = 0

    for (tenant_id, member_id, meter_id, obis, slot_start), total in buckets.items():
        lookup = {
            "tenant_id": tenant_id,
            "meter_id": meter_id,
            "obis_code": obis,
            "period_start": slot_start,
            "period_type": period_type,
        }

        if member_id is not None:
            lookup["member_id"] = member_id

        AggregatedReading.objects.update_or_create(
            **lookup,
            defaults={
                "value": total.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP),
            },
        )
        written += 1

    return {
        "status": "ok",
        "period_type": period_type,
        "rows": written,
        "range_start": start.isoformat(),
        "range_end": end.isoformat(),
    }


@shared_task
def aggregate_hourly():
    now = timezone.now()
    start = now - timedelta(days=2)
    return aggregate_period_from_15min("hour", start, now)


@shared_task
def aggregate_daily():
    now = timezone.now()
    start = now - timedelta(days=40)
    return aggregate_period_from_15min("day", start, now)


@shared_task
def aggregate_weekly():
    now = timezone.now()
    start = now - timedelta(days=120)
    return aggregate_period_from_15min("week", start, now)


@shared_task
def aggregate_monthly():
    now = timezone.now()
    start = now - timedelta(days=400)
    return aggregate_period_from_15min("month", start, now)


@shared_task
def aggregate_yearly():
    now = timezone.now()
    start = now - timedelta(days=365 * 5)
    return aggregate_period_from_15min("year", start, now)
