##################
# billing/tasks.py
##################

from celery import shared_task
from billing.services_dirty import process_all


@shared_task
def process_dirty():
    process_all(5000)
