##################################
# forecast/services_ml_features.py
##################################

import math
import numpy as np


def _time_features(dt):
    """
    Zyklische Zeitfeatures: Stunde + Wochentag
    """
    hour = dt.hour
    weekday = dt.weekday()

    hour_sin = math.sin(2 * math.pi * hour / 24)
    hour_cos = math.cos(2 * math.pi * hour / 24)

    weekday_sin = math.sin(2 * math.pi * weekday / 7)
    weekday_cos = math.cos(2 * math.pi * weekday / 7)

    return [hour_sin, hour_cos, weekday_sin, weekday_cos]


def build_training_matrix(prod_rows, weather_map=None):
    """
    Baut Trainingsdaten ausschließlich aus der Zeitreihe.

    Erwartet:
    prod_rows = [
        {"timestamp": <datetime>, "value": <float>},
        ...
    ]

    Nutzt:
    - lag_1
    - lag_2
    - lag_3
    - lag_24
    - lag_48
    - rolling_4h
    - zyklische Zeitfeatures
    """
    X = []
    y = []

    if len(prod_rows) < 60:
        return np.array([]), np.array([])

    values = [float(r["value"]) for r in prod_rows]
    timestamps = [r["timestamp"] for r in prod_rows]

    for i in range(48, len(prod_rows)):
        ts = timestamps[i]

        lag_1 = values[i - 1]
        lag_2 = values[i - 2]
        lag_3 = values[i - 3]
        lag_24 = values[i - 24]
        lag_48 = values[i - 48]
        rolling_4h = sum(values[i - 4 : i]) / 4.0

        features = [
            lag_1,
            lag_2,
            lag_3,
            lag_24,
            lag_48,
            rolling_4h,
            *_time_features(ts),
        ]

        X.append(features)
        y.append(values[i])

    return np.array(X), np.array(y)


def build_recursive_feature_vector(history_values, future_dt):
    """
    Baut Feature-Vektor für rekursive Vorhersage.
    history_values = bereits bekannte + vorhergesagte Werte
    """
    lag_1 = history_values[-1]
    lag_2 = history_values[-2]
    lag_3 = history_values[-3]
    lag_24 = history_values[-24]
    lag_48 = history_values[-48]
    rolling_4h = sum(history_values[-4:]) / 4.0

    return np.array(
        [
            [
                lag_1,
                lag_2,
                lag_3,
                lag_24,
                lag_48,
                rolling_4h,
                *_time_features(future_dt),
            ]
        ]
    )
