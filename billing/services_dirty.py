###########################
# billing/services_dirty.py
###########################

from django.db import connection

SQL_BALANCE = """
WITH dirty AS (
    SELECT meter_id, period_start
    FROM billing_dirtyslot
    ORDER BY period_start
    LIMIT %s
)

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
    ar.meter_id,
    ar.period_start,

    SUM(CASE WHEN obis_code = '1.8.0' THEN value ELSE 0 END),
    SUM(CASE WHEN obis_code = '2.8.0' THEN value ELSE 0 END),

    LEAST(
        SUM(CASE WHEN obis_code = '1.8.0' THEN value ELSE 0 END),
        SUM(CASE WHEN obis_code = '2.8.0' THEN value ELSE 0 END)
    ),

    GREATEST(
        SUM(CASE WHEN obis_code = '1.8.0' THEN value ELSE 0 END)
        - SUM(CASE WHEN obis_code = '2.8.0' THEN value ELSE 0 END),
        0
    ),

    GREATEST(
        SUM(CASE WHEN obis_code = '2.8.0' THEN value ELSE 0 END)
        - SUM(CASE WHEN obis_code = '1.8.0' THEN value ELSE 0 END),
        0
    ),

    now()

FROM metering_aggregatedreading ar
JOIN dirty d
  ON d.meter_id = ar.meter_id
 AND d.period_start = ar.period_start

GROUP BY ar.meter_id, ar.period_start

HAVING
    SUM(CASE WHEN obis_code = '1.8.0' THEN value ELSE 0 END) > 0
 OR SUM(CASE WHEN obis_code = '2.8.0' THEN value ELSE 0 END) > 0

ON CONFLICT (meter_id, period_start)
DO UPDATE SET
    consumption_kwh = EXCLUDED.consumption_kwh,
    generation_kwh = EXCLUDED.generation_kwh,
    self_consumption_kwh = EXCLUDED.self_consumption_kwh,
    grid_import_kwh = EXCLUDED.grid_import_kwh,
    grid_export_kwh = EXCLUDED.grid_export_kwh;
"""


SQL_DELETE = """
DELETE FROM billing_dirtyslot
WHERE (meter_id, period_start) IN (
    SELECT meter_id, period_start
    FROM billing_dirtyslot
    ORDER BY period_start
    LIMIT %s
);
"""


def process_all(limit=5000):
    with connection.cursor() as cursor:
        cursor.execute(SQL_BALANCE, [limit])
        cursor.execute(SQL_DELETE, [limit])
