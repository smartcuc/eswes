######################################
# forecast/services_weather_history.py
######################################

from decimal import Decimal
import requests

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

    return {
        "time": data["time"],
        "temperature_2m": data.get("temperature_2m", []),
        "cloud_cover": data.get("cloud_cover", []),
        "shortwave_radiation": data.get("shortwave_radiation", []),
    }


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

    saved = 0

    for ts, temp, cloud, sw in zip(
        payload["time"],
        payload["temperature_2m"],
        payload["cloud_cover"],
        payload["shortwave_radiation"],
    ):
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
        "total": len(payload["time"]),
    }
