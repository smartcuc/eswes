#####################
# backend/tasks.py
#####################
import logging

logger = logging.getLogger(__name__)

from celery import shared_task
import requests
from market.tasks import fetch_spot_prices as market_fetch_spot_prices


@shared_task(bind=True)
def process_data(self, data):
    logger.info("task started", extra={"task_id": self.request.id})


@shared_task
def fetch_spot_prices():
    return market_fetch_spot_prices()
