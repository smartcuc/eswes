##################
# billing/tasks.py
##################

from datetime import timedelta
from celery import shared_task
from django.utils import timezone

from billing.services_balance import compute_balance_range


@shared_task
def compute_balance_last_2h():
    """
    Rechnet Balance Slots der letzten 2 Stunden neu (Late Data tolerant).
    """
    now = timezone.now()
    start = now - timedelta(hours=2)
    compute_balance_range(start, now)
    return {"status": "ok"}
