########################################
# forecast/tasks_weather_observations.py
########################################

from celery import shared_task

from core.models import Tenant

from forecast.services_weather_observations import (
    store_sensor_community_observations,
)


@shared_task
def fetch_weather_observations():

    results = []

    for tenant in Tenant.objects.all():

        if tenant.latitude is None or tenant.longitude is None:
            continue

        result = store_sensor_community_observations(
            lat=tenant.latitude,
            lon=tenant.longitude,
        )

        results.append(result)

    return results
