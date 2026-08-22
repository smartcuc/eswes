##################################
# forecast/services_ml_features.py
##################################

import math
import numpy as np
from datetime import timedelta


def _time_features(dt):
    """
    Zyklische Zeitfeatures:
    - Stunde (24h)
    - Monat (12m)
    - Wochentag (7d)
    """
    hour = dt.hour
    month = dt.month
    weekday = dt.weekday()

    hour_sin = math.sin(2 * math.pi * hour / 24)
    hour_cos = math.cos(2 * math.pi * hour / 24)

    month_sin = math.sin(2 * math.pi * (month - 1) / 12)
    month_cos = math.cos(2 * math.pi * (month - 1) / 12)

    weekday_sin = math.sin(2 * math.pi * weekday / 7)
    weekday_cos = math.cos(2 * math.pi * weekday / 7)

    return [hour_sin, hour_cos, month_sin, month_cos, weekday_sin, weekday_cos]


def build_solar_feature_vector(
    dt,
    weather=None,
    physics_kw=0.0,
    lag_24=0.0,
    lag_48=0.0,
    lag_1=0.0,
):
    """
    Baut einen standardisierten Feature-Vektor für Solar-Prognose:
    [
        physics_kw,
        radiation_wm2,
        temperature_c,
        cloud_cover_pct,
        lag_24,
        lag_48,
        lag_1,
        hour_sin, hour_cos,
        month_sin, month_cos,
        weekday_sin, weekday_cos
    ]
    """
    weather = weather or {}
    radiation = float(weather.get("shortwave_radiation_wm2") or 0.0)
    temperature = float(weather.get("temperature_c") or 15.0)
    cloud_cover = float(weather.get("cloud_cover_pct") or 0.0)
    phys = float(physics_kw or 0.0)

    time_feats = _time_features(dt)

    return [
        phys,
        radiation,
        temperature,
        cloud_cover,
        float(lag_24 or 0.0),
        float(lag_48 or 0.0),
        float(lag_1 or 0.0),
        *time_feats,
    ]


def build_generator_training_matrix(
    prod_rows,
    weather_map=None,
    physics_map=None,
):
    """
    Baut Trainingsmatrix (X, y) aus historischen Erzeugungsdaten und Wetterdaten.

    prod_rows = [
        {"timestamp": <datetime>, "value": <float kW oder kWh>},
        ...
    ]
    """
    weather_map = weather_map or {}
    physics_map = physics_map or {}

    if len(prod_rows) < 24:
        return np.array([]), np.array([])

    value_by_ts = {
        r["timestamp"].replace(minute=0, second=0, microsecond=0): float(r["value"] or 0.0)
        for r in prod_rows
    }

    X = []
    y = []

    sorted_ts = sorted(value_by_ts.keys())

    for ts in sorted_ts:
        actual_val = value_by_ts[ts]

        # Wetter & Physik für diesen Zeitpunkt
        weather = weather_map.get(ts, {})
        phys_val = physics_map.get(ts, 0.0)

        # Lags
        lag_24 = value_by_ts.get(ts - timedelta(hours=24), actual_val)
        lag_48 = value_by_ts.get(ts - timedelta(hours=48), lag_24)
        lag_1 = value_by_ts.get(ts - timedelta(hours=1), actual_val)

        feat = build_solar_feature_vector(
            dt=ts,
            weather=weather,
            physics_kw=phys_val,
            lag_24=lag_24,
            lag_48=lag_48,
            lag_1=lag_1,
        )

        X.append(feat)
        y.append(actual_val)

    return np.array(X), np.array(y)


# Legacy-Kompatibilität für bestehende Aufrufe
def build_training_matrix(prod_rows, weather_map=None):
    return build_generator_training_matrix(prod_rows, weather_map)


def build_recursive_feature_vector(history_values, future_dt, weather=None, physics_kw=0.0):
    lag_1 = history_values[-1] if history_values else 0.0
    lag_24 = history_values[-24] if len(history_values) >= 24 else lag_1
    lag_48 = history_values[-48] if len(history_values) >= 48 else lag_24

    feat = build_solar_feature_vector(
        dt=future_dt,
        weather=weather,
        physics_kw=physics_kw,
        lag_24=lag_24,
        lag_48=lag_48,
        lag_1=lag_1,
    )
    return np.array([feat])
