###########################
# billing/services_dirty.py
###########################

from django.db import transaction
from billing.models import DirtySlot
from billing.services_balance import compute_balance_for_slots
from billing.services_allocation import allocate_user_balance_for_slots


def process_dirty_slots(limit=5000):

    dirty = list(DirtySlot.objects.order_by("period_start")[:limit])

    if not dirty:
        return {"status": "noop"}

    from datetime import timedelta

    start = min(d.period_start for d in dirty)
    end = max(d.period_start for d in dirty) + timedelta(minutes=15)

    with transaction.atomic():
        compute_balance_for_slots(start, end)
        allocate_user_balance_for_slots(start, end)

        DirtySlot.objects.filter(id__in=[d.id for d in dirty]).delete()

    return {"processed": len(dirty)}
