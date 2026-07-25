###########################
# forecast/tasks_weather.py
###########################

from celery import shared_task
from devices.models import Home

from forecast.services_weather import (
    group_homes_by_location,
    fetch_and_store_weather_for_group,
)


@shared_task
def fetch_weather_data():
    """
    Lädt Wetterdaten für alle Tenants,
    gruppiert nach Standort (1 API-Call pro Location-Gruppe).
    """

    homes = list(Home.objects.all())

    if not homes:
        return {
            "status": "ok",
            "groups": 0,
            "message": "no homes found",
        }

    location_groups = group_homes_by_location(homes)

    results = []

    for location_key, home_group in location_groups.items():
        try:
            result = fetch_and_store_weather_for_group(
                home_group,
                hours=48,
            )

            results.append(
        {
            "location_key": str(location_key),
            "status": "ok",
            "count": result.get("count"),
            "home_count": result.get("home_count"),
            "written_total": result.get("written_total"),
        }
    )

        except Exception as e:
            results.append(
                {
                    "location_key": str(location_key),
                    "status": "error",
                    "error": str(e),
                }
            )

    return {
        "status": "ok",
        "groups": len(results),
        "results": results,
    }
