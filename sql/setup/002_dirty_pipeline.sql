-- ✅ Dirty Table

CREATE TABLE IF NOT EXISTS billing_dirtyslot (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    meter_id uuid NOT NULL,
    period_start timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (meter_id, period_start)
);

-- ✅ Trigger Function

CREATE OR REPLACE FUNCTION mark_dirty_after_agg()
RETURNS trigger AS $$
BEGIN

    INSERT INTO billing_dirtyslot (meter_id, period_start)
    VALUES (NEW.meter_id, NEW.period_start)
    ON CONFLICT DO NOTHING;

    -- Late data fix (1h zurück)
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
$$ LANGUAGE plpgsql;

-- ✅ Trigger

DROP TRIGGER IF EXISTS trigger_dirty ON metering_aggregatedreading;

CREATE TRIGGER trigger_dirty
AFTER INSERT OR UPDATE
ON metering_aggregatedreading
FOR EACH ROW
EXECUTE FUNCTION mark_dirty_after_agg();

