######################
# forecast/services.py
######################

from django.utils import timezone
from datetime import timedelta

from forecast.models import SolarForecast


def get_forecast_for_slot(tenant, ts):

    return SolarForecast.objects.filter(tenant=tenant, timestamp=ts).first()


def get_forecast_range(tenant, start, end):

    return SolarForecast.objects.filter(
        tenant=tenant, timestamp__gte=start, timestamp__lt=end
    ).order_by("timestamp")
