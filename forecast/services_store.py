###########################
# forecast/services_store.py
###########################

from forecast.models import SolarForecast
from forecast.services_compare import build_hybrid_series
from producer.models import GeneratorString
from forecast.services_physics import predict_next_24h_physics_for_generator_string


def _store_series(generator_string, rows, source):
    rows = rows or []
    saved = 0

    for row in rows:
        SolarForecast.objects.update_or_create(
            generator_string=generator_string,
            timestamp=row["timestamp"],
            source=source,
            defaults={
                "forecast_kwh": row["forecast_kw"],
            },
        )
        saved += 1

    return saved


def save_all_forecasts_for_generator_string(generator_string):

    phys = (
        predict_next_24h_physics_for_generator_string(
            generator_string,
        )
        or []
    )

    ml = []

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

    saved_phys = _store_series(
        generator_string,
        phys,
        "physics",
    )

    saved_ml = _store_series(
        generator_string,
        ml,
        "ml",
    )

    saved_hybrid = _store_series(
        generator_string,
        hybrid,
        "hybrid",
    )

    return {
        "status": "ok",
        "counts": {
            "physics": saved_phys,
            "ml": saved_ml,
            "hybrid": saved_hybrid,
        },
    }
