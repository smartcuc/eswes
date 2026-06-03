##################
# billing/tasks.py
##################

from datetime import timedelta
from celery import shared_task
from django.utils import timezone

from metering.services_slots import floor_to_slot, slot_minutes
from billing.services_balance import compute_balance_for_slots
from billing.services_allocation import allocate_user_balance_for_slots

from celery import shared_task
from billing.services_dirty import process_all


@shared_task
def process_dirty():
    process_all(5000)
