-- ✅ Extensions
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ✅ Dirty trigger function
CREATE OR REPLACE FUNCTION public.mark_dirty_after_agg()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO billing_dirtyslot (meter_id, period_start)
    VALUES (NEW.meter_id, NEW.period_start)
    ON CONFLICT DO NOTHING;

    FOR i IN 1..4 LOOP
        INSERT INTO billing_dirtyslot (meter_id, period_start)
        VALUES (
            NEW.meter_id,
            NEW.period_start - (i * interval '15 min')
        )
        ON CONFLICT DO NOTHING;
    END LOOP;

 REPLACE FUNCTION public.metering_rollup_15min()    RETURN NEW;
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO metering_aggregatedreading (
        id, meter_id, period_start, period_end, value, unit, obis_code
    )
    SELECT
        gen_random_uuid(),
        ir.meter_id,

        date_trunc('hour', ir.ts_start)
        + floor(date_part('minute', ir.ts_start) / 15) * interval '15 minutes',

        date_trunc('hour', ir.ts_start)
        + (floor(date_part('minute', ir.ts_start) / 15) + 1) * interval '15 minutes',

        SUM(ir.value),
        'kWh',
        ir.obis_code

    FROM metering_intervalreading ir
    GROUP BY ir.meter_id,
             date_trunc('hour', ir.ts_start)
             + floor(date_part('minute', ir.ts_start) / 15) * interval '15 minutes',
             ir.obis_code

    ON CONFLICT (meter_id, period_start)
    DO UPDATE SET value = EXCLUDED.value;
END;
$$;


-- ✅ Balance calc
CREATE OR REPLACE FUNCTION public.process_dirty_balance(limit_rows integer DEFAULT 5000)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE cnt int;
BEGIN

WITH dirty AS (
    SELECT meter_id, period_start
    FROM billing_dirtyslot
    LIMIT limit_rows
)

INSERT INTO metering_balanceslot (
    id, meter_id, period_start,
    consumption_kwh, generation_kwh,
    self_consumption_kwh,
    grid_import_kwh, grid_export_kwh,
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
ON CONFLICT (meter_id, period_start)
DO UPDATE SET
    consumption_kwh = EXCLUDED.consumption_kwh,
    generation_kwh = EXCLUDED.generation_kwh,
    self_consumption_kwh = EXCLUDED.self_consumption_kwh,
    grid_import_kwh = EXCLUDED.grid_import_kwh,
    grid_export_kwh = EXCLUDED.grid_export_kwh;

GET DIAGNOSTICS cnt = ROW_COUNT;

DELETE FROM billing_dirtyslot
WHERE (meter_id, period_start) IN (
    SELECT meter_id, period_start
    FROM billing_dirtyslot
    LIMIT limit_rows
);

RETURN cnt;

END;
$$;


-- ✅ Trigger (WICHTIG)
DROP TRIGGER IF EXISTS trigger_dirty ON metering_aggregatedreading;

CREATE TRIGGER trigger_dirty
AFTER INSERT OR UPDATE
ON metering_aggregatedreading
FOR EACH ROW
EXECUTE FUNCTION public.mark_dirty_after_agg();
END;
$$;


-- ✅ Rollup 15min
