###################
# forecast/tasks.py
###################

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from metering.models import Tenant
from forecast.models import SolarForecast, TenantForecastAccuracy
from forecast.services_weather_history import store_historical_weather_for_tenant
from forecast.services_ml import (
    train_tenant_model,
    predict_next_24h_ml_for_tenant,
)
from forecast.services_store import (
    save_tenant_forecast,
    compute_tenant_forecast_series,
)
from forecast.services_compare import compute_mae, compute_mape, blend_hybrid
from forecast.services_series import get_tenant_hourly_actuals


@shared_task
def sync_weather_history_last_30d():
    """
    Lädt für alle Tenants die letzten 30 Tage Wetterhistorie nach.
    """
    end = timezone.now().date()
    start = end - timedelta(days=30)

    results = []

    for tenant in Tenant.objects.all():
        results.append(
            store_historical_weather_for_tenant(
                tenant=tenant,
                start_date=start.isoformat(),
                end_date=end.isoformat(),
            )
        )

    return results


@shared_task
def train_all_solar_ml_models():
    """
    Trainiert für alle Tenants ein ML-Modell.
    """
    results = []

    for tenant in Tenant.objects.all():
        results.append(train_tenant_model(tenant))

    return results


@shared_task
def save_all_physics_forecasts():
    """
    Speichert den physikalischen Forecast für alle Tenants.
    """
    results = []

    for tenant in Tenant.objects.all():
        result = save_tenant_forecast(tenant, source="physics")
        results.append(
            {
                "tenant_id": str(tenant.id),
                "status": "physics_saved",
                **result,
            }
        )

    return results


@shared_task
def save_all_ml_forecasts():
    """
    Speichert ML-Forecasts für alle Tenants.
    """
    results = []

    for tenant in Tenant.objects.all():
        ml_preds = predict_next_24h_ml_for_tenant(tenant)

        if ml_preds is None:
            results.append(
                {
                    "tenant_id": str(tenant.id),
                    "status": "no_ml_model_or_not_enough_data",
                }
            )
            continue

        saved = 0

        for entry in ml_preds:
            _, created = SolarForecast.objects.update_or_create(
                tenant=tenant,
                timestamp=entry["timestamp"],
                defaults={
                    "forecast_kwh": entry["forecast_kw"],
                    "source": "ml",
                },
            )
            if created:
                saved += 1

        results.append(
            {
                "tenant_id": str(tenant.id),
                "status": "ml_saved",
                "saved": saved,
                "total": len(ml_preds),
            }
        )

    return results


@shared_task
def save_all_hybrid_forecasts(alpha=0.7):
    """
    Echter Hybrid auf Tenant-Level:
    hybrid = alpha * ML + (1 - alpha) * Physik
    """
    results = []

    for tenant in Tenant.objects.all():
        ml_preds = predict_next_24h_ml_for_tenant(tenant)
        physics_preds = compute_tenant_forecast_series(tenant)

        if ml_preds is None and not physics_preds:
            results.append(
                {
                    "tenant_id": str(tenant.id),
                    "status": "no_ml_no_physics",
                }
            )
            continue

        if ml_preds is None:
            fallback = save_tenant_forecast(tenant, source="physics")
            results.append(
                {
                    "tenant_id": str(tenant.id),
                    "status": "fallback_physics",
                    **fallback,
                }
            )
            continue

        if not physics_preds:
            saved = 0
            for entry in ml_preds:
                _, created = SolarForecast.objects.update_or_create(
                    tenant=tenant,
                    timestamp=entry["timestamp"],
                    defaults={
                        "forecast_kwh": entry["forecast_kw"],
                        "source": "ml",
                    },
                )
                if created:
                    saved += 1

            results.append(
                {
                    "tenant_id": str(tenant.id),
                    "status": "fallback_ml",
                    "saved": saved,
                    "total": len(ml_preds),
                }
            )
            continue

        ml_map = {entry["timestamp"]: entry["forecast_kw"] for entry in ml_preds}
        physics_map = {
            entry["timestamp"]: entry["forecast_kw"] for entry in physics_preds
        }

        all_timestamps = sorted(set(ml_map.keys()) | set(physics_map.keys()))
        saved = 0

        for ts in all_timestamps:
            ml_val = ml_map.get(ts)
            phys_val = physics_map.get(ts)

            if ml_val is None and phys_val is None:
                continue
            if ml_val is None:
                hybrid_kw = phys_val
            elif phys_val is None:
                hybrid_kw = ml_val
            else:
                hybrid_kw = blend_hybrid(float(phys_val), float(ml_val), alpha=alpha)

            _, created = SolarForecast.objects.update_or_create(
                tenant=tenant,
                timestamp=ts,
                defaults={
                    "forecast_kwh": hybrid_kw,
                    "source": "hybrid",
                },
            )
            if created:
                saved += 1

        results.append(
            {
                "tenant_id": str(tenant.id),
                "status": "hybrid_saved",
                "saved": saved,
                "total": len(all_timestamps),
                "alpha": alpha,
            }
        )

    return results


@shared_task
def compare_models_last_24h():
    """
    Vergleicht die letzten 24h Istwerte gegen gespeicherte physics/ml/hybrid Forecasts.
    """
    results = []

    now = timezone.now()
    start = now - timedelta(hours=24)

    for tenant in Tenant.objects.all():
        actual_rows = get_tenant_hourly_actuals(tenant, start=start, end=now)

        if not actual_rows:
            continue

        actual_map = {row["timestamp"]: float(row["value"]) for row in actual_rows}
        timestamps = sorted(actual_map.keys())

        for source in ["physics", "ml", "hybrid"]:
            forecast_rows = list(
                SolarForecast.objects.filter(
                    tenant=tenant,
                    source=source,
                    timestamp__gte=start,
                    timestamp__lt=now,
                )
                .order_by("timestamp")
                .values("timestamp", "forecast_kwh")
            )

            forecast_map = {
                row["timestamp"]: float(row["forecast_kwh"]) for row in forecast_rows
            }

            common_ts = [ts for ts in timestamps if ts in forecast_map]
            if not common_ts:
                continue

            actual_vals = [actual_map[ts] for ts in common_ts]
            forecast_vals = [forecast_map[ts] for ts in common_ts]

            mae = compute_mae(actual_vals, forecast_vals)
            mape = compute_mape(actual_vals, forecast_vals)

            TenantForecastAccuracy.objects.create(
                tenant=tenant,
                model_type=source,
                window_start=common_ts[0],
                window_end=common_ts[-1],
                mae_kw=mae,
                mape_pct=mape,
            )

            results.append(
                {
                    "tenant_id": str(tenant.id),
                    "model_type": source,
                    "mae_kw": mae,
                    "mape_pct": mape,
                }
            )

    return results
