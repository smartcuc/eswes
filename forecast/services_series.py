#############################
# forecast/services_series.py
#############################

from django.db.models import Sum

from core.models import AggregatedReading

def get_tenant_hourly_actuals(tenant, start=None, end=None):
    """
    Aggregiert reale Tenant-Produktion stündlich.
    Nutzt period_start als Zeitfeld.
    """
    qs = AggregatedReading.objects.filter(
        tenant=tenant,
        period_type="hourly",
    )

    if start is not None:
        qs = qs.filter(period_start__gte=start)

    if end is not None:
        qs = qs.filter(period_start__lt=end)

    rows = (
        qs.values("period_start")
        .annotate(total_value=Sum("value"))
        .order_by("period_start")
    )

    return [
        {
            "timestamp": row["period_start"],
            "value": float(row["total_value"]),
        }
        for row in rows
    ]


def estimate_tenant_capacity_kw(tenant, days=30):
    """
    Vereinfachte Schätzung einer Tenant-weiten "Kapazität" aus historischen Istwerten.
    Zweck: Physikmodell in dimensional sinnvolle Größenordnung bringen.
    """
    rows = get_tenant_hourly_actuals(tenant)
    if not rows:
        return 0.0

    values = [r["value"] for r in rows]
    return max(values) if values else 0.0
