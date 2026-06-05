###############################
# market/services_validation.py
###############################

from market.models import SpotPrice
from django.utils import timezone


def validate_spot_prices():

    now = timezone.now()

    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timezone.timedelta(days=1)

    prices = list(
        SpotPrice.objects.filter(timestamp__gte=start, timestamp__lt=end).order_by(
            "timestamp"
        )
    )

    result = {
        "count": len(prices),
        "expected": 96,
        "missing_slots": 0,
        "gaps": 0,
        "invalid_intervals": 0,
        "status": "ok",
    }

    if not prices:
        result["status"] = "error"
        result["reason"] = "no-data"
        return result

    if len(prices) < 96:
        result["missing_slots"] = 96 - len(prices)

    expected_delta = timezone.timedelta(minutes=15)

    prev = None

    for p in prices:
        if prev:
            delta = p.timestamp - prev.timestamp

            if delta != expected_delta:
                result["invalid_intervals"] += 1

                if delta > expected_delta:
                    result["gaps"] += 1

        prev = p

    if result["missing_slots"] > 10 or result["gaps"] > 5:
        result["status"] = "error"
    elif result["missing_slots"] > 0 or result["invalid_intervals"] > 0:
        result["status"] = "warning"
    else:
        result["status"] = "ok"

    return result
