#####################
# operations/tasks.py
#####################

import logging
import redis

from celery import shared_task

from django.conf import settings
from django.utils import timezone

from market.models import SpotPrice
from devices.models import Device

from devices.models import (
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
)

from operations.models import HealthState


logger = logging.getLogger(__name__)


@shared_task
def run_health_checks():

    checks = [
        check_spot_prices,
        check_celery_queues,
        check_aggregation_1m,
        check_aggregation_5m,
        check_aggregation_15m,
        check_aggregation_1h,
        check_mqtt,
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


def update_aggregation_health(
    key,
    model,
    max_age_seconds,
):

    latest = model.objects.order_by("-bucket").first()

    if not latest:

        HealthState.objects.update_or_create(
            key=key,
            defaults={
                "status": "error",
                "value": "no data",
                "details": {},
            },
        )

        return

    age = timezone.now() - latest.bucket

    if age.total_seconds() > max_age_seconds:

        status = "error"

    elif age.total_seconds() > (max_age_seconds / 2):

        status = "warn"

    else:

        status = "ok"

    HealthState.objects.update_or_create(
        key=key,
        defaults={
            "status": status,
            "value": latest.bucket.isoformat(),
            "details": {
                "age_seconds": int(age.total_seconds()),
            },
        },
    )


def check_aggregation_1m():

    update_aggregation_health(
        key="aggregation_1m",
        model=DeviceMetric1m,
        max_age_seconds=600,
    )


def check_aggregation_5m():

    update_aggregation_health(
        key="aggregation_5m",
        model=DeviceMetric5m,
        max_age_seconds=1800,
    )


def check_aggregation_15m():

    update_aggregation_health(
        key="aggregation_15m",
        model=DeviceMetric15m,
        max_age_seconds=3600,
    )


def check_aggregation_1h():

    update_aggregation_health(
        key="aggregation_1h",
        model=DeviceMetric1h,
        max_age_seconds=7200,
    )


def check_mqtt():

    latest = (
        Device.objects.exclude(last_seen__isnull=True).order_by("-last_seen").first()
    )

    if not latest:

        HealthState.objects.update_or_create(
            key="mqtt",
            defaults={
                "status": "error",
                "value": "no device seen",
                "details": {},
            },
        )

        return

    age = timezone.now() - latest.last_seen

    if age.total_seconds() > 900:

        status = "error"

    elif age.total_seconds() > 300:

        status = "warn"

    else:

        status = "ok"

    HealthState.objects.update_or_create(
        key="mqtt",
        defaults={
            "status": status,
            "value": latest.last_seen.isoformat(),
            "details": {
                "device_id": latest.id,
                "age_seconds": int(age.total_seconds()),
            },
        },
    )

