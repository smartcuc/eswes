# Schema Überblick

## Tabellen

### metering_intervalreading
- Rohdaten (15-min Slots)
- Quelle: Smart Meter

Wichtige Felder:
- meter_id (FK)
- ts_start
- value
- obis_code (1.8.0 / 2.8.0)

---

### metering_aggregatedreading
- aggregierte Werte

---

### metering_balanceslot
- Business Layer
- Energieflüsse

---

## Beziehungen

Meter
 → IntervalReading
 → AggregatedReading
 → BalanceSlot