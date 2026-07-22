#################################
# devices/services/aggregation.py
#################################

from datetime import timedelta, datetime


from django.db import transaction
from django.db.models import (
    Avg,
    Min,
    Max,
    Count,
)

from django.utils import timezone

from devices.models import (
    DeviceMetric,
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
    DeviceConfig,
)


def floor_bucket(dt, seconds):

    epoch = int(dt.timestamp())

    floored = epoch - (epoch % seconds)

    return datetime.fromtimestamp(
        floored,
        tz=dt.tzinfo,
    )


def aggregate_1m():

    now = timezone.now()

    current_bucket = floor_bucket(
        now,
        60,
    )

    target = current_bucket - timedelta(
        minutes=1,
    )

    start = target
    end = target + timedelta(
        minutes=1,
    )

    rows = (
        DeviceMetric.objects
        .filter(
            timestamp__gte=start,
            timestamp__lt=end,
        )
        .values(
            "device_id",
        )
        .annotate(
            avg=Avg("value"),
            min=Min("value"),
            max=Max("value"),
            count=Count("id"),
        )
    )

    configs = dict(
        DeviceConfig.objects.filter(
            device__configured=True,
            metric_definition__isnull=False,
        ).values_list(
            "device_id",
            "metric_definition__key",
        )
    )

    with transaction.atomic():

        for row in rows:

            metric_key = configs.get(
                row["device_id"]
            )

            if not metric_key:
                continue

            energy_wh = None

            if (
                metric_key == "power"
                and row["avg"] is not None
            ):
                energy_wh = row["avg"] / 60

            DeviceMetric1m.objects.update_or_create(
                device_id=row["device_id"],
                metric_key=metric_key,
                bucket=target,
                defaults={
                    "avg": row["avg"],
                    "min": row["min"],
                    "max": row["max"],
                    "count": row["count"],
                    "energy_wh": energy_wh,
                },
            )


def rollup(
    source_model,
    target_model,
    bucket_seconds,
):
    """
    Generic rollup.

    - weighted avg
    - correct min/max
    - summed counts
    - summed energy
    """

    now = timezone.now()

    current_bucket = floor_bucket(
        now,
        bucket_seconds,
    )

    target = current_bucket - timedelta(
        seconds=bucket_seconds,
    )

    start = target
    end = target + timedelta(
        seconds=bucket_seconds,
    )

    rows = (
        source_model.objects
        .filter(
            bucket__gte=start,
            bucket__lt=end,
        )
        .order_by()
    )

    groups = {}

    for row in rows:

        key = (
            row.device_id,
            row.metric_key,
        )

        groups.setdefault(
            key,
            []
        ).append(row)

    with transaction.atomic():

        for (
            device_id,
            metric_key,
        ), items in groups.items():

            total_count = sum(
                item.count or 0
                for item in items
            )

            if total_count == 0:
                continue

            weighted_sum = sum(
                (item.avg or 0)
                * (item.count or 0)
                for item in items
            )

            avg = (
                weighted_sum
                / total_count
            )

            min_value = min(
                item.min
                for item in items
            )

            max_value = max(
                item.max
                for item in items
            )

            energy_wh = sum(
                item.energy_wh or 0
                for item in items
            )

            target_model.objects.update_or_create(
                device_id=device_id,
                metric_key=metric_key,
                bucket=target,
                defaults={
                    "avg": avg,
                    "min": min_value,
                    "max": max_value,
                    "count": total_count,
                    "energy_wh": energy_wh,
                },
            )

def aggregate_5m():

    rollup(
        source_model=DeviceMetric1m,
        target_model=DeviceMetric5m,
        bucket_seconds=300,
    )


def aggregate_15m():

    rollup(
        source_model=DeviceMetric5m,
        target_model=DeviceMetric15m,
        bucket_seconds=900,
    )


def aggregate_1h():

    rollup(
        source_model=DeviceMetric15m,
        target_model=DeviceMetric1h,
        bucket_seconds=3600,
    )
