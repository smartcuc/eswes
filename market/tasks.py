#################
# market/tasks.py
#################

import requests
from decimal import Decimal
from datetime import timezone as dt_timezone

from celery import shared_task
from django.utils import timezone

from market.models import SpotPrice


def unix_to_dt(ts):
    return timezone.datetime.fromtimestamp(ts, tz=dt_timezone.utc)


@shared_task
def fetch_spot_prices():

    url = "https://api.energy-charts.info/price"
    params = {"bzn": "DE-LU"}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    timestamps = data.get("unix_seconds", [])
    prices = data.get("price", [])

    # API liefert EUR / MWh → wir brauchen EUR / kWh
    # → durch 1000 teilen

    for ts, price_mwh in zip(timestamps, prices):

        dt = unix_to_dt(ts)
        price_kwh = Decimal(str(price_mwh)) / Decimal("1000")

        SpotPrice.objects.update_or_create(
            timestamp=dt,
            defaults={"price_eur_per_kwh": price_kwh, "source": "energy-charts"},
        )

    return {"status": "ok", "count": len(timestamps)}
