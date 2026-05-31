# forecast/services_breakdown.py

from collections import defaultdict
from django.db.models import Sum
from metering.models import AggregatedReading
from forecast.models import SolarForecast


def compute_meter_weights(tenant):
    """
    Berechnet den Anteil jedes Meters am Gesamtverbrauch.
    """
    rows = (
        AggregatedReading.objects.filter(tenant=tenant)
        .values("meter_id")
        .annotate(total=Sum("value"))
    )

    total_sum = sum(float(r["total"] or 0) for r in rows)

    weights = {}
    if total_sum == 0:
        return {}

    for r in rows:
        weights[r["meter_id"]] = float(r["total"]) / total_sum

    return weights


def breakdown_forecast_to_meters(tenant, source="hybrid"):
    """
    Verteilt Tenant-Forecast auf Meter.
    """

    weights = compute_meter_weights(tenant)

    if not weights:
        return {"status": "no_weights"}

    forecasts = SolarForecast.objects.filter(
        tenant=tenant,
        source=source,
    ).order_by("timestamp")

    results = []

    for f in forecasts:
        for meter_id, weight in weights.items():

            results.append(
                {
                    "meter_id": meter_id,
                    "timestamp": f.timestamp,
                    "forecast_kwh": float(f.forecast_kwh) * weight,
                    "source": source,
                }
            )

    return {
        "status": "ok",
        "rows": len(results),
        "meters": len(weights),
    }
