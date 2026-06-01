############################
# metering/services_slots.py
############################

from datetime import timedelta
from django.conf import settings
from django.utils import timezone


def slot_minutes():
    return int(getattr(settings, "BILLING_SLOT_MINUTES", 15))


def floor_to_slot(dt, minutes=None):
    minutes = minutes or slot_minutes()

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())

    minute = (dt.minute // minutes) * minutes
    return dt.replace(minute=minute, second=0, microsecond=0)


def ceil_to_slot(dt, minutes=None):
    minutes = minutes or slot_minutes()

    floored = floor_to_slot(dt, minutes)
    if floored == dt.replace(second=0, microsecond=0):
        return floored
    return floored + timedelta(minutes=minutes)


def iter_slots(start, end, minutes=None):
    minutes = minutes or slot_minutes()

    current = floor_to_slot(start, minutes)
    while current < end:
        yield current
        current += timedelta(minutes=minutes)


def overlap_fraction(src_start, src_end, slot_start, slot_end):
    """
    Anteil des Quellenintervalls, der in den Slot fällt.
    """
    latest_start = max(src_start, slot_start)
    earliest_end = min(src_end, slot_end)

    overlap = (earliest_end - latest_start).total_seconds()
    total = (src_end - src_start).total_seconds()

    if overlap <= 0 or total <= 0:
        return 0.0

    return overlap / total
