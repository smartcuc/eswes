-- ✅ Balance Unique

CREATE UNIQUE INDEX IF NOT EXISTS uniq_balance_meter_time
ON metering_balanceslot (meter_id, period_start);

-- ✅ UserBalance Unique

CREATE UNIQUE INDEX IF NOT EXISTS uniq_user_meter_time
ON billing_userbalanceslot (user_id, meter_id, period_start);

-- ✅ Dirty Index

CREATE INDEX IF NOT EXISTS idx_dirty_meter_time
ON billing_dirtyslot (meter_id, period_start);

-- ✅ Performance Index

CREATE INDEX IF NOT EXISTS idx_interval_meter_time
ON metering_intervalreading (meter_id, ts_start DESC);
