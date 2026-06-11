#############################
# billing/services_balance.py
#############################

from decimal import Decimal
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from core.models import AggregatedReading, Meter, BalanceSlot

from core.utils.slots import floor_to_slot, slot_minutes


def _sum_kwh(qs):
    v = qs.aggregate(total=Sum("value"))["total"]
    return v if v is not None else Decimal("0")


def compute_balance_for_meter_slot(meter, slot_start):
    """
    Berechnet Balance für genau EINEN Meter und Slot.
    """

    base = AggregatedReading.objects.filter(
        meter=meter,
        period_start=slot_start,
    )
    
    # fallback
    if not base.exists():
        return None

    consumption = _sum_kwh(base.filter(obis_code__startswith="1.8"))
    generation = _sum_kwh(base.filter(obis_code__startswith="2.8"))

    self_consumption = min(consumption, generation)
    grid_import = max(consumption - generation, Decimal("0"))
    grid_export = max(generation - consumption, Decimal("0"))

    # ✅ Tenant sauber über Meter ableiten
    tenant = meter.tenant

    obj, _ = BalanceSlot.objects.update_or_create(
        meter=meter,
        tenant=tenant,
        period_start=slot_start,
        defaults={
            "consumption_kwh": consumption,
            "generation_kwh": generation,
            "self_consumption_kwh": self_consumption,
            "grid_import_kwh": grid_import,
            "grid_export_kwh": grid_export,
        },
    )

    return obj


def floor_to_billing_slot(dt):
    return floor_to_slot(dt, slot_minutes())


def compute_balance_range(start, end):
    """
    Berechnet Balance für ALLE Meter über Zeitraum.
    """

    start = floor_to_billing_slot(start)
    end = floor_to_billing_slot(end)

    meters = Meter.objects.all()

    slot = start
    step = timedelta(minutes=slot_minutes())

    while slot < end:
        for meter in meters:
            compute_balance_for_meter_slot(meter, slot)
        slot += step
