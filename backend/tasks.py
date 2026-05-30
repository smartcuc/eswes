#####################
# backend/tasks.py
#####################
import logging

logger = logging.getLogger(__name__)

from celery import shared_task
import requests
from celery import shared_task
from django.utils import timezone


@shared_task(bind=True)
def process_data(self, data):
    logger.info("task started", extra={"task_id": self.request.id})


@shared_task
def fetch_spot_prices():
    """
    Beispiel: Day-Ahead Preise holen (API anpassbar)
    """

    url = "https://api.energy-charts.info/price?bzn=DE&start=now"

    try:
        response = requests.get(url)
        data = response.json()

        timestamps = data.get("unix_seconds", [])
        prices = data.get("price", [])

        for ts, price in zip(timestamps, prices):
            dt = timezone.datetime.fromtimestamp(ts, tz=timezone.utc)

            # €/MWh → €/kWh
            price_kwh = price / 1000

            SpotPrice.objects.update_or_create(
                timestamp=dt, defaults={"price_eur_per_kwh": price_kwh}
            )

    except Exception as e:
        print("Spot price fetch failed:", e)
