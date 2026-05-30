#####################################
# forecast/services_solar_forecast.py
#####################################

from datetime import datetime

from forecast.services_weather import get_weather_forecast
from forecast.services_series import estimate_tenant_capacity_kw


def solar_power_kw(capacity_kw, radiation, temperature, cloud_cover):
    if radiation <= 0 or capacity_kw <= 0:
        return 0.0

    # capacity_kw wird als beobachtete tenant-weite Peak-/Kapazitäts-Näherung genutzt.
    base_power = capacity_kw * (radiation / 1000.0)

    # Temperaturverlust: ca. -0.4% pro °C > 25
    temp_loss = max(0.0, (temperature - 25.0) * 0.004)
    temp_factor = 1.0 - temp_loss

    # Cloud-Dämpfung
    cloud_factor = 1.0 - (cloud_cover / 100.0) * 0.75

    # generischer Anlagenwirkungsgrad / Verluste
    performance_ratio = 0.85

    power = base_power * temp_factor * cloud_factor * performance_ratio
    return max(0.0, power)


def tenant_solar_forecast_24h(tenant):
    """
    Physikalisch vereinfachter Tenant-Level Forecast.
    """
    if tenant.latitude is None or tenant.longitude is None:
        return []

    weather = get_weather_forecast(tenant.latitude, tenant.longitude)
    capacity_kw = estimate_tenant_capacity_kw(tenant)

    results = []

    for ts, rad, temp, clouds in zip(
        weather["timestamps"],
        weather["radiation"],
        weather["temperature"],
        weather["cloud_cover"],
    ):
        production = solar_power_kw(
            capacity_kw=capacity_kw,
            radiation=float(rad or 0),
            temperature=float(temp or 0),
            cloud_cover=float(clouds or 0),
        )

        results.append(
            {
                "timestamp": datetime.fromisoformat(ts),
                "forecast_kw": production,
                "radiation_wm2": float(rad or 0),
                "temperature_c": float(temp or 0),
                "cloud_cover_pct": float(clouds or 0),
            }
        )

    return results
