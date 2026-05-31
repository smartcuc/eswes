##############################
# forecast/services_weather.py
##############################

import requests

DEFAULT_LAT = 50.9
DEFAULT_LON = 6.97


def resolve_forecast_coordinates(tenant):
    """
    Liefert Forecast-Koordinaten zurück.

    Priorität:
    1. tenant.latitude / tenant.longitude, falls vorhanden
    2. Fallback-Koordinaten (DEFAULT_LAT / DEFAULT_LON)

    Damit bleibt der Code stabil, auch wenn Tenant aktuell
    keine Geo-Felder im Modell hat.
    """
    lat = getattr(tenant, "latitude", None)
    lon = getattr(tenant, "longitude", None)

    if lat is None or lon is None:
        lat = DEFAULT_LAT
        lon = DEFAULT_LON

    return float(lat), float(lon)


def get_weather_forecast(lat, lon):
    """
    Holt stündliche Wetterdaten von Open-Meteo.

    Rückgabeformat:
    {
        "timestamps": [...],
        "radiation": [...],
        "temperature": [...],
        "cloud_cover": [...],
    }
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "shortwave_radiation,cloud_cover,temperature_2m",
        "forecast_days": 2,
        "timezone": "UTC",
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()
    hourly = data["hourly"]

    return {
        "timestamps": hourly.get("time", []),
        "radiation": hourly.get("shortwave_radiation", []),
        "temperature": hourly.get("temperature_2m", []),
        "cloud_cover": hourly.get("cloud_cover", []),
    }
