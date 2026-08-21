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


def fetch_spot_prices_smard():

    index_url = (
        "https://www.smard.de/app/chart_data/" "4169/DE-LU/index_quarterhour.json"
    )

    index_response = requests.get(
        index_url,
        timeout=10,
    )

    index_response.raise_for_status()

    latest_timestamp = index_response.json()["timestamps"][-1]

    data_url = (
        "https://www.smard.de/app/chart_data/"
        f"4169/DE-LU/"
        f"4169_DE-LU_quarterhour_"
        f"{latest_timestamp}.json"
    )

    response = requests.get(
        data_url,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    objs = []

    for ts_ms, price_mwh in data.get(
        "series",
        [],
    ):

        if price_mwh is None:
            continue

        dt = timezone.datetime.fromtimestamp(
            ts_ms / 1000,
            tz=dt_timezone.utc,
        )

        price_kwh = Decimal(str(price_mwh)) / Decimal("1000")

        objs.append(
            SpotPrice(
                timestamp=dt,
                price_eur_per_kwh=price_kwh,
                source="smard",
            )
        )

    if objs:
        SpotPrice.objects.bulk_create(
            objs,
            update_conflicts=True,
            unique_fields=["timestamp", "source"],
            update_fields=["price_eur_per_kwh"],
        )

    count = len(objs)

    cache.set(
        "spot:last_update",
        timezone.now().isoformat(),
        timeout=None,
    )

    cache.set(
        "spot:last_count",
        count,
        timeout=None,
    )

    cache.set(
        "spot:last_success",
        True,
        timeout=None,
    )

    return {
        "status": "ok",
        "count": count,
    }


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

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

    except requests.RequestException:

        return fetch_spot_prices_smard()

    data = response.json()

    timestamps = data.get("unix_seconds", [])
    prices = data.get("price", [])

    objs = []

    for ts, price_mwh in zip(timestamps, prices):

        if price_mwh is None:
            continue

        dt = unix_to_dt(ts)
        price_kwh = Decimal(str(price_mwh)) / Decimal("1000")

        objs.append(
            SpotPrice(
                timestamp=dt,
                price_eur_per_kwh=price_kwh,
                source="energy-charts",
            )
        )

    if objs:
        SpotPrice.objects.bulk_create(
            objs,
            update_conflicts=True,
            unique_fields=["timestamp", "source"],
            update_fields=["price_eur_per_kwh"],
        )

    count = len(objs)

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
