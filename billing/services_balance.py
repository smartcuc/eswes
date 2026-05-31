#############################
# billing/services_balance.py
#############################

from decimal import Decimal
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from metering.models import AggregatedReading, Tenant
from metering.models import BalanceSlot


def _sum_kwh(qs):
    v = qs.aggregate(total=Sum("value"))["total"]
    return v if v is not None else Decimal("0")


def compute_balance_for_slot(tenant: Tenant, slot_start):
    """
    slot_start muss exakt auf 15min gefloort sein.
    Nutzt AggregatedReading(period_type='15min').

    Verbrauch: obis 1.8.*
    Erzeugung/Einspeisung: obis 2.8.*
    """
    base = AggregatedReading.objects.filter(
        tenant=tenant,
        period_type="15min",
        period_start=slot_start,
    )

    consumption = _sum_kwh(base.filter(obis_code__startswith="1.8"))
    generation = _sum_kwh(base.filter(obis_code__startswith="2.8"))

    self_consumption = min(consumption, generation)
    grid_import = max(consumption - generation, Decimal("0"))
    grid_export = max(generation - consumption, Decimal("0"))

    obj, _ = BalanceSlot.objects.update_or_create(
        tenant=tenant,
        period_start=slot_start,
        period_type="15min",
        defaults={
            "consumption_kwh": consumption,
            "generation_kwh": generation,
            "self_consumption_kwh": self_consumption,
            "grid_import_kwh": grid_import,
            "grid_export_kwh": grid_export,
        },
    )
    return obj


def floor_to_15min(dt):
    minute = (dt.minute // 15) * 15
    return dt.replace(minute=minute, second=0, microsecond=0)


def compute_balance_range(start, end):
    """
    Berechnet Balance für alle Tenants für Slots im Zeitraum [start, end).
    """
    start = floor_to_15min(start)
    end = floor_to_15min(end)

    tenants = Tenant.objects.all()

    slot = start
    while slot < end:
        for t in tenants:
            compute_balance_for_slot(t, slot)
        slot += timedelta(minutes=15)
