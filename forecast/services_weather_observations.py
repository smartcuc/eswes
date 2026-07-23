###########################################
# forecast/services_weather_observations.py
###########################################

from forecast.models import WeatherObservation
from datetime import timezone
from django.utils.dateparse import parse_datetime
import logging

from math import radians
from math import sin
from math import cos
from math import sqrt
from math import atan2

from forecast.providers.sensor_community import (
    fetch_nearby_observations,
)


logger = logging.getLogger(__name__)

def distance_km(
    lat1,
    lon1,
    lat2,
    lon2,
):

    r = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return r * c


def store_sensor_community_observations(
    lat,
    lon,
):

    rows = fetch_nearby_observations(
        lat=lat,
        lon=lon,
    )

    logger.info(
        "SensorCommunity rows=%s",
        len(rows),
    )

    count = 0

    for row in rows:

        location = row.get("location")

        if not location:
            continue

        try:

            obs_lat = float(location["latitude"])
            obs_lon = float(location["longitude"])

            distance = distance_km(
                lat,
                lon,
                obs_lat,
                obs_lon,
            )

            if distance > 25:
                continue

        except Exception:
            continue

        timestamp = parse_datetime(row.get("timestamp"))

        if timestamp is None:
            continue

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        sensor = row.get("sensor") or {}

        station_id = str(sensor.get("id")) if sensor.get("id") else None

        temperature_c = None
        humidity_pct = None

        for item in row.get(
            "sensordatavalues",
            [],
        ):

            value_type = item.get("value_type")

            raw_value = item.get("value")

            try:
                numeric_value = float(raw_value)
            except Exception:
                continue

            if value_type == "temperature":
                temperature_c = numeric_value

            elif value_type == "humidity":
                humidity_pct = numeric_value

        if (
            temperature_c is None
            and humidity_pct is None
        ):

            continue

        obj, created = WeatherObservation.objects.update_or_create(
            provider="sensor_community",
            station_id=station_id,
            timestamp=timestamp,
            defaults={
                "latitude": obs_lat,
                "longitude": obs_lon,
                "temperature_c": temperature_c,
                "humidity_pct": humidity_pct,
            },
        )

        if created:
            count += 1

    return {
        "saved": count,
    }

