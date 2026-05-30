# ✅ Master TODO – Energy Sharing Platform

## 📌 Status
- ✅ Infrastruktur und Datenbank stehen
- ✅ TimescaleDB läuft
- ✅ Hypertables erstellt
- 🚧 Fokus jetzt: Business Logic & Dokumentation

---

# 🧩 PHASE 1 – Infrastruktur ✅ (FERTIG)

- [x] Django Projekt setup
- [x] PostgreSQL installiert
- [x] TimescaleDB installiert
- [x] DB Verbindung konfiguriert
- [x] UUID als Primary Keys

---

# ⚙️ PHASE 2 – Data Layer ✅ (FERTIG)

- [x] IntervalReading (Hypertable)
- [x] SpotPrice (Hypertable)
- [x] AggregatedReading (Hypertable)
- [x] Constraints angepasst (Timescale kompatibel)
- [x] Composite Primary Keys auf DB-Level

---

# 🚧 PHASE 3 – Core Logic (AKTUELL)

## 🔥 Aggregation

- [ ] Stored Function: `metering_rollup_readings`
- [ ] Stored Procedure: `metering_rollup_window`
- [ ] Aggregation testen (15min / hour / day)

---

## 🔥 OBIS Definition

- [ ] Datei: `metering/constants.py`

```python
OBIS_CONSUMPTION = "1.8.0"
OBIS_GENERATION = "2.8.0"
 optional: obis_codes Tabelle


🔥 BalanceSlot Calculation

 Modell: BalanceSlot definieren/prüfen
 Stored Procedure bauen:

consumption
generation
self_consumption
grid_import
grid_export




🧠 PHASE 4 – Orchestration
🔧 Django Command

 Datei: metering/management/commands/rollup.py
 ruft CALL metering_rollup_window(...) auf
 CLI Parameter:

--hours
--tenant




🔧 Scheduling

 Celery Beat oder cron
 Aggregation alle 5–15 Minuten
 Late Data Reprocessing (letzte 24h)


💼 PHASE 5 – Business Logic
💶 Billing Engine

 BalanceSlot + SpotPrice join
 Kosten berechnen


💳 Tariff Integration

 Tariff Model nutzen
 Preisregeln implementieren


🧾 Invoice System

 Invoice Modell
 InvoiceLine
 Payment handling


📊 PHASE 6 – API Layer

 AggregatedReading API
 BalanceSlot API
 Dashboard endpoints
 Filter (tenant + time range)


⚡ PHASE 7 – Performance & Scale

 Compression Policy

SQLALTER TABLE metering_intervalreading SET (timescaledb.compress);SELECT add_compression_policy('metering_intervalreading', INTERVAL '30 days');Weitere Zeilen anzeigen

 Retention Policy
 Continuous Aggregates


📘 PHASE 8 – System Dokumentation
Architektur

 Systemübersicht
 Komponenten:

Django
TimescaleDB
(optional) Celery




Datenfluss
IntervalReading → Aggregation → Balance → Billing


Datenmodell

 Tabellen dokumentieren:

Tenant
Meter
IntervalReading
AggregatedReading
BalanceSlot
SpotPrice




Timescale

 Hypertables dokumentieren
 Partition Spalten erklären
 PK-Strategie dokumentieren


Business Logik

 OBIS Codes
 Aggregationslogik
 Balance Formeln


⚙️ PHASE 9 – Setup Guide
Setup

 Python / PostgreSQL / Timescale Versionen
 Repository klonen
 Virtualenv
 Requirements installieren


Datenbank

 DB erstellen
 Extension aktivieren:

SQLCREATE EXTENSION timescaledb;CREATE EXTENSION pgcrypto;Weitere Zeilen anzeigen

Migration
Shellpython manage.py migrateWeitere Zeilen anzeigen

Hypertables

 PK entfernen
 create_hypertable(...)
 Composite PK setzen


Testing

 Testdaten einfügen
 Aggregation testen
 Balance testen


📁 Projektstruktur (Empfehlung)
README.md
docs/
 ├── setup.md
 ├── architecture.md
 ├── data-model.md
 ├── timescale.md
 ├── aggregation.md
 └── billing.md


🎯 PRIORITY (EMPFOHLEN)
🔥 Jetzt:

OBIS Definition
Aggregation Procedure finalisieren
BalanceSlot Procedure


🚀 Danach:

Django Command
Scheduling


💼 Später:

Billing
API Erweiterung


✅ Aktueller Fortschritt





























BereichStatusInfrastruktur✅ 100%Datenmodell✅ 95%Timescale✅ 100%Business Logic🚧 30%Dokumentation❌ 0%

🚀 Ziel
Produktionsreife Time-Series Energy Plattform
→ skalierbar
→ performant
→ abrechnungsfähig



---

## ✅ Tipp
Speichere das z. B. als:


docs/todo.md
