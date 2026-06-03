# Architecture Overview

## Core Pipeline

IntervalReading → AggregatedReading → BalanceSlot → UserBalanceSlot

## Layers

- Metering: Raw data + aggregation
- Energy: balance calculation
- Billing: user allocation
- Market: pricing data
- Forecast: weather + solar prediction

## Principle

- Meter-first design
- Slot-based time modelS