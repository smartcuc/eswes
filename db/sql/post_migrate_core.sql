-- =====================================================
-- ✅ CORE DATA PIPELINE SETUP (NO metering, ONLY core)
-- =====================================================

-- -----------------------------------------------------
-- EXTENSIONS
-- -----------------------------------------------------
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- -----------------------------------------------------
-- DIRTY TRIGGER FUNCTION
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION public.mark_dirty_after_agg()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    -- aktueller Slot
    INSERT INTO billing_dirtyslot (meter_id, period_start)
    VALUES (NEW.meter_id, NEW.period_start)
    ON CONFLICT DO NOTHING;

    -- rückwirkende Slots (Late Data)
    FOR i IN 1..4 LOOP
        INSERT INTO billing_dirtyslot (meter_id, period_start)
        VALUES (
            NEW.meter_id,
            NEW.period_start - (i * interval '15 min')
        )
        ON CONFLICT DO NOTHING;
    END LOOP;

    RETURN NEW;
END;
$$;


-- -----------------------------------------------------
-- ROLLUP: Interval → Aggregated
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION public.rollup_15min()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO core_aggregatedreading (
        id,
        meter_id,
        period_start,
        period_end,
        value,
        unit,
        obis_code
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

    FROM core_intervalreading ir
    GROUP BY
        ir.meter_id,
        date_trunc('hour', ir.ts_start)
        + floor(date_part('minute', ir.ts_start) / 15) * interval '15 minutes',
        ir.obis_code

    ON CONFLICT (meter_id, period_start)
    DO UPDATE SET value = EXCLUDED.value;

END;
$$;


-- -----------------------------------------------------
-- DIRTY BALANCE PROCESSOR
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION public.process_dirty_balance(limit_rows integer DEFAULT 5000)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE cnt int;
BEGIN

WITH dirty AS (
    SELECT meter_id, period_start
    FROM billing_dirtyslot
    ORDER BY period_start
    LIMIT limit_rows
)

INSERT INTO core_balanceslot (
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

FROM core_aggregatedreading ar
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
    ORDER BY period_start
    LIMIT limit_rows
);

RETURN cnt;

END;
$$;


-- -----------------------------------------------------
-- TRIGGER
-- -----------------------------------------------------
DROP TRIGGER IF EXISTS trigger_dirty ON core_aggregatedreading;

CREATE TRIGGER trigger_dirty
AFTER INSERT OR UPDATE
ON core_aggregatedreading
FOR EACH ROW
EXECUTE FUNCTION public.mark_dirty_after_agg();


-- -----------------------------------------------------
-- TIMESCALE (Core & EMS Hypertables)
-- TimescaleDB verlangt, dass der Partitionierungs-Key Teil des Primary Keys ist.
-- -----------------------------------------------------
DO $$
BEGIN
    -- 1. core_intervalreading
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'core_intervalreading') THEN
        ALTER TABLE core_intervalreading DROP CONSTRAINT IF EXISTS core_intervalreading_pkey CASCADE;
        ALTER TABLE core_intervalreading ADD PRIMARY KEY (id, ts_start);
        PERFORM create_hypertable('core_intervalreading', 'ts_start', if_not_exists => TRUE, migrate_data => TRUE);
    END IF;

    -- 2. core_aggregatedreading
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'core_aggregatedreading') THEN
        ALTER TABLE core_aggregatedreading DROP CONSTRAINT IF EXISTS core_aggregatedreading_pkey CASCADE;
        ALTER TABLE core_aggregatedreading DROP CONSTRAINT IF EXISTS core_aggregatedreading_meter_id_period_start_key CASCADE;
        ALTER TABLE core_aggregatedreading ADD PRIMARY KEY (id, period_start);
        PERFORM create_hypertable('core_aggregatedreading', 'period_start', if_not_exists => TRUE, migrate_data => TRUE);
    END IF;

    -- 3. core_balanceslot
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'core_balanceslot') THEN
        ALTER TABLE core_balanceslot DROP CONSTRAINT IF EXISTS core_balanceslot_pkey CASCADE;
        ALTER TABLE core_balanceslot ADD PRIMARY KEY (id, period_start);
        PERFORM create_hypertable('core_balanceslot', 'period_start', if_not_exists => TRUE, migrate_data => TRUE);
    END IF;

    -- 4. market_spotprice
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'market_spotprice') THEN
        ALTER TABLE market_spotprice DROP CONSTRAINT IF EXISTS market_spotprice_pkey CASCADE;
        ALTER TABLE market_spotprice DROP CONSTRAINT IF EXISTS market_spotprice_timestamp_source_a3536ea1_uniq CASCADE;
        ALTER TABLE market_spotprice ADD PRIMARY KEY (id, timestamp);
        PERFORM create_hypertable('market_spotprice', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
    END IF;

    -- 5. devices_devicemetric
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'devices_devicemetric') THEN
        ALTER TABLE devices_devicemetric DROP CONSTRAINT IF EXISTS devices_devicemetric_pkey CASCADE;
        ALTER TABLE devices_devicemetric ADD PRIMARY KEY (id, timestamp);
        PERFORM create_hypertable('devices_devicemetric', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
    END IF;

    -- 6. devices_devicemetric1m
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'devices_devicemetric1m') THEN
        ALTER TABLE devices_devicemetric1m DROP CONSTRAINT IF EXISTS devices_devicemetric1m_pkey CASCADE;
        ALTER TABLE devices_devicemetric1m DROP CONSTRAINT IF EXISTS devices_devicemetric1m_device_id_bucket_metric_key_77e77b63_uniq CASCADE;
        ALTER TABLE devices_devicemetric1m ADD PRIMARY KEY (id, bucket);
        PERFORM create_hypertable('devices_devicemetric1m', 'bucket', if_not_exists => TRUE, migrate_data => TRUE);
    END IF;

    -- 7. devices_devicemetric5m
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'devices_devicemetric5m') THEN
        ALTER TABLE devices_devicemetric5m DROP CONSTRAINT IF EXISTS devices_devicemetric5m_pkey CASCADE;
        ALTER TABLE devices_devicemetric5m DROP CONSTRAINT IF EXISTS devices_devicemetric5m_device_id_bucket_metric_key_3811f5d6_uniq CASCADE;
        ALTER TABLE devices_devicemetric5m ADD PRIMARY KEY (id, bucket);
        PERFORM create_hypertable('devices_devicemetric5m', 'bucket', if_not_exists => TRUE, migrate_data => TRUE);
    END IF;
END $$;


-- =====================================================
-- ✅ DONE
-- =====================================================