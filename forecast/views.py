###################
# forecast/views.py
###################


from django.utils import timezone
from datetime import timedelta

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from forecast.models import SolarForecast
from metering.models import AggregatedReading


# =========================================================
# METER FORECAST
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def meter_forecast(request, meter_id):

    qs = SolarForecast.objects.filter(meter_id=meter_id).order_by("timestamp")[:96]

    data = [
        {
            "timestamp": row.timestamp,
            "forecast_kw": float(row.forecast_kw),
        }
        for row in qs
    ]

    return Response(data)


# =========================================================
# METER FORECAST vs ACTUAL
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def meter_forecast_vs_actual(request, meter_id):

    now = timezone.now()
    start = now - timedelta(hours=24)

    forecast_qs = SolarForecast.objects.filter(
        meter_id=meter_id,
        timestamp__gte=start,
    )

    actual_qs = AggregatedReading.objects.filter(
        meter_id=meter_id,
        period_type="hourly",
        timestamp__gte=start,
    )

    # ✅ schneller Lookup
    actual_map = {a.timestamp: a.value for a in actual_qs}

    data = []

    for f in forecast_qs.order_by("timestamp"):
        actual = actual_map.get(f.timestamp)

        data.append(
            {
                "timestamp": f.timestamp,
                "forecast_kw": float(f.forecast_kw),
                "actual_kw": float(actual) if actual is not None else None,
            }
        )

    return Response(data)


# =========================================================
# USER FORECAST (aggregiert über alle Meter)
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_forecast(request):

    meters = request.user.meters.all()

    qs = SolarForecast.objects.filter(meter__in=meters)

    result = {}

    for row in qs:
        key = row.timestamp
        result[key] = result.get(key, 0) + float(row.forecast_kw)

    return Response(
        [{"timestamp": k, "forecast_kw": v} for k, v in sorted(result.items())]
    )


# =========================================================
# TENANT FORECAST
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def tenant_forecast(request):

    tenant = request.user.tenant

    if not tenant:
        return Response({"error": "no tenant"}, status=400)

    qs = SolarForecast.objects.filter(tenant=tenant)

    result = {}

    for row in qs:
        key = row.timestamp
        result[key] = result.get(key, 0) + float(row.forecast_kw)

    return Response(
        [{"timestamp": k, "forecast_kw": v} for k, v in sorted(result.items())]
    )


# =========================================================
# GLOBAL FORECAST (ADMIN)
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def global_forecast(request):

    if not request.user.is_staff:
        return Response({"error": "not allowed"}, status=403)

    qs = SolarForecast.objects.all()

    result = {}

    for row in qs:
        key = row.timestamp
        result[key] = result.get(key, 0) + float(row.forecast_kw)

    return Response(
        [{"timestamp": k, "forecast_kw": v} for k, v in sorted(result.items())]
    )
