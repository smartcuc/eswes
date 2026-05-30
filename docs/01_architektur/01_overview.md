# Architektur Überblick

## Datenfluss

Meter → IntervalReading → Aggregation → BalanceSlot → API

## Komponenten

- Django API
- TimescaleDB
- Celery
- Redis