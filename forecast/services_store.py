############################
# forecast/services_store.py
############################

from forecast.models import SolarForecast
from forecast.services_solar_forecast import tenant_solar_forecast_24h


def compute_tenant_forecast_series(tenant):
    """
    Liefert die physikalische Tenant-Level-Forecast-Serie.
    """
    return tenant_solar_forecast_24h(tenant)


def save_tenant_forecast(tenant, source="physics"):
    """
    Speichert Tenant-Level Forecasts in forecast_solarforecast.

    WICHTIG:
    - Kein meter-Feld verwenden (existiert im aktuellen Modell nicht)
    - Eindeutigkeit läuft über (tenant, timestamp)
    """
    series = compute_tenant_forecast_series(tenant)

    saved = 0

    for entry in series:
        _, created = SolarForecast.objects.update_or_create(
            tenant=tenant,
            timestamp=entry["timestamp"],
            defaults={
                "forecast_kwh": entry["forecast_kw"],
                "source": source,
            },
        )
        if created:
            saved += 1

    return {
        "saved": saved,
        "total": len(series),
    }
