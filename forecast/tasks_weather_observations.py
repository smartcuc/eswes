########################################
# forecast/tasks_weather_observations.py
########################################

from celery import shared_task
from devices.models import Home

from forecast.services_weather_observations import (
    store_sensor_community_observations,
)


@shared_task
def fetch_weather_observations():

    results = []

    for home in Home.objects.all():

        if home.latitude is None or home.longitude is None:
            continue

        result = store_sensor_community_observations(
            home=home,
        )

        results.append(
            {
                "home": home.name,
                **result,
            }
        )

    return results
