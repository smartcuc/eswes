#################
# market/tasks.py
#################

import requests
from decimal import Decimal
from datetime import timezone as dt_timezone

from celery import shared_task
from django.utils import timezone
from django.core.cache import cache

from market.models import SpotPrice
from market.tasks_analysis import compute_daily_spot_summary


def unix_to_dt(ts):
    return timezone.datetime.fromtimestamp(ts, tz=dt_timezone.utc)


@shared_task
def fetch_spot_prices():

    url = "https://api.energy-charts.info/price"
    start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timezone.timedelta(days=2)

    params = {
        "bzn": "DE-LU",
        "start": int(start.timestamp()),
        "end": int(end.timestamp()),
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    timestamps = data.get("unix_seconds", [])
    prices = data.get("price", [])

    count = 0

    for ts, price_mwh in zip(timestamps, prices):

        dt = unix_to_dt(ts)
        price_kwh = Decimal(str(price_mwh)) / Decimal("1000")

        SpotPrice.objects.update_or_create(
            timestamp=dt,
            defaults={
                "price_eur_per_kwh": price_kwh,
                "source": "energy-charts",
            },
        )

        count += 1

    # ✅ Redis Status
    cache.set("spot:last_update", timezone.now().isoformat(), timeout=None)
    cache.set("spot:last_count", count, timeout=None)
    cache.set("spot:last_success", True, timeout=None)

    return {
        "status": "ok",
        "count": count,
    }


@shared_task(bind=True, max_retries=20)
def fetch_spot_prices_retry(self):

    try:
        result = fetch_spot_prices()

        count = result.get("count", 0)

        # ✅ Erwartung: mindestens ~80 Werte
        if count < 80:
            raise Exception(f"Spotpreise unvollständig ({count})")

        # ✅ SUCCESS markieren
        cache.set("spot:ready", True, timeout=None)

        # ✅ 🔥 Analyse starten
        compute_daily_spot_summary.delay()

        return result

    except Exception as e:

        cache.set("spot:last_success", False, timeout=None)

        # ✅ retry alle 5 Minuten
        raise self.retry(countdown=300, exc=e)
