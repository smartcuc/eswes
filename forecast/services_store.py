###########################
# forecast/services_store.py
###########################

from forecast.models import SolarForecast
from forecast.services_compare import build_hybrid_series
from forecast.services_ml import predict_next_24h_ml_for_tenant
from forecast.services_physics import predict_next_24h_physics_for_tenant


def _store_series(tenant, rows, source):
    rows = rows or []
    saved = 0

    for row in rows:
        SolarForecast.objects.update_or_create(
            tenant=tenant,
            timestamp=row["timestamp"],
            source=source,
            defaults={
                "forecast_kwh": row["forecast_kw"],
            },
        )
        saved += 1

    return saved


def save_all_forecasts_for_tenant(tenant):

    phys = predict_next_24h_physics_for_tenant(tenant) or []
    ml = predict_next_24h_ml_for_tenant(tenant) or []

    # ✅ kein Input → fertig
    if not ml and not phys:
        return {
            "status": "no_data",
            "counts": {"physics": 0, "ml": 0, "hybrid": 0},
        }

    # ✅ Hybrid sauber ableiten
    if not ml:
        hybrid = phys
    elif not phys:
        hybrid = ml
    else:
        hybrid = build_hybrid_series(ml, phys, use_dynamic_weight=True)

    saved_phys = _store_series(tenant, phys, "physics")
    saved_ml = _store_series(tenant, ml, "ml")
    saved_hybrid = _store_series(tenant, hybrid, "hybrid")

    return {
        "status": "ok",
        "counts": {
            "physics": saved_phys,
            "ml": saved_ml,
            "hybrid": saved_hybrid,
        },
    }
