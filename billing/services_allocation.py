##################################
# billing/services_allocation.py
##################################

from datetime import timedelta
from django.db.models import Q

from billing.models import UserMeterAssignment, UserBalanceSlot
from core.models import BalanceSlot
from core.utils.slots import floor_to_slot, slot_minutes


def _active_assignment_map_for_slot(slot_start):
    """
    Liefert ein Mapping:
        meter_id -> aktive UserMeterAssignment
    für genau einen Slot-Zeitpunkt.
    """

    assignments = (
        UserMeterAssignment.objects.filter(
            is_active=True,
            valid_from__lte=slot_start,
        )
        .filter(Q(valid_to__isnull=True) | Q(valid_to__gt=slot_start))
        .select_related("user", "meter")
    )

    return {a.meter_id: a for a in assignments}


def allocate_user_balance_for_slot(slot_start):
    """
    Rollt Meter-Balance auf den zugeordneten Billing-User hoch.

    Wichtig:
    - genau EIN aktiver Billing-User pro Meter
    - ein User kann mehrere Meter haben
    """
    slot_start = floor_to_slot(slot_start, slot_minutes())

    assignment_map = _active_assignment_map_for_slot(slot_start)

    meter_balances = BalanceSlot.objects.filter(
        period_start=slot_start,
        meter__isnull=False,
    ).select_related("meter", "tenant")

    written = 0
    skipped = 0

    for row in meter_balances:
        assignment = assignment_map.get(row.meter_id)

        if assignment is None:
            skipped += 1
            continue

        UserBalanceSlot.objects.update_or_create(
            user=assignment.user,
            meter=row.meter,
            period_start=row.period_start,
            defaults={
                "tenant": row.tenant,
                "consumption_kwh": row.consumption_kwh,
                "generation_kwh": row.generation_kwh,
                "self_consumption_kwh": row.self_consumption_kwh,
                "grid_import_kwh": row.grid_import_kwh,
                "grid_export_kwh": row.grid_export_kwh,
            },
        )
        written += 1

    return {
        "status": "ok",
        "slot_start": str(slot_start),
        "written": written,
        "skipped": skipped,
    }


def allocate_user_balance_range(start, end):
    """
    Rechnet UserBalanceSlots für alle Slots im Zeitraum [start, end).
    """
    start = floor_to_slot(start, slot_minutes())
    end = floor_to_slot(end, slot_minutes())

    slot = start
    step = timedelta(minutes=slot_minutes())

    results = []

    while slot < end:
        results.append(allocate_user_balance_for_slot(slot))
        slot += step

    return {
        "status": "ok",
        "from": str(start),
        "to": str(end),
        "results": results,
    }
