########################
# forecast/services_ml.py
########################

from pathlib import Path
from datetime import timedelta

import joblib
from sklearn.ensemble import RandomForestRegressor
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from metering.models import AggregatedReading
from forecast.models import TenantWeatherSnapshot
from forecast.services_ml_features import (
    build_training_matrix,
    build_recursive_feature_vector,
)
from forecast.services_weather import get_weather_forecast, resolve_forecast_coordinates

MODEL_DIR = Path(settings.BASE_DIR) / "ml_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def model_path_for_tenant(tenant_id):
    return MODEL_DIR / f"tenant_{tenant_id}.joblib"


def ceil_to_next_hour(dt):
    """
    Rundet einen Zeitpunkt auf die nächste volle Stunde auf.
    Wenn bereits volle Stunde, bleibt er auf dieser Stunde.
    """
    dt = dt.replace(second=0, microsecond=0)

    if dt.minute == 0:
        return dt

    return (dt + timedelta(hours=1)).replace(minute=0)


def _load_tenant_hourly_actuals(tenant):
    rows = list(
        AggregatedReading.objects.filter(
            tenant=tenant,
            period_type="hourly",
        )
        .values("period_start")
        .annotate(total_value=Sum("value"))
        .order_by("period_start")
    )

    if len(rows) < 2:
        return []

    result = []
    prev = None

    for row in rows:
        ts = row["period_start"]
        total_value = float(row["total_value"] or 0)

        if prev is None:
            prev = total_value
            continue

        diff = total_value - prev
        if diff < 0:
            diff = 0.0

        result.append(
            {
                "timestamp": ts,
                "value": diff,
            }
        )

        prev = total_value

    return result


def _load_historical_weather_map(tenant):
    rows = (
        TenantWeatherSnapshot.objects.filter(tenant=tenant)
        .order_by("ts")
        .values("ts", "temperature_c", "cloud_cover_pct", "shortwave_radiation_wm2")
    )

    return {
        row["ts"]: {
            "temperature_c": row["temperature_c"],
            "cloud_cover_pct": row["cloud_cover_pct"],
            "shortwave_radiation_wm2": row["shortwave_radiation_wm2"],
        }
        for row in rows
    }


def _load_future_weather_map(tenant):
    lat, lon = resolve_forecast_coordinates(tenant)
    weather = get_weather_forecast(lat, lon)

    result = {}

    for ts, rad, temp, clouds in zip(
        weather["timestamps"],
        weather["radiation"],
        weather["temperature"],
        weather["cloud_cover"],
    ):
        from datetime import datetime

        dt = datetime.fromisoformat(ts)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone=timezone.UTC)

        result[dt] = {
            "temperature_c": temp,
            "cloud_cover_pct": clouds,
            "shortwave_radiation_wm2": rad,
        }

    return result


def train_tenant_model(tenant):
    prod_rows = _load_tenant_hourly_actuals(tenant)
    weather_map = _load_historical_weather_map(tenant)

    X, y = build_training_matrix(prod_rows, weather_map)

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


def load_model(tenant_id):
    path = model_path_for_tenant(tenant_id)
    if not path.exists():
        return None
    return joblib.load(path)


def predict_next_24h_ml_for_tenant(tenant):
    model = load_model(tenant.id)

    if model is None:
        train_result = train_tenant_model(tenant)
        if train_result.get("status") != "trained":
            return None
        model = load_model(tenant.id)

    prod_rows = _load_tenant_hourly_actuals(tenant)
    if len(prod_rows) < 60:
        return None

    future_weather_map = _load_future_weather_map(tenant)

    history_values = [float(r["value"]) for r in prod_rows]
    history_timestamps = [r["timestamp"] for r in prod_rows]

    last_ts = history_timestamps[-1]
    start_ts = ceil_to_next_hour(last_ts)

    results = []

    for step in range(24):
        future_dt = start_ts + timedelta(hours=step)
        future_dt = future_dt.replace(minute=0, second=0, microsecond=0)

        weather = future_weather_map.get(future_dt)

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
