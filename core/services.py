##################
# core/services.py
##################

from core.models import IntervalReading, AggregatedReading, BalanceSlot


# ✅ --------------------------------------
# BASIC FILTERS (OHNE SCOPE!)
# Scope macht jetzt dein ViewSet
# ✅ --------------------------------------

def get_readings(meter_id=None):
    qs = IntervalReading.objects.all()
    if meter_id:
        qs = qs.filter(meter_id=meter_id)
    return qs


def get_consumption_readings():
    return IntervalReading.objects.filter(obis_code__startswith="1.8")


def get_generation_readings():
    return IntervalReading.objects.filter(obis_code__startswith="2.8")


# ✅ --------------------------------------
# AGGREGATED
# ✅ --------------------------------------

def get_aggregated(meter_id=None):
    qs = AggregatedReading.objects.all()
    if meter_id:
        qs = qs.filter(meter_id=meter_id)
    return qs


# ✅ --------------------------------------
# KPI (JETZT WICHTIG)
# ✅ --------------------------------------

def get_dashboard_summary():
    slots = BalanceSlot.objects.all()

    total_consumption = sum(s.consumption_kwh for s in slots)
    total_generation = sum(s.generation_kwh for s in slots)

    return {
        "total_consumption": total_consumption,
        "total_generation": total_generation,
    }


# ✅ --------------------------------------
# DEBUG
# ✅ --------------------------------------

def get_late_readings():
    return IntervalReading.objects.filter(is_late=True)


def get_duplicate_readings():
    return IntervalReading.objects.filter(is_duplicate=True)