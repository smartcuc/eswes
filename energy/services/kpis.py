#########################
# energy/services/kpis.py
#########################

from datetime import datetime, time

from django.db.models import Sum
from django.utils import timezone

from devices.models import DeviceMetric1h
from energy.ems.models import EMSSignalSource

import logging

logger = logging.getLogger(__name__)


def get_today_consumption(user):

    today_start = timezone.make_aware(
        datetime.combine(
            timezone.localdate(),
            time.min,
        )
    )

    grid_devices = EMSSignalSource.objects.filter(
        home__user=user,
        signal_type="grid",
    ).values_list(
        "device_id",
        flat=True,
    )

    if not grid_devices.exists():

        # logger.warning(
        #     "No grid source configured for user %s",
        #     user.id,
        # )

        return None

    total_wh = (
        DeviceMetric1h.objects
        .filter(
            device_id__in=grid_devices,
            bucket__gte=today_start,
            metric_key="power",
        )
        .aggregate(
            total=Sum("energy_wh")
        )["total"]
        or 0
    )

    rows = (
        DeviceMetric1h.objects
        .filter(
            device_id__in=grid_devices,
            bucket__gte=today_start,
            metric_key="power",
        )
        .values("bucket")
        .annotate(
            total_wh=Sum("energy_wh")
        )
        .order_by("bucket")
    )

    history = [
        round(
            (row["total_wh"] or 0) / 1000,
            3,
        )
        for row in rows
    ]
    
    return {
        "value": round(
            total_wh / 1000,
            2,
        ),
        "source": "grid_source",
        "history": history,
    }
