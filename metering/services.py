#
#
#

from metering.models import (
    IntervalReading,
    AggregatedReading,
    Meter,
)
from metering.obis import OBIS_MAP

# ============================================================
# ✅ BASIC: USER SCOPED READINGS
# ============================================================


def get_readings_for_user(user):
    """
    Alle Rohdaten für den User (tenant-isoliert)
    """
    return IntervalReading.objects.filter(tenant=user.tenant)


def get_readings_for_member(user, member_id):
    """
    Rohdaten für ein bestimmtes Mitglied
    """
    return IntervalReading.objects.filter(
        tenant=user.tenant, meter__member_id=member_id
    )


def get_readings_for_meter(user, meter_id):
    """
    Rohdaten für einen bestimmten Zähler
    """
    return IntervalReading.objects.filter(tenant=user.tenant, meter_id=meter_id)


# ============================================================
# ✅ AGGREGATED DATA
# ============================================================


def get_aggregated_for_user(user, period_type=None):
    """
    Aggregierte Daten für Tenant
    period_type: hour/day/week/month/year
    """
    qs = AggregatedReading.objects.filter(tenant=user.tenant)

    if period_type:
        qs = qs.filter(period_type=period_type)

    return qs


def get_aggregated_for_member(user, member_id, period_type=None):
    """
    Aggregierte Daten für ein Mitglied
    """
    qs = AggregatedReading.objects.filter(tenant=user.tenant, member_id=member_id)

    if period_type:
        qs = qs.filter(period_type=period_type)

    return qs


def get_aggregated_for_meter(user, meter_id, period_type=None):
    """
    Aggregierte Daten für einzelnen Zähler
    """
    qs = AggregatedReading.objects.filter(tenant=user.tenant, meter_id=meter_id)

    if period_type:
        qs = qs.filter(period_type=period_type)

    return qs


# ============================================================
# ✅ CONSUMPTION vs GENERATION (OBIS)
# ============================================================


def get_consumption_readings(user):
    """
    Nur Verbrauch (1.8.x)
    """
    return IntervalReading.objects.filter(
        tenant=user.tenant, obis_code__startswith="1.8"
    )


def get_generation_readings(user):
    """
    Nur Einspeisung (2.8.x)
    """
    return IntervalReading.objects.filter(
        tenant=user.tenant, obis_code__startswith="2.8"
    )


def get_consumption_aggregated(user, period_type="day"):
    """
    Aggregierter Verbrauch
    """
    return AggregatedReading.objects.filter(
        tenant=user.tenant, period_type=period_type, obis_code__startswith="1.8"
    )


def get_generation_aggregated(user, period_type="day"):
    """
    Aggregierte Einspeisung
    """
    return AggregatedReading.objects.filter(
        tenant=user.tenant, period_type=period_type, obis_code__startswith="2.8"
    )


# ============================================================
# ✅ DASHBOARD HELPERS
# ============================================================


def get_dashboard_summary(user):
    """
    Kurze Übersicht:
    - Gesamtverbrauch
    - Gesamteinspeisung
    """

    consumption = get_consumption_aggregated(user, "day")
    generation = get_generation_aggregated(user, "day")

    total_consumption = sum([c.value for c in consumption])
    total_generation = sum([g.value for g in generation])

    return {
        "total_consumption": total_consumption,
        "total_generation": total_generation,
    }


# ============================================================
# ✅ QUALITY / DEBUGGING
# ============================================================


def get_late_readings(user):
    return IntervalReading.objects.filter(tenant=user.tenant, is_late=True)


def get_duplicate_readings(user):
    return IntervalReading.objects.filter(tenant=user.tenant, is_duplicate=True)


# ============================================================
# ✅ OPTIONAL: OBIS METADATA
# ============================================================


def get_obis_info(obis_code):
    """
    Mapping für UI / Anzeige
    """
    return OBIS_MAP.get(
        obis_code, {"name": "Unknown", "unit": "unknown", "type": "unknown"}
    )
