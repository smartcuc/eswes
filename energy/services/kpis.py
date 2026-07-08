#########################
# energy/services/kpis.py
#########################

from datetime import datetime, time

from django.db.models import Sum
from django.utils import timezone

from devices.models import (
    DeviceConfig,
    DeviceMetric1h,
)

import logging

logger = logging.getLogger(__name__)


def get_today_consumption(user):
    """
    Liefert den heutigen Verbrauch in kWh.

    Prioritäten:

    1. Direkter Verbrauchszähler (consumer)
    2. PV + Grid Bilanz
    3. Nur Grid Import
    """

    today_start = timezone.make_aware(
        datetime.combine(
            timezone.localdate(),
            time.min,
        )
    )

    # =====================================================
    # Priorität 1:
    # Direkter Verbrauchszähler
    # =====================================================

    consumer_devices = DeviceConfig.objects.filter(
        device__home__user=user,
        role__key="consumer",
        measurement_type="power",
    ).values_list(
        "device_id",
        flat=True,
    )

    if consumer_devices.exists():

        total_wh = (
            DeviceMetric1h.objects
            .filter(
                device_id__in=consumer_devices,
                bucket__gte=today_start,
                metric_key="power",
            )
            .aggregate(
                total=Sum("energy_wh")
            )["total"]
            or 0
        )

        return {
            "value": round(total_wh / 1000, 2),
            "source": "consumer_meter",
        }

    # =====================================================
    # Priorität 2:
    # PV + Grid Bilanz
    # Verbrauch =
    # PV + Import - Export
    # =====================================================

    producer_devices = DeviceConfig.objects.filter(
        device__home__user=user,
        role__key="producer",
        measurement_type="power",
    ).values_list(
        "device_id",
        flat=True,
    )

    grid_devices = DeviceConfig.objects.filter(
        device__home__user=user,
        role__key="grid",
        measurement_type="power",
    ).values_list(
        "device_id",
        flat=True,
    )

    if (
        producer_devices.exists()
        and grid_devices.exists()
    ):

        pv_wh = (
            DeviceMetric1h.objects
            .filter(
                device_id__in=producer_devices,
                bucket__gte=today_start,
                metric_key="power",
            )
            .aggregate(
                total=Sum("energy_wh")
            )["total"]
            or 0
        )

        grid_wh = (
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

        total_wh = pv_wh + grid_wh

        return {
            "value": round(total_wh / 1000, 2),
            "source": "energy_balance",
        }

    # =====================================================
    # Priorität 3:
    # Nur Netzbezug
    # =====================================================

    if grid_devices.exists():

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
        
        logger.info(
            "Today KPI: %.2f kWh (%s)",
            total_wh / 1000,
            "consumer_meter",
        )
        return {
            "value": round(total_wh / 1000, 2),
            "source": "grid_only",
        }

    # =====================================================
    # nichts gefunden
    # =====================================================

    return None
