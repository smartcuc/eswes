#########################
# forecast/services_ml.py
#########################

from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestRegressor
from django.conf import settings

from forecast.models import TenantWeatherSnapshot
from forecast.services_ml_features import (
    build_training_matrix_with_weather,
    build_recursive_feature_vector,
)
from forecast.services_series import get_tenant_hourly_actuals
from forecast.services_weather import get_weather_forecast

MODEL_DIR = Path(settings.BASE_DIR) / "ml_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def model_path_for_tenant(tenant_id):
    return MODEL_DIR / f"solar_tenant_{tenant_id}.joblib"


def train_tenant_model(tenant):
    prod_rows = get_tenant_hourly_actuals(tenant)

    weather_rows = list(
        TenantWeatherSnapshot.objects.filter(tenant=tenant)
        .order_by("ts")
        .values("ts", "temperature_c", "cloud_cover_pct", "shortwave_radiation_wm2")
    )

    weather_map = {
        row["ts"]: {
            "temperature_c": row["temperature_c"],
            "cloud_cover_pct": row["cloud_cover_pct"],
            "shortwave_radiation_wm2": row["shortwave_radiation_wm2"],
        }
        for row in weather_rows
    }

    X, y = build_training_matrix_with_weather(prod_rows, weather_map)

    if len(X) == 0:
        return {
            "status": "not_enough_data",
            "tenant_id": str(tenant.id),
        }

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X, y)

    path = model_path_for_tenant(tenant.id)
    joblib.dump(model, path)

    return {
        "status": "trained",
        "tenant_id": str(tenant.id),
        "samples": len(X),
        "model_path": str(path),
    }


def load_tenant_model(tenant_id):
    path = model_path_for_tenant(tenant_id)
    if not path.exists():
        return None
    return joblib.load(path)


def predict_next_24h_ml_for_tenant(tenant):
    model = load_tenant_model(tenant.id)
    if model is None:
        return None

    if tenant.latitude is None or tenant.longitude is None:
        return None

    prod_rows = get_tenant_hourly_actuals(tenant)
    if len(prod_rows) < 60:
        return None

    history_values = [float(r["value"]) for r in prod_rows]
    history_timestamps = [r["timestamp"] for r in prod_rows]

    # echte Forecast-Wetterdaten für die Zukunft
    weather_forecast = get_weather_forecast(tenant.latitude, tenant.longitude)
    weather_future_map = {}

    for ts, rad, temp, clouds in zip(
        weather_forecast["timestamps"],
        weather_forecast["radiation"],
        weather_forecast["temperature"],
        weather_forecast["cloud_cover"],
    ):
        weather_future_map[ts] = {
            "temperature_c": temp,
            "cloud_cover_pct": clouds,
            "shortwave_radiation_wm2": rad,
        }

    last_ts = history_timestamps[-1]
    delta = history_timestamps[-1] - history_timestamps[-2]

    results = []

    for step in range(1, 25):
        future_dt = last_ts + step * delta
        future_key = future_dt.isoformat(timespec="minutes")
        weather = weather_future_map.get(
            future_key,
            {"temperature_c": 20, "cloud_cover_pct": 0, "shortwave_radiation_wm2": 0},
        )

        X_future = build_recursive_feature_vector(
            history_values=history_values,
            future_dt=future_dt,
            weather=weather,
        )

        pred = float(model.predict(X_future)[0])
        pred = max(0.0, pred)

        history_values.append(pred)

        results.append(
            {
                "timestamp": future_dt,
                "forecast_kw": pred,
            }
        )

    return results
