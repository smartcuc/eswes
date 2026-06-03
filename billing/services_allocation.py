##################################
# billing/services_allocation.py
##################################

from billing.models import UserBalanceSlot, UserMeterAssignment
from metering.models import BalanceSlot


def allocate_user_balance_slots(start, end):

    assignments = UserMeterAssignment.objects.filter(is_active=True)
    assignment_map = {a.meter_id: a for a in assignments}

    slots = BalanceSlot.objects.filter(
        period_start__gte=start,
        period_start__lt=end,
    )

    rows = []

    for s in slots:
        if s.consumption_kwh == 0 and s.generation_kwh == 0:
            continue  # 🔥 WICHTIG: keine nutzlosen Slots

        a = assignment_map.get(s.meter_id)
        if not a:
            continue

        rows.append(
            UserBalanceSlot(
                user_id=a.user_id,
                meter_id=s.meter_id,
                period_start=s.period_start,
                consumption_kwh=s.consumption_kwh,
                generation_kwh=s.generation_kwh,
                self_consumption_kwh=s.self_consumption_kwh,
                grid_import_kwh=s.grid_import_kwh,
                grid_export_kwh=s.grid_export_kwh,
            )
        )

    UserBalanceSlot.objects.bulk_create(
        rows,
        update_conflicts=True,
        unique_fields=["user", "meter", "period_start"],
        update_fields=[
            "consumption_kwh",
            "generation_kwh",
            "self_consumption_kwh",
            "grid_import_kwh",
            "grid_export_kwh",
        ],
    )
