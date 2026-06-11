###############
# core/tasks.py
###############

from celery import shared_task
from django.db import connection


@shared_task
def rollup_15min():
    with connection.cursor() as cursor:
        cursor.execute("SELECT rollup_15min();")


@shared_task
def process_dirty_balance():
    with connection.cursor() as cursor:
        cursor.execute("SELECT process_dirty_balance();")

        