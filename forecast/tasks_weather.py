###########################
# forecast/tasks_weather.py
###########################

from celery import shared_task
from core.models import Tenant

from forecast.services_weather import (
    group_tenants_by_location,
    fetch_and_store_weather_for_group,
)


@shared_task
def fetch_weather_data():
    """
    Lädt Wetterdaten für alle Tenants,
    gruppiert nach Standort (1 API-Call pro Location-Gruppe).
    """

    tenants = list(Tenant.objects.all())

    if not tenants:
        return {
            "status": "ok",
            "groups": 0,
            "message": "no tenants found",
        }

    location_groups = group_tenants_by_location(tenants)

    results = []

    for location_key, tenant_group in location_groups.items():
        try:
            result = fetch_and_store_weather_for_group(
                tenant_group,
                hours=48,
            )

            results.append(
                {
                    "location_key": str(location_key),
                    "status": "ok",
                    "count": result.get("count"),
                    "tenant_count": result.get("tenant_count"),
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
