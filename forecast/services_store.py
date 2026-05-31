############################
# forecast/services_store.py
############################

from forecast.models import SolarForecast
from forecast.services_solar_forecast import tenant_solar_forecast_24h
from forecast.services_ml import predict_next_24h_ml_for_tenant
from forecast.services_compare import build_hybrid_series


def save_all_forecasts_for_tenant(tenant):
    """
    Speichert Physics, ML und Hybrid Forecasts für einen Tenant.
    """

    # ✅ berechnen
    phys = tenant_solar_forecast_24h(tenant)
    ml = predict_next_24h_ml_for_tenant(tenant)
    hybrid = build_hybrid_series(ml, phys, use_dynamic_weight=True)

    # ✅ speichern
    _save_series(tenant, phys, source="physics")
    _save_series(tenant, ml, source="ml")
    _save_series(tenant, hybrid, source="hybrid")

    return {
        "status": "ok",
        "counts": {
            "physics": len(phys),
            "ml": len(ml),
            "hybrid": len(hybrid),
        },
    }


def _save_series(tenant, series, source):
    for entry in series:
        SolarForecast.objects.update_or_create(
            tenant=tenant,
            timestamp=entry["timestamp"],
            source=source,
            defaults={
                "forecast_kwh": entry["forecast_kw"],
            },
        )
