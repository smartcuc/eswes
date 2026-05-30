# Datenbank (Timescale Setup)

Dieses Kapitel beschreibt das komplette Datenbank-Setup:

- Schema (Tabellen & Beziehungen)
- Timescale Konfiguration (Hypertables)
- Datenpipeline (Aggregation + Balance)
- Prüfskripte

## Übersicht

Meter → IntervalReading → Aggregation → BalanceSlot

## Ziel

- reproduzierbare Datenbasis
- stabile Verarbeitung
- überprüfbare Konsistenz