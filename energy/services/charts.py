###########################
# energy/services/charts.py
###########################

from datetime import timedelta

from django.utils import timezone

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

    rows = (
        DeviceMetric1h.objects
        .filter(
            device_id__in=device_ids,
            metric_key="power",
            bucket__gte=since,
        )
        .order_by("bucket")
    )

    return [
        round(row.avg, 1)
        for row in rows
    ]


def get_chart_data(
    device_ids,
    period="24h",
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

    #
    # 1 Stunde
    #
    if period == "1h":

        since = now - timedelta(hours=1)

        rows = (
            DeviceMetric1m.objects
            .filter(
                device_id__in=device_ids,
                metric_key="power",
                bucket__gte=since,
            )
            .order_by("bucket")
        )

        return {
            "period": "1h",
            "unit": "W",
            "timestamps": [
                row.bucket.strftime("%H:%M")
                for row in rows
            ],
            "values": [
                round(row.avg, 1)
                for row in rows
            ],
        }

    #
    # 6 Stunden
    #
    elif period == "6h":

        since = now - timedelta(hours=6)

        rows = (
            DeviceMetric5m.objects
            .filter(
                device_id__in=device_ids,
                metric_key="power",
                bucket__gte=since,
            )
            .order_by("bucket")
        )

        return {
            "period": "6h",
            "unit": "W",
            "timestamps": [
                row.bucket.strftime("%H:%M")
                for row in rows
            ],
            "values": [
                round(row.avg, 1)
                for row in rows
            ],
        }

    #
    # 24 Stunden (Default)
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
            .order_by("bucket")
        )

        return {
            "period": "24h",
            "unit": "W",
            "timestamps": [
                row.bucket.strftime("%H:%M")
                for row in rows
            ],
            "values": [
                round(row.avg, 1)
                for row in rows
            ],
        }

    #
    # 5 Tage
    #
    elif period == "5d":

        since = now - timedelta(days=7)

        rows = (
            DeviceMetric1h.objects
            .filter(
                device_id__in=device_ids,
                metric_key="power",
                bucket__gte=since,
            )
            .order_by("bucket")
        )

        return {
            "period": "7d",
            "unit": "W",
            "timestamps": [
                row.bucket.strftime("%d.%m %Hh")
                for row in rows
            ],
            "values": [
                round(row.avg, 1)
                for row in rows
            ],
        }
    
    return {
    "period": "24h",
    "unit": "W",
    "timestamps": [],
    "values": [],
}