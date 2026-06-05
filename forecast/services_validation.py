######################################
# forecast/services_validation.py
######################################

from django.utils import timezone


def validate_weather_payload(payload):

    timestamps = payload.get("timestamps", [])

    expected_delta = timezone.timedelta(hours=1)

    gaps = 0
    invalid_intervals = 0

    prev = None

    for ts in timestamps:
        dt = timezone.datetime.fromisoformat(ts)

        if prev:
            delta = dt - prev

            if delta != expected_delta:
                invalid_intervals += 1

                if delta > expected_delta:
                    gaps += 1

        prev = dt

    return {
        "count": len(timestamps),
        "gaps": gaps,
        "invalid_intervals": invalid_intervals,
        "status": "ok" if gaps == 0 and invalid_intervals == 0 else "warning",
    }
