######################################
# forecast/services_weather_history.py
######################################

from decimal import Decimal
import requests

from django.utils.dateparse import parse_datetime
from django.utils import timezone


from forecast.models import TenantWeatherSnapshot


def fetch_historical_weather(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,cloud_cover,shortwave_radiation",
        "timezone": "UTC",
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()["hourly"]

    return data


def store_historical_weather_for_tenant(tenant, start_date, end_date):
    if tenant.latitude is None or tenant.longitude is None:
        return {
            "tenant_id": str(tenant.id),
            "status": "missing_coordinates",
        }

    payload = fetch_historical_weather(
        tenant.latitude,
        tenant.longitude,
        start_date,
        end_date,
    )

    times = payload.get("time", [])
    temps = payload.get("temperature_2m", [])
    clouds = payload.get("cloud_cover", [])
    radiation = payload.get("shortwave_radiation", [])

    total = len(times)

    saved = 0
    skipped = 0
    missing_values = 0

    for i in range(total):

        ts = parse_datetime(times[i])

        temp = temps[i] if i < len(temps) else None
        cloud = clouds[i] if i < len(clouds) else None
        sw = radiation[i] if i < len(radiation) else None

        if ts is None:
            skipped += 1
            continue

        if timezone.is_naive(ts):
            ts = timezone.make_aware(ts, timezone.UTC)

        if temp is None or cloud is None or sw is None:
            missing_values += 1

        _, created = TenantWeatherSnapshot.objects.update_or_create(
            tenant=tenant,
            ts=ts,
            defaults={
                "temperature_c": Decimal(str(temp)) if temp is not None else None,
                "cloud_cover_pct": Decimal(str(cloud)) if cloud is not None else None,
                "shortwave_radiation_wm2": Decimal(str(sw)) if sw is not None else None,
            },
        )

        if created:
            saved += 1

    return {
        "tenant_id": str(tenant.id),
        "status": "ok",
        "saved": saved,
        "total": total,
        "skipped": skipped,
        "missing_values": missing_values,
    }
