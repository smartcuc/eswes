##########################
# forecast/views_public.py
##########################

from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from metering.models import Tenant
from forecast.models import SolarForecast

VALID_SOURCES = {"ml", "physics", "hybrid"}


def _parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _ceil_to_next_hour(dt):
    dt = dt.replace(second=0, microsecond=0)

    if dt.minute == 0:
        return dt

    return (dt + timedelta(hours=1)).replace(minute=0)


def _get_public_tenant_or_error(request):
    tenant_id = request.GET.get("tenant")

    if not tenant_id:
        return None, Response(
            {"error": "tenant query parameter is required"},
            status=400,
        )

    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        return None, Response({"error": "tenant not found"}, status=404)

    if not getattr(tenant, "is_public", False):
        return None, Response({"error": "tenant not public"}, status=403)

    return tenant, None


# =========================================================
# PUBLIC FORECAST LIST
# GET /api/public/forecast/?tenant=<uuid>&source=hybrid&hours=24&limit=100&offset=0
# =========================================================
@api_view(["GET"])
@permission_classes([AllowAny])
def public_forecast_list(request):
    tenant, error = _get_public_tenant_or_error(request)
    if error:
        return error

    source = request.GET.get("source", "hybrid")
    hours = _parse_int(request.GET.get("hours"), 24)
    limit = _parse_int(request.GET.get("limit"), 100)
    offset = _parse_int(request.GET.get("offset"), 0)

    if source not in VALID_SOURCES:
        return Response(
            {
                "error": f"invalid source '{source}'",
                "valid_sources": sorted(VALID_SOURCES),
            },
            status=400,
        )

    now = _ceil_to_next_hour(timezone.now())
    end = now + timedelta(hours=hours)

    qs = SolarForecast.objects.filter(
        tenant=tenant,
        source=source,
        timestamp__gte=now,
        timestamp__lte=end,
    ).order_by("timestamp")

    total = qs.count()
    rows = list(qs[offset : offset + limit].values("timestamp", "forecast_kwh"))

    data = [
        {
            "timestamp": row["timestamp"],
            "value": float(row["forecast_kwh"]),
        }
        for row in rows
    ]

    return Response(
        {
            "tenant_id": str(tenant.id),
            "tenant_name": tenant.name,
            "source": source,
            "unit": "kWh",
            "hours": hours,
            "limit": limit,
            "offset": offset,
            "total": total,
            "data": data,
        }
    )


# =========================================================
# PUBLIC FORECAST RECOMMENDATION
# GET /api/public/forecast/recommendation/?tenant=<uuid>&source=hybrid&hours=24&window_hours=3
# =========================================================
@api_view(["GET"])
@permission_classes([AllowAny])
def public_forecast_recommendation(request):
    tenant, error = _get_public_tenant_or_error(request)
    if error:
        return error

    source = request.GET.get("source", "hybrid")
    hours = _parse_int(request.GET.get("hours"), 24)
    window_hours = _parse_int(request.GET.get("window_hours"), 3)

    if source not in VALID_SOURCES:
        return Response(
            {
                "error": f"invalid source '{source}'",
                "valid_sources": sorted(VALID_SOURCES),
            },
            status=400,
        )

    if window_hours < 1:
        return Response({"error": "window_hours must be >= 1"}, status=400)

    now = _ceil_to_next_hour(timezone.now())
    end = now + timedelta(hours=hours)

    rows = list(
        SolarForecast.objects.filter(
            tenant=tenant,
            source=source,
            timestamp__gte=now,
            timestamp__lte=end,
        )
        .order_by("timestamp")
        .values("timestamp", "forecast_kwh")
    )

    if not rows:
        return Response(
            {
                "tenant_id": str(tenant.id),
                "tenant_name": tenant.name,
                "source": source,
                "hours": hours,
                "window_hours": window_hours,
                "best_hour": None,
                "best_window": None,
                "message": "no forecast data available",
            }
        )

    best_hour_row = max(rows, key=lambda r: float(r["forecast_kwh"]))
    best_hour = {
        "timestamp": best_hour_row["timestamp"],
        "value": float(best_hour_row["forecast_kwh"]),
    }

    best_window = None
    message = None

    if len(rows) < window_hours:
        message = "not enough data for window"
    else:
        best_sum = None

        for i in range(len(rows) - window_hours + 1):
            window = rows[i : i + window_hours]
            window_sum = sum(float(r["forecast_kwh"]) for r in window)

            if best_sum is None or window_sum > best_sum:
                best_sum = window_sum
                best_window = {
                    "start": window[0]["timestamp"],
                    "end": window[-1]["timestamp"],
                    "hours": window_hours,
                    "total_kwh": window_sum,
                    "avg_kwh": window_sum / window_hours,
                }

    result = {
        "tenant_id": str(tenant.id),
        "tenant_name": tenant.name,
        "source": source,
        "hours": hours,
        "window_hours": window_hours,
        "best_hour": best_hour,
        "best_window": best_window,
    }

    if message:
        result["message"] = message

    return Response(result)
