###########################
# energy/services/charts.py
###########################

from datetime import timedelta
from zoneinfo import ZoneInfo

from django.utils import timezone
from django.db.models import Sum, Avg

from devices.models import (
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric1h,
)


def get_dashboard_chart(device_ids):
    """
    Sparkline für Dashboard-Kacheln.

    Immer letzte 24h.
    """

    since = timezone.now() - timedelta(hours=24)

    rows = DeviceMetric1h.objects.filter(
        device_id__in=device_ids,
        metric_key="power",
        bucket__gte=since,
    ).order_by("bucket")

    return [round(row.avg, 1) for row in rows]


def get_chart_data(
    device_ids,
    period="24h",
    timezone_name="UTC",
):
    """
    Modalchart.

    Perioden:
        1h
        6h
        24h
        5d
    """

    now = timezone.now()
    tz = ZoneInfo(timezone_name)

    #
    # 1 Stunde
    #
    if period == "1h":

        since = now - timedelta(hours=1)

        rows = DeviceMetric1m.objects.filter(
            device_id__in=device_ids,
            metric_key="power",
            bucket__gte=since,
        ).order_by("bucket")

        return {
            "period": "1h",
            "unit": "W",
            "timestamps": [row.bucket.astimezone(tz).strftime("%H:%M") for row in rows],
            "export_timestamps": [
                row.bucket.astimezone(tz).strftime("%d.%m.%Y %H:%M") for row in rows
            ],
            "values": [round(row.avg, 1) for row in rows],
        }

    #
    # 6 Stunden
    #
    elif period == "6h":

        since = now - timedelta(hours=6)

        rows = DeviceMetric5m.objects.filter(
            device_id__in=device_ids,
            metric_key="power",
            bucket__gte=since,
        ).order_by("bucket")

        return {
            "period": "6h",
            "unit": "W",
            "timestamps": [row.bucket.astimezone(tz).strftime("%H:%M") for row in rows],
            "export_timestamps": [
                row.bucket.astimezone(tz).strftime("%d.%m.%Y %H:%M") for row in rows
            ],
            "values": [round(row.avg, 1) for row in rows],
        }

    #
    # 24 Stunden
    #
    elif period == "24h":

        since = now - timedelta(hours=24)

        rows = (
            DeviceMetric1h.objects
            .filter(
                device_id__in=device_ids,
                metric_key="power",
                bucket__gte=since,
            )
            .values("bucket")
            .annotate(
                value=Sum("avg")
            )
            .order_by("bucket")
        )

        return {
            "period": "24h",
            "unit": "W",
            "timestamps": [
                row["bucket"].astimezone(tz).strftime("%H:%M")
                for row in rows
            ],
            "export_timestamps": [
                row["bucket"].astimezone(tz).strftime("%d.%m.%Y %H:%M")
                for row in rows
            ],
            "values": [
                round(row["value"] or 0, 1)
                for row in rows
            ],
        }

    #
    # 5 Tage
    #
    elif period == "5d":

        since = now - timedelta(days=5)

        rows = DeviceMetric1h.objects.filter(
            device_id__in=device_ids,
            metric_key="power",
            bucket__gte=since,
        ).order_by("bucket")

        return {
            "period": "5d",
            "unit": "W",
            "timestamps": [
                row.bucket.astimezone(tz).strftime("%d.%m %H:%M") for row in rows
            ],
            "export_timestamps": [
                row.bucket.astimezone(tz).strftime("%d.%m.%Y %H:%M") for row in rows
            ],
            "values": [round(row.avg, 1) for row in rows],
        }

    return {
        "period": "24h",
        "unit": "W",
        "timestamps": [],
        "export_timestamps": [],
        "values": [],
    }
