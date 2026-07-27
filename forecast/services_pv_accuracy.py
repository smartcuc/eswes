##################################
# forecast/services_pv_accuracy.py
##################################

from django.utils import timezone
from devices.models import DeviceMetric1h


def compare_forecast_run(run):

    device = run.generator_string.generator.device

    if not device:
        return []

    rows = []

    for forecast in run.values.order_by("timestamp"):

        # Nur bereits vergangene Zeitpunkte bewerten
        if forecast.timestamp > timezone.now():
            continue

        actual = DeviceMetric1h.objects.filter(
            device=device,
            bucket=forecast.timestamp,
            metric_key="power",
        ).first()

        forecast_kwh = float(forecast.forecast_kwh)

        actual_kwh = float(actual.energy_wh) / 1000 if actual else None

        error_kwh = forecast_kwh - actual_kwh if actual_kwh is not None else None

        rows.append(
            {
                "timestamp": forecast.timestamp,
                "forecast_kwh": forecast_kwh,
                "actual_kwh": actual_kwh,
                "error_kwh": error_kwh,
            }
        )

    return rows


def calculate_forecast_accuracy(run):

    rows = compare_forecast_run(run)

    valid_rows = [row for row in rows if row["actual_kwh"] is not None]

    # Mindestens halber Tag Vergleichsdaten
    if len(valid_rows) < 12:
        return {
            "points": len(valid_rows),
            "status": "insufficient_data",
        }

    absolute_errors = [abs(row["error_kwh"]) for row in valid_rows]

    total_forecast_kwh = sum(row["forecast_kwh"] for row in valid_rows)

    total_actual_kwh = sum(row["actual_kwh"] for row in valid_rows)

    delta_kwh = total_forecast_kwh - total_actual_kwh

    delta_percent = (
        (delta_kwh / total_actual_kwh) * 100 if total_actual_kwh > 0 else None
    )

    return {
        "points": len(valid_rows),
        "mae_kwh": (sum(absolute_errors) / len(absolute_errors)),
        "max_error_kwh": max(absolute_errors),
        "total_forecast_kwh": round(
            total_forecast_kwh,
            3,
        ),
        "total_actual_kwh": round(
            total_actual_kwh,
            3,
        ),
        "delta_kwh": round(
            delta_kwh,
            3,
        ),
        "delta_percent": (
            round(delta_percent, 2) if delta_percent is not None else None
        ),
    }


def summarize_forecast_runs(limit=50):

    from forecast.models import ForecastRun

    results = []

    runs = ForecastRun.objects.filter(source="physics").order_by("-generated_at")[
        :limit
    ]

    # Nur vollständig abgelaufene ForecastRuns
    runs = [
        run
        for run in runs
        if run.values.last() and run.values.last().timestamp < timezone.now()
    ]

    for run in runs:

        accuracy = calculate_forecast_accuracy(run)

        if accuracy.get("status") == "insufficient_data":
            continue

        results.append(
            {
                "run_id": str(run.id),
                "generated_at": run.generated_at,
                "generator": str(run.generator_string),
                **accuracy,
            }
        )

    return results

