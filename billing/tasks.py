##################
# billing/tasks.py
##################

from celery import shared_task
from django.db import connection


@shared_task
def compute_balance_last_24h():
    sql = """
    INSERT INTO metering_balanceslot (
        id,
        meter_id,
        period_start,
        consumption_kwh,
        generation_kwh,
        self_consumption_kwh,
        grid_import_kwh,
        grid_export_kwh,
        created_at
    )
    SELECT
        gen_random_uuid(),
        meter_id,
        slot,
        value / 4.0,
        0,
        0,
        value / 4.0,
        0,
        now()
    FROM (
        SELECT
            meter_id,
            ts_start,
            value,
            generate_series(
                ts_start,
                ts_start + interval '45 minutes',
                interval '15 minutes'
            ) AS slot
        FROM metering_intervalreading
        WHERE ts_start >= now() - interval '24 hours'
    ) t
    ON CONFLICT DO NOTHING;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)

    return "ok"


@shared_task
def compute_dirty_slots_task():
    return "ok"


@shared_task
def compute_balance_rolling():
    return "ok"
