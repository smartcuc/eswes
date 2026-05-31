#####################################
# forecast/services_solar_forecast.py
#####################################

from datetime import datetime
from datetime import timezone as dt_timezone
from django.utils import timezone

from forecast.services_weather import (
    get_weather_forecast,
    resolve_forecast_coordinates,
)
from forecast.services_series import get_tenant_hourly_actuals


def estimate_tenant_capacity_kw(tenant):
    rows = get_tenant_hourly_actuals(tenant)

    if not rows:
        return 1.0

    values = [float(r["value"]) for r in rows if r.get("value") is not None]

    if len(values) < 2:
        return 1.0

    # ✅ Differenzen berechnen (echte Leistung!)
    diffs = [max(0.0, values[i] - values[i - 1]) for i in range(1, len(values))]

    if not diffs:
        return 1.0

    return max(diffs)


def solar_power_kw(capacity_kw, radiation, temperature, cloud_cover):
    """
    Vereinfachtes physikalisches Modell:
    - radiation skaliert die Leistung
    - Temperatur reduziert leicht bei Hitze
    - Wolken reduzieren nutzbare Strahlung
    """
    if capacity_kw <= 0:
        return 0.0

    if radiation is None:
        radiation = 0.0
    if temperature is None:
        temperature = 20.0
    if cloud_cover is None:
        cloud_cover = 0.0

    radiation = float(radiation)
    temperature = float(temperature)
    cloud_cover = float(cloud_cover)

    # Basis: 1000 W/m² ~ 100% grobe Auslastung
    base = capacity_kw * (radiation / 1000.0)

    # Temperaturverlust: ca. 0.4% pro °C über 25
    temp_loss = max(0.0, (temperature - 25.0) * 0.004)
    temp_factor = 1.0 - temp_loss

    # Wolkenreduktion
    cloud_factor = 1.0 - (cloud_cover / 100.0) * 0.75

    # Anlagenwirkungsgrad / Verluste
    performance_ratio = 0.85

    power = base * temp_factor * cloud_factor * performance_ratio
    power = max(0.0, power)

    return power


def tenant_solar_forecast_24h(tenant):
    """
    Baut einen vereinfachten physikalischen 24h-Forecast für einen Tenant.
    Nutzt Fallback-Koordinaten, falls Tenant aktuell keine Geo-Felder hat.

    WICHTIG:
    - Die Timestamps werden timezone-aware (UTC) zurückgegeben,
      damit sie später mit ML-Timestamps sauber gematcht werden können.
    """
    lat, lon = resolve_forecast_coordinates(tenant)

    weather = get_weather_forecast(lat, lon)
    capacity_kw = estimate_tenant_capacity_kw(tenant)

    results = []

    for ts, rad, temp, clouds in zip(
        weather["timestamps"],
        weather["radiation"],
        weather["temperature"],
        weather["cloud_cover"],
    ):
        dt = datetime.fromisoformat(ts)

        # Falls Open-Meteo naive ISO-Zeit liefert -> UTC-aware machen
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone=dt_timezone.utc)

        production = solar_power_kw(
            capacity_kw=capacity_kw,
            radiation=rad,
            temperature=temp,
            cloud_cover=clouds,
        )

        results.append(
            {
                "timestamp": dt,
                "forecast_kw": float(production),
                "radiation_wm2": float(rad or 0),
                "temperature_c": float(temp or 0),
                "cloud_cover_pct": float(clouds or 0),
            }
        )

    return results
