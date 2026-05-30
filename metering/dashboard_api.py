###########################
# metering/dashboard_api.py
###########################

from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, Min, Max
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from metering.models import (
    BalanceSlot,
)  # dein Django-Model mit db_table="metering_balanceslot"
from metering.serializers_dashboard import DashboardSummarySerializer
from metering.serializers_dashboard_timeseries import (
    DashboardTimeseriesResponseSerializer,
)

# Import dein Model (anpassen falls es in anderer App liegt)
from metering.models import Meter  # owner_user / tenant erwartet

# BalanceSlot ist in deiner DB als metering_balanceslot; Model muss existieren:
# from billing.models import BalanceSlot  # <- falls BalanceSlot bei dir in billing liegt

# Wenn BalanceSlot bei dir in metering liegt, ändere auf:
from metering.models import BalanceSlot


class MyDashboardView(APIView):
    """
    GET /api/dashboard/me/?hours=24[&tenant=<uuid>]
    - Standalone: filtert über Meter.owner_user == request.user
    - Tenant (optional): filtert über Meter.tenant_id == tenant
    Quelle: BalanceSlot (Business Layer)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        hours = int(request.query_params.get("hours", "24"))
        hours = max(1, min(hours, 24 * 90))  # 1h .. 90 Tage

        tenant_id = request.query_params.get("tenant")  # optional
        since = timezone.now() - timedelta(hours=hours)

        qs = BalanceSlot.objects.filter(period_start__gte=since)

        tenant_id = request.query_params.get("tenant")

        if tenant_id:
            qs = qs.filter(meter__tenant_id=tenant_id)

        elif request.user.is_authenticated:
            qs = qs.filter(meter__owner_user=request.user)

        #        qs = BalanceSlot.objects.filter(period_start__gte=since)
        #
        #        # Standalone: alle Meter des Users
        #        # Tenant: alle Meter im Tenant
        #        if tenant_id:
        #            qs = qs.filter(meter__tenant_id=tenant_id)
        #        else:
        #            qs = qs.filter(meter__owner_user=request.user)
        #

        agg = qs.aggregate(
            consumption_kwh=Sum("consumption_kwh"),
            generation_kwh=Sum("generation_kwh"),
            self_consumption_kwh=Sum("self_consumption_kwh"),
            grid_import_kwh=Sum("grid_import_kwh"),
            grid_export_kwh=Sum("grid_export_kwh"),
            period_start_from=Min("period_start"),
            period_start_to=Max("period_start"),
        )

        # Nulls -> 0
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

        data = DashboardSummarySerializer(payload).data
        return Response(data)


class MyDashboardTimeseriesView(APIView):
    """
    GET /api/dashboard/me/timeseries/?hours=24
    Optional:
      - &tenant=<TENANT_UUID>
      - oder &from=...&to=...
    Gibt eine Zeitreihe zurück (chart-ready).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # --- Zeitfenster bestimmen ---
        hours = request.query_params.get("hours")
        from_q = request.query_params.get("from")
        to_q = request.query_params.get("to")

        if from_q and to_q:
            # ISO8601 parsing über Django helper
            from_ts = timezone.datetime.fromisoformat(from_q.replace("Z", "+00:00"))
            to_ts = timezone.datetime.fromisoformat(to_q.replace("Z", "+00:00"))
            if timezone.is_naive(from_ts):
                from_ts = timezone.make_aware(from_ts, timezone=timezone.utc)
            if timezone.is_naive(to_ts):
                to_ts = timezone.make_aware(to_ts, timezone=timezone.utc)
        else:
            h = int(hours or "24")
            h = max(1, min(h, 24 * 90))  # 1h .. 90 Tage
            to_ts = timezone.now()
            from_ts = to_ts - timedelta(hours=h)

        tenant_id = request.query_params.get("tenant")

        # --- Base Query ---
        qs = BalanceSlot.objects.filter(
            period_start__gte=from_ts, period_start__lte=to_ts
        )

        # Tenant vs Standalone
        if tenant_id:
            qs = qs.filter(meter__tenant_id=tenant_id)
        else:
            qs = qs.filter(meter__owner_user=request.user)

        # --- Zeitreihe aggregieren über alle Meter des Users/Tenants ---
        # Group by period_start und summiere die KPIs
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

        # None -> 0
        def z(v):
            return v if v is not None else Decimal("0.000")

        series = []
        for p in points:
            series.append(
                {
                    "period_start": p["period_start"],
                    "consumption_kwh": z(p["consumption_kwh"]),
                    "generation_kwh": z(p["generation_kwh"]),
                    "self_consumption_kwh": z(p["self_consumption_kwh"]),
                    "grid_import_kwh": z(p["grid_import_kwh"]),
                    "grid_export_kwh": z(p["grid_export_kwh"]),
                }
            )

        payload = {
            "from": from_ts,
            "to": to_ts,
            "step": "15min",  # aktuell: BalanceSlots sind 15-min Slots
            "rows": len(series),
            "series": series,
        }

        return Response(DashboardTimeseriesResponseSerializer(payload).data)
