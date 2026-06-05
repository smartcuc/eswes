###################################
# market/services_price_analysis.py
###################################

from market.models import SpotPrice
from django.utils import timezone
from collections import defaultdict


def get_hourly_prices():
    now = timezone.now()

    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timezone.timedelta(days=1)

    prices = SpotPrice.objects.filter(timestamp__gte=start, timestamp__lt=end).order_by(
        "timestamp"
    )

    hours = defaultdict(list)

    for p in prices:
        hour = p.timestamp.replace(minute=0, second=0, microsecond=0)
        hours[hour].append(float(p.price_eur_per_kwh))

    hourly_avg = []

    for hour, values in hours.items():
        if len(values) == 4:
            avg_price = sum(values) / len(values)
            hourly_avg.append({"hour": hour, "price": avg_price})

    return sorted(hourly_avg, key=lambda x: x["hour"])


def get_cheapest_hours(hourly_prices):
    return sorted(hourly_prices, key=lambda x: x["price"])[:3]


def find_cheapest_window(hourly_prices, window_size):
    best = None

    for i in range(len(hourly_prices) - window_size + 1):

        window = hourly_prices[i : i + window_size]

        avg_price = sum(x["price"] for x in window) / window_size

        if not best or avg_price < best["avg_price"]:
            best = {
                "start": window[0]["hour"],
                "end": window[-1]["hour"],
                "avg_price": avg_price,
            }

    return best


def get_price_insights():

    hourly = get_hourly_prices()

    return {
        "cheapest_hours": get_cheapest_hours(hourly),
        "best_2h": find_cheapest_window(hourly, 2),
        "best_3h": find_cheapest_window(hourly, 3),
        "best_5h": find_cheapest_window(hourly, 5),
    }
