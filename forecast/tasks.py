###################
# forecast/tasks.py
###################

from celery import shared_task
from django.utils import timezone

from core.models import Tenant

from forecast.services_ml import train_tenant_model
from forecast.services_store import save_all_forecasts_for_tenant

# 🔥 NEU IMPORTIEREN
from forecast.services_weather import (
    group_tenants_by_location,
    fetch_and_store_weather_for_group,
)


@shared_task
def update_all_forecasts():
    """
    Zentrale Forecast-Pipeline:
    - Weather
    - ML
    - Forecast
    """

    # ✅ STEP 2 → HIER REIN
    tenants = list(Tenant.objects.all())

    if not tenants:
        return {"status": "no tenants"}

    location_groups = group_tenants_by_location(tenants)

    results = []

    for location_key, tenant_group in location_groups.items():

        try:
            weather_result = fetch_and_store_weather_for_group(tenant_group, hours=48)

        except Exception as e:
            for tenant in tenant_group:
                results.append(
                    {
                        "tenant_id": str(tenant.id),
                        "status": "error",
                        "stage": "weather",
                        "error": str(e),
                    }
                )
            continue

        # ✅ zweiter try (Forecast)
        for tenant in tenant_group:
            try:
                train_result = train_tenant_model(tenant)
                forecast_result = save_all_forecasts_for_tenant(tenant)

                results.append(
                    {
                        "tenant_id": str(tenant.id),
                        "status": "ok",
                        "location_key": str(location_key),
                        "weather_points": weather_result.get("count"),
                        "counts": forecast_result.get("counts"),
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "tenant_id": str(tenant.id),
                        "status": "error",
                        "stage": "forecast",
                        "error": str(e),
                    }
                )

    return {
        "run_at": str(timezone.now()),
        "results": results,
    }
