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
from rest_framework.authentication import SessionAuthentication

from metering.models import BalanceSlot, Meter


class MyDashboardView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hours = int(request.query_params.get("hours", "24"))
        hours = max(1, min(hours, 24 * 90))

        tenant_id = request.query_params.get("tenant")
        since = timezone.now() - timedelta(hours=hours)

        qs = BalanceSlot.objects.filter(period_start__gte=since)

        if request.user.is_superuser:
            qs = BalanceSlot.objects.filter(period_start__gte=since)

        else:
            if tenant_id:
                meter_ids = Meter.objects.filter(tenant_id=tenant_id).values_list(
                    "id", flat=True
                )
            else:
                meter_ids = Meter.objects.filter(owner_user=request.user).values_list(
                    "id", flat=True
                )

            qs = qs.filter(meter_id__in=meter_ids)

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

        return Response(payload)


class MyDashboardTimeseriesView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hours = int(request.query_params.get("hours", "24"))
        hours = max(1, min(hours, 24 * 90))

        tenant_id = request.query_params.get("tenant")

        to_ts = timezone.now()
        from_ts = to_ts - timedelta(hours=hours)

        qs = BalanceSlot.objects.filter(
            period_start__gte=from_ts,
            period_start__lte=to_ts,
        )

        if request.user.is_superuser:
            # ✅ Admin sieht alles
            pass

        else:
            if tenant_id:
                meter_ids = Meter.objects.filter(tenant_id=tenant_id).values_list(
                    "id", flat=True
                )

            else:
                meter_ids = Meter.objects.filter(owner_user=request.user).values_list(
                    "id", flat=True
                )

            qs = qs.filter(meter_id__in=meter_ids)

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

        return Response(
            {
                "from": from_ts,
                "to": to_ts,
                "rows": len(series),
                "series": series,
            }
        )
