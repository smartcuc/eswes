#######################
# core/api/dashboard.py
#######################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Sum, Min, Max
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from core.models import BalanceSlot
from core.permissions import HasTenantContext

from core.api.serializers_dashboard import DashboardSummarySerializer
from core.api.serializers_timeseries import DashboardTimeseriesResponseSerializer


# ============================================================
# ✅ SUMMARY
# ============================================================

class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated, HasTenantContext]

    def get(self, request):

        hours = int(request.query_params.get("hours", "24"))
        hours = max(1, min(hours, 24 * 90))

        since = timezone.now() - timedelta(hours=hours)

        qs = BalanceSlot.objects.filter(period_start__gte=since)

        # ✅ minimal safe tenant handling (optional)
        tenant = getattr(request, "tenant", None)
        if tenant:
            qs = qs.filter(tenant=tenant)

        agg = qs.aggregate(
            consumption_kwh=Sum("consumption_kwh"),
            generation_kwh=Sum("generation_kwh"),
            self_consumption_kwh=Sum("self_consumption_kwh"),
            grid_import_kwh=Sum("grid_import_kwh"),
            grid_export_kwh=Sum("grid_export_kwh"),
            period_start_from=Min("period_start"),
            period_start_to=Max("period_start"),
        )

        def z(x):
            return x if x is not None else Decimal("0.000")

        payload = {
            "period_start_from": agg["period_start_from"],
            "period_start_to": agg["period_start_to"],
            "consumption_kwh": z(agg["consumption_kwh"]),
            "generation_kwh": z(agg["generation_kwh"]),
            "self_consumption_kwh": z(agg["self_consumption_kwh"]),
            "grid_import_kwh": z(agg["grid_import_kwh"]),
            "grid_export_kwh": z(agg["grid_export_kwh"]),
            "rows": qs.count(),
        }

        return Response(DashboardSummarySerializer(payload).data)


# ============================================================
# ✅ TIMESERIES
# ============================================================

class DashboardTimeseriesView(APIView):
    permission_classes = [IsAuthenticated, HasTenantContext]

    def get(self, request):

        hours = request.query_params.get("hours")
        from_q = request.query_params.get("from")
        to_q = request.query_params.get("to")

        if from_q and to_q:
            from_ts = timezone.datetime.fromisoformat(from_q.replace("Z", "+00:00"))
            to_ts = timezone.datetime.fromisoformat(to_q.replace("Z", "+00:00"))

            if timezone.is_naive(from_ts):
                from_ts = timezone.make_aware(from_ts, timezone=timezone.utc)
            if timezone.is_naive(to_ts):
                to_ts = timezone.make_aware(to_ts, timezone=timezone.utc)
        else:
            h = int(hours or "24")
            h = max(1, min(h, 24 * 90))
            to_ts = timezone.now()
            from_ts = to_ts - timedelta(hours=h)

        qs = BalanceSlot.objects.filter(
            period_start__gte=from_ts,
            period_start__lte=to_ts,
        )

        tenant = getattr(request, "tenant", None)
        if tenant:
            qs = qs.filter(tenant=tenant)

        points = (
            qs.values("period_start")
            .annotate(
                consumption_kwh=Sum("consumption_kwh"),
                generation_kwh=Sum("generation_kwh"),
                self_consumption_kwh=Sum("self_consumption_kwh"),
                grid_import_kwh=Sum("grid_import_kwh"),
                grid_export_kwh=Sum("grid_export_kwh"),
            )
            .order_by("period_start")
        )

        def z(v):
            return v if v is not None else Decimal("0.000")

        series = [
            {
                "period_start": p["period_start"],
                "consumption_kwh": z(p["consumption_kwh"]),
                "generation_kwh": z(p["generation_kwh"]),
                "self_consumption_kwh": z(p["self_consumption_kwh"]),
                "grid_import_kwh": z(p["grid_import_kwh"]),
                "grid_export_kwh": z(p["grid_export_kwh"]),
            }
            for p in points
        ]

        payload = {
            "from": from_ts,
            "to": to_ts,
            "step": "15min",
            "rows": len(series),
            "series": series,
        }

        return Response(DashboardTimeseriesResponseSerializer(payload).data)
    