######################
# metering/services.py
######################

from metering.models import (
    IntervalReading,
    AggregatedReading,
)
from metering.obis import OBIS_MAP


# ============================================================
# ✅ CORE: SCOPE FILTER (ZENTRAL!)
# ============================================================

def scope_filter(queryset, request):
    """
    Universeller Scope-Filter für ALLE Modelle.

    Unterstützt:
    - meter-basierte Models (IntervalReading, BalanceSlot, etc.)
    - direkte owner_user / owner_membership Models
    """

    model = queryset.model

    # =========================
    # ✅ COMMUNITY SCOPE
    # =========================
    if request.scope == "community":

        # 1. Modelle mit direktem tenant
        if hasattr(model, "tenant"):
            queryset = queryset.filter(tenant=request.tenant)

        # 2. Modelle mit owner_membership
        if hasattr(model, "owner_membership"):
            queryset = queryset.filter(owner_membership=request.member)

        # 3. Modelle via meter
        if hasattr(model, "meter"):
            queryset = queryset.filter(
                meter__tenant=request.tenant,
                meter__owner_membership=request.member,
            )

        return queryset

    # =========================
    # ✅ PERSONAL SCOPE
    # =========================
    else:

        # 1. direkte owner_user Models
        if hasattr(model, "owner_user"):
            queryset = queryset.filter(owner_user=request.user)

        # 2. direkte tenant Modelle
        if hasattr(model, "tenant"):
            queryset = queryset.filter(tenant__isnull=True)

        # 3. meter-basierte Modelle
        if hasattr(model, "meter"):
            queryset = queryset.filter(
                meter__tenant__isnull=True,
                meter__owner_user=request.user,
            )

        return queryset

# ============================================================
# ✅ BASIC READINGS
# ============================================================


def get_readings(request):
    qs = IntervalReading.objects.all()
    return scope_filter(qs, request)


def get_readings_for_meter(request, meter_id):
    qs = IntervalReading.objects.filter(meter_id=meter_id)
    return scope_filter(qs, request)


# ============================================================
# ✅ AGGREGATED DATA
# ============================================================


def get_aggregated(request, period_type=None):
    qs = AggregatedReading.objects.all()

    if period_type:
        qs = qs.filter(period_type=period_type)

    return scope_filter(qs, request)


def get_aggregated_for_meter(request, meter_id, period_type=None):
    qs = AggregatedReading.objects.filter(meter_id=meter_id)

    if period_type:
        qs = qs.filter(period_type=period_type)

    return scope_filter(qs, request)


# ============================================================
# ✅ CONSUMPTION vs GENERATION
# ============================================================


def get_consumption_readings(request):
    qs = IntervalReading.objects.filter(
        obis_code__startswith="1.8"
    )
    return scope_filter(qs, request)


def get_generation_readings(request):
    qs = IntervalReading.objects.filter(
        obis_code__startswith="2.8"
    )
    return scope_filter(qs, request)


def get_consumption_aggregated(request, period_type="day"):
    qs = AggregatedReading.objects.filter(
        obis_code__startswith="1.8",
        period_type=period_type,
    )
    return scope_filter(qs, request)


def get_generation_aggregated(request, period_type="day"):
    qs = AggregatedReading.objects.filter(
        obis_code__startswith="2.8",
        period_type=period_type,
    )
    return scope_filter(qs, request)


# ============================================================
# ✅ DASHBOARD SUMMARY
# ============================================================


def get_dashboard_summary(request):
    consumption = get_consumption_aggregated(request, "day")
    generation = get_generation_aggregated(request, "day")

    total_consumption = sum(c.value for c in consumption)
    total_generation = sum(g.value for g in generation)

    return {
        "total_consumption": total_consumption,
        "total_generation": total_generation,
    }


# ============================================================
# ✅ QUALITY / DEBUGGING
# ============================================================


def get_late_readings(request):
    qs = IntervalReading.objects.filter(is_late=True)
    return scope_filter(qs, request)


def get_duplicate_readings(request):
    qs = IntervalReading.objects.filter(is_duplicate=True)
    return scope_filter(qs, request)


# ============================================================
# ✅ OBIS METADATA
# ============================================================


def get_obis_info(obis_code):
    return OBIS_MAP.get(
        obis_code,
        {"name": "Unknown", "unit": "unknown", "type": "unknown"},
    )
