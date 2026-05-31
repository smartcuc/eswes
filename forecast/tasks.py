###################
# forecast/tasks.py
###################

from celery import shared_task
from django.utils import timezone

from metering.models import Tenant
from metering.models import Tenant
from forecast.services_ml import train_tenant_model
from forecast.services_store import save_all_forecasts_for_tenant


@shared_task
def update_all_forecasts():
    """
    Zentrale Forecast-Pipeline:
    - Physics
    - ML
    - Hybrid (dynamisch)
    """

    results = []

    for tenant in Tenant.objects.all():
        try:
            # ✅ 1. ML retrain
            train_result = train_tenant_model(tenant)

            # ✅ 2. Forecast neu berechnen
            forecast_result = save_all_forecasts_for_tenant(tenant)

            results.append(
                {
                    "tenant_id": str(tenant.id),
                    "status": "ok",
                    "training": train_result.get("status"),
                    "counts": forecast_result.get("counts"),
                }
            )

        except Exception as e:
            results.append(
                {
                    "tenant_id": str(tenant.id),
                    "status": "error",
                    "error": str(e),
                }
            )

    return {
        "run_at": str(timezone.now()),
        "results": results,
    }
