-- ✅ INTERVALREADING vorbereiten

ALTER TABLE metering_intervalreading
DROP CONSTRAINT IF EXISTS metering_intervalreading_pkey;

CREATE UNIQUE INDEX IF NOT EXISTS uniq_interval
ON metering_intervalreading (id, ts_start);

-- ✅ AggregatedReading vorbereiten

ALTER TABLE metering_aggregatedreading
DROP CONSTRAINT IF EXISTS metering_aggregatedreading_pkey;

ALTER TABLE metering_aggregatedreading
ADD PRIMARY KEY (id, period_start);

-- ✅ Balance vorbereiten

ALTER TABLE metering_balanceslot
DROP CONSTRAINT IF EXISTS metering_balanceslot_pkey;

ALTER TABLE metering_balanceslot
ADD PRIMARY KEY (id, period_start);

-- ✅ Hypertables

SELECT create_hypertable(
    'metering_intervalreading',
    'ts_start',
    migrate_data => true
);

SELECT create_hypertable(
    'metering_aggregatedreading',
    'period_start',
    migrate_data => true
);

SELECT create_hypertable(
    'metering_balanceslot',
    'period_start',
    migrate_data => true
);
