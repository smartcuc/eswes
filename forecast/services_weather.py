##############################
# forecast/services_weather.py
##############################

import requests
import logging

logger = logging.getLogger(__name__)


def get_weather_forecast(lat: float, lon: float):
    """
    Holt Tenant-Level Forecast-Wetterdaten von Open-Meteo.
    Standardisiert die Rückgabe auf:
    - timestamps
    - radiation
    - cloud_cover
    - temperature
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "shortwave_radiation,cloud_cover,temperature_2m",
        "forecast_days": 2,
        "timezone": "UTC",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    hourly = data["hourly"]

    cloud_cover = hourly.get("cloud_cover")
    if cloud_cover is None:
        # Fallback, falls API in deiner Region / Version noch cloudcover liefert
        cloud_cover = hourly.get("cloudcover", [])

    return {
        "timestamps": hourly["time"],
        "radiation": hourly.get("shortwave_radiation", []),
        "cloud_cover": cloud_cover,
        "temperature": hourly.get("temperature_2m", []),
    }
