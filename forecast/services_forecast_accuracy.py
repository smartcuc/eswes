from datetime import datetime, time
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from devices.models import Home
from forecast.models import WeatherForecast
from forecast.services_weather_history import fetch_historical_weather

DEFAULT_LAT = getattr(settings, "DEFAULT_WEATHER_LAT", 50.9)
DEFAULT_LON = getattr(settings, "DEFAULT_WEATHER_LON", 6.97)


def _resolve_home_and_coords(target):
    home = None
    if isinstance(target, Home):
        home = target
    elif target is not None:
        home = Home.objects.filter(user__memberships__tenant=target).first()

    if not home:
        home = Home.objects.first()

    lat = (
        getattr(home, "latitude", None)
        or getattr(target, "latitude", None)
        or DEFAULT_LAT
    )
    lon = (
        getattr(home, "longitude", None)
        or getattr(target, "longitude", None)
        or DEFAULT_LON
    )

    return home, float(lat), float(lon)


def calculate_forecast_accuracy(target, start_date, end_date):
    home, lat, lon = _resolve_home_and_coords(target)

    start_dt = timezone.make_aware(
        datetime.combine(start_date, time.min), timezone.utc
    )
    end_dt = timezone.make_aware(
        datetime.combine(end_date, time.max), timezone.utc
    )

    filter_kwargs = {
        "ts__gte": start_dt,
        "ts__lte": end_dt,
    }
    if home:
        filter_kwargs["home"] = home

    forecast_rows = {
        row.ts.replace(minute=0, second=0, microsecond=0): row
        for row in WeatherForecast.objects.filter(**filter_kwargs)
    }

    if not forecast_rows:
        return {"status": "error", "reason": "no-forecast-data-in-range"}

    try:
        payload = fetch_historical_weather(
            lat,
            lon,
            start_date,
            end_date,
        )
    except Exception as e:
        return {"status": "error", "reason": f"history-fetch-failed: {e}"}

    times = payload.get("time", [])
    actual_temp = payload.get("temperature_2m", [])
    actual_cloud = payload.get("cloud_cover", [])
    actual_rad = payload.get("shortwave_radiation", [])

    compared = 0
    temperature_error = 0.0
    cloud_error = 0.0
    radiation_error = 0.0

    for i in range(len(times)):
        ts = parse_datetime(times[i])
        if ts is None:
            continue

        if timezone.is_naive(ts):
            ts = timezone.make_aware(ts, timezone.utc)

        ts = ts.replace(minute=0, second=0, microsecond=0)

        if ts not in forecast_rows:
            continue

        f = forecast_rows[ts]

        if f.temperature_c is not None and i < len(actual_temp) and actual_temp[i] is not None:
            temperature_error += abs(float(f.temperature_c) - float(actual_temp[i]))

        if f.cloud_cover_pct is not None and i < len(actual_cloud) and actual_cloud[i] is not None:
            cloud_error += abs(float(f.cloud_cover_pct) - float(actual_cloud[i]))

        if f.shortwave_radiation_wm2 is not None and i < len(actual_rad) and actual_rad[i] is not None:
            radiation_error += abs(float(f.shortwave_radiation_wm2) - float(actual_rad[i]))

        compared += 1

    if compared == 0:
        return {"status": "error", "reason": "no-overlap-after-alignment"}

    return {
        "status": "ok",
        "points_compared": compared,
        "mean_temp_error": round(temperature_error / compared, 3),
        "mean_cloud_error": round(cloud_error / compared, 3),
        "mean_radiation_error": round(radiation_error / compared, 3),
    }
