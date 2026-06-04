###################
# metering/tasks.py
###################

from celery import shared_task
from django.db import connection
from datetime import timedelta, datetime


@shared_task
def aggregate_15min():
    return "ok"


@shared_task
def aggregate_hourly():
    now = datetime.utcnow()
    start = now - timedelta(hours=24)

    sql = """
    INSERT INTO metering_aggregatedreading (
        id,
        meter_id,
        period_start,
        period_type,
        obis_code,
        value,
        unit,
        created_at
    )
    SELECT
        gen_random_uuid(),
        meter_id,
        date_trunc('hour', ts_start),
        'hour',
        obis_code,
        SUM(value),
        'kWh',
        now()
    FROM metering_intervalreading
    WHERE ts_start >= %s AND ts_start < %s
    GROUP BY meter_id, date_trunc('hour', ts_start), obis_code

    ON CONFLICT (meter_id, period_start, obis_code)
    DO UPDATE SET value = EXCLUDED.value;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, [start, now])

    return "ok"
