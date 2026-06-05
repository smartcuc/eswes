########################################
# forecast/services_forecast_accuracy.py
########################################

########################################
# forecast/services_forecast_accuracy.py
########################################

from django.utils.dateparse import parse_datetime

from forecast.models import TenantWeatherSnapshot
from forecast.services_weather_history import fetch_historical_weather


def calculate_forecast_accuracy(tenant, start_date, end_date):

    print("ACCURACY DEBUG → tenant:", tenant)
    print("ACCURACY DEBUG → type:", type(tenant))

    # 🔵 Forecast aus DB (✅ saubere Zeit-Normalisierung!)
    forecast_rows = {
        row.ts.replace(minute=0, second=0, microsecond=0): row
        for row in TenantWeatherSnapshot.objects.filter(
            tenant=tenant,
            ts__date__gte=start_date,
            ts__date__lte=end_date,
        )
    }

    # 🟢 Realität von API laden
    payload = fetch_historical_weather(
        tenant.latitude,
        tenant.longitude,
        start_date,
        end_date,
    )

    times = payload["time"]
    actual_temp = payload["temperature_2m"]
    actual_cloud = payload["cloud_cover"]
    actual_rad = payload["shortwave_radiation"]

    compared = 0

    temperature_error = 0
    cloud_error = 0
    radiation_error = 0

    for i in range(len(times)):

        ts = parse_datetime(times[i])
        if ts is None:
            continue

        # ✅ WICHTIG: gleiche Normalisierung wie DB
        ts = ts.replace(minute=0, second=0, microsecond=0)

        # ✅ kein Match → überspringen
        if ts not in forecast_rows:
            continue

        f = forecast_rows[ts]

        # ✅ Fehler berechnen (nur wenn Werte vorhanden)
        if f.temperature_c is not None and actual_temp[i] is not None:
            temperature_error += abs(float(f.temperature_c) - actual_temp[i])

        if f.cloud_cover_pct is not None and actual_cloud[i] is not None:
            cloud_error += abs(float(f.cloud_cover_pct) - actual_cloud[i])

        if f.shortwave_radiation_wm2 is not None and actual_rad[i] is not None:
            radiation_error += abs(float(f.shortwave_radiation_wm2) - actual_rad[i])

        compared += 1

    # ✅ kein Overlap → sauberer Fehler
    if compared == 0:
        return {"status": "error", "reason": "no-overlap-after-alignment"}

    return {
        "status": "ok",
        "points_compared": compared,
        "mean_temp_error": temperature_error / compared,
        "mean_cloud_error": cloud_error / compared,
        "mean_radiation_error": radiation_error / compared,
    }
