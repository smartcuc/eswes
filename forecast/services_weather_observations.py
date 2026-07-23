###########################################
# forecast/services_weather_observations.py
###########################################

from forecast.models import WeatherObservation

from forecast.providers.sensor_community import (
    fetch_nearby_observations,
)


def store_sensor_community_observations(
    lat,
    lon,
):

    rows = fetch_nearby_observations(
        lat=lat,
        lon=lon,
    )

    count = 0

    for row in rows:

        location = row.get("location")

        if not location:
            continue

        try:

            obs_lat = float(location["latitude"])

            obs_lon = float(location["longitude"])

        except Exception:
            continue

        WeatherObservation.objects.create(
            latitude=obs_lat,
            longitude=obs_lon,
            provider="sensor_community",
        )

        count += 1

    return {
        "saved": count,
    }
