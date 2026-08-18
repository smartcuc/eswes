#####################
# operations/tasks.py
#####################

import logging
import redis

from celery import shared_task

from django.conf import settings
from django.utils import timezone

from market.models import SpotPrice
from operations.models import HealthState

logger = logging.getLogger(__name__)


@shared_task
def run_health_checks():

    checks = [
        check_spot_prices,
        check_celery_queues,
    ]

    for check in checks:

        try:
            check()

        except Exception:

            logger.exception(
                "health check failed: %s",
                check.__name__,
            )


def check_spot_prices():

    latest = SpotPrice.objects.order_by("-timestamp").first()

    if not latest:

        HealthState.objects.update_or_create(
            key="spot_prices",
            defaults={
                "status": "error",
                "value": "no spot prices available",
                "details": {},
            },
        )

        return

    timestamp = latest.timestamp

    if timezone.is_naive(timestamp):
        timestamp = timezone.make_aware(timestamp)

    age = timezone.now() - timestamp

    if age.total_seconds() > 21600:

        status = "error"

    elif age.total_seconds() > 10800:

        status = "warn"

    else:

        status = "ok"

    HealthState.objects.update_or_create(
        key="spot_prices",
        defaults={
            "status": status,
            "value": (f"latest spot price: " f"{timestamp.isoformat()}"),
            "details": {
                "age_seconds": int(age.total_seconds()),
                "timestamp": timestamp.isoformat(),
            },
        },
    )


def check_celery_queue():

    redis_url = settings.CELERY_BROKER_URL

    client = redis.from_url(redis_url)

    queue_length = client.llen("celery")

    if queue_length >= 10000:

        status = "error"

    elif queue_length >= 1000:

        status = "warn"

    else:

        status = "ok"

    HealthState.objects.update_or_create(
        key="celery_queue",
        defaults={
            "status": status,
            "value": str(queue_length),
            "details": {
                "queue": "celery",
                "length": queue_length,
            },
        },
    )


def check_celery_queues():

    redis_url = settings.CELERY_BROKER_URL

    client = redis.from_url(redis_url)

    queues = [
        "celery",
        "critical",
        "market",
        "aggregation",
        "telemetry",
        "forecast",
        "demo",
    ]

    for queue in queues:

        queue_length = client.llen(queue)

        if queue_length >= 10000:

            status = "error"

        elif queue_length >= 1000:

            status = "warn"

        else:

            status = "ok"

        HealthState.objects.update_or_create(
            key=f"celery_queue_{queue}",
            defaults={
                "status": status,
                "value": str(queue_length),
                "details": {
                    "queue": queue,
                    "length": queue_length,
                },
            },
        )
