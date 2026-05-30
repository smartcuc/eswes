# Timescale Setup

## Voraussetzungen

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgcrypto;


IntervalReading
ALTER TABLE metering_intervalreading
DROP CONSTRAINT metering_intervalreading_pkey;

SELECT create_hypertable(
    'metering_intervalreading',
    'ts_start',
    if_not_exists => TRUE
);

ALTER TABLE metering_intervalreading
ADD PRIMARY KEY (id, ts_start);


AggregatedReading
ALTER TABLE metering_aggregatedreading
DROP CONSTRAINT metering_aggregatedreading_pkey;

SELECT create_hypertable(
    'metering_aggregatedreading',
    'period_start',
    if_not_exists => TRUE
);

ALTER TABLE metering_aggregatedreading
ADD PRIMARY KEY (id, period_start);


BalanceSlot
ALTER TABLE metering_balanceslot
DROP CONSTRAINT metering_balanceslot_pkey;

SELECT create_hypertable(
    'metering_balanceslot',
    'period_start',
    if_not_exists => TRUE
);

ALTER TABLE metering_balanceslot
ADD PRIMARY KEY (id, period_start)
