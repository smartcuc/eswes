# Data Pipeline

1. Raw ingestion (IntervalReading)
2. Aggregation (15min buckets)
3. Balance calculation
4. User allocation

All steps are deterministic and idempotent.