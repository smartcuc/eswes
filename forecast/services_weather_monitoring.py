#########################################
# forecast/services_weather_monitoring.py
#########################################

from django.utils import timezone
from forecast.models import TenantWeatherSnapshot


def validate_weather_data(tenant):

    print("WEATHER DEBUG → tenant:", tenant)
    print("WEATHER DEBUG → type:", type(tenant))

    now = timezone.now()

    start = now.replace(minute=0, second=0, microsecond=0)
    end = start + timezone.timedelta(hours=48)

    print("BEFORE FILTER: → tenant:", tenant)
    print("BEFORE FILTER: → type:", type(tenant))

    rows = list(
        TenantWeatherSnapshot.objects.filter(
            tenant=tenant,
            ts__gte=start,
            ts__lt=end,
        ).order_by("ts")
    )

    result = {
        "count": len(rows),
        "expected": 48,
        "missing_slots": 0,
        "gaps": 0,
        "invalid_intervals": 0,
        "missing_values": 0,
        "status": "ok",
    }

    if not rows:
        result["status"] = "error"
        result["reason"] = "no-data"
        return result

    if len(rows) < 48:
        result["missing_slots"] = 48 - len(rows)

    expected_delta = timezone.timedelta(hours=1)

    prev = None

    for r in rows:
        if prev:
            delta = r.ts - prev.ts

            if delta != expected_delta:
                result["invalid_intervals"] += 1

                if delta > expected_delta:
                    result["gaps"] += 1

        if (
            r.temperature_c is None
            or r.cloud_cover_pct is None
            or r.shortwave_radiation_wm2 is None
        ):
            result["missing_values"] += 1

        prev = r

    if result["missing_slots"] > 5 or result["gaps"] > 2:
        result["status"] = "error"
    elif result["missing_slots"] > 0 or result["missing_values"] > 0:
        result["status"] = "warning"
    else:
        result["status"] = "ok"

    return result
