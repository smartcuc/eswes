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