##################
# billing/tasks.py
##################

from datetime import timedelta
from celery import shared_task
from django.utils import timezone

from billing.services_balance import compute_balance_range
from billing.services_allocation import allocate_user_balance_range


@shared_task
def compute_balance_last_24h():
    now = timezone.now()
    start = now - timedelta(hours=24)
    compute_balance_range(start, now)
    return {"status": "ok", "from": str(start), "to": str(now)}


@shared_task
def allocate_user_balance_last_24h():
    now = timezone.now()
    start = now - timedelta(hours=24)
    return allocate_user_balance_range(start, now)
