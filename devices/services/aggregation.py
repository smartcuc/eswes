#
# services/aggregation.py
##


from datetime import timedelta

def floor_bucket(dt, seconds):
    return dt - timedelta(
        seconds=dt.second % seconds,
        microseconds=dt.microsecond
    )

from django.utils import timezone
from django.db.models import Avg, Min, Max, Count

from devices.models import DeviceMetric, DeviceMetric1m


def aggregate_1m():
    now = timezone.now()

    # aktueller Bucket
    current_bucket = floor_bucket(now, 60)

    # letzter abgeschlossener Bucket
    target = current_bucket - timedelta(minutes=1)

    start = target
    end = target + timedelta(minutes=1)

    rows = (
        DeviceMetric.objects
        .filter(timestamp__gte=start, timestamp__lt=end)
        .values("device_id")
        .annotate(
            avg=Avg("value"),
            min=Min("value"),
            max=Max("value"),
            count=Count("id"),
        )
    )

    for r in rows:
        DeviceMetric1m.objects.update_or_create(
            device_id=r["device_id"],
            bucket=target,
            defaults={
                "avg": r["avg"],
                "min": r["min"],
                "max": r["max"],
                "count": r["count"],
            }
        )


from devices.models import DeviceMetric1m, DeviceMetric5m


def aggregate_5m():
    now = timezone.now()

    current_bucket = floor_bucket(now, 300)  # 5m
    target = current_bucket - timedelta(minutes=5)

    start = target
    end = target + timedelta(minutes=5)

    rows = (
        DeviceMetric1m.objects
        .filter(bucket__gte=start, bucket__lt=end)
        .values("device_id")
        .annotate(
            avg=Avg("avg"),
            min=Min("min"),
            max=Max("max"),
            count=Avg("count"),  # alternativ Sum
        )
    )

    for r in rows:
        DeviceMetric5m.objects.update_or_create(
            device_id=r["device_id"],
            bucket=target,
            defaults={
                "avg": r["avg"],
                "min": r["min"],
                "max": r["max"],
                "count": int(r["count"] or 0),
            }
        )

