##################
# billing/tasks.py
##################

from datetime import timedelta
from celery import shared_task
from django.utils import timezone

from metering.services_slots import floor_to_slot, slot_minutes
from billing.services_balance import compute_balance_for_slots
from billing.services_allocation import allocate_user_balance_for_slots


# ✅ Haupt-Task: genau EIN Slot
@shared_task
def compute_balance_incremental():
    now = timezone.now()
    end = floor_to_slot(now, slot_minutes())

    start = end - timedelta(minutes=slot_minutes())

    compute_balance_for_slots(start, end)
    allocate_user_balance_for_slots(start, end)

    return {"type": "incremental", "from": str(start), "to": str(end)}


# ✅ Rolling Window (Late Data Fix)
@shared_task
def compute_balance_rolling():
    now = timezone.now()
    end = floor_to_slot(now, slot_minutes())

    # 8 Slots = 2 Stunden
    start = end - timedelta(minutes=slot_minutes() * 8)

    compute_balance_for_slots(start, end)
    allocate_user_balance_for_slots(start, end)

    return {"type": "rolling", "from": str(start), "to": str(end)}


# ✅ Safety Backfill (selten)
@shared_task
def compute_balance_backfill():
    now = timezone.now()
    end = floor_to_slot(now, slot_minutes())

    start = end - timedelta(hours=24)

    compute_balance_for_slots(start, end)
    allocate_user_balance_for_slots(start, end)

    return {"type": "backfill", "from": str(start), "to": str(end)}


from datetime import timedelta
from celery import shared_task
from django.utils import timezone

from metering.services_slots import floor_to_slot, slot_minutes
from billing.services_balance import compute_balance_for_slots
from billing.services_allocation import allocate_user_balance_for_slots
from billing.services_dirty import process_dirty_slots


# ✅ Haupttask: Dirty Slots (Primary Path)
@shared_task
def compute_dirty_slots_task():
    return process_dirty_slots(limit=5000)


# ✅ Rolling Window (Fallback / Late Data)
@shared_task
def compute_balance_rolling():
    now = timezone.now()
    end = floor_to_slot(now, slot_minutes())
    start = end - timedelta(minutes=slot_minutes() * 8)  # 2h

    compute_balance_for_slots(start, end)
    allocate_user_balance_for_slots(start, end)

    return {"type": "rolling", "from": str(start), "to": str(end)}


# ✅ Daily Backfill (safety)
@shared_task
def compute_balance_backfill():
    now = timezone.now()
    end = floor_to_slot(now, slot_minutes())
    start = end - timedelta(hours=24)

    compute_balance_for_slots(start, end)
    allocate_user_balance_for_slots(start, end)

    return {"type": "backfill", "from": str(start), "to": str(end)}
