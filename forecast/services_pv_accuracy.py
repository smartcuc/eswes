##################################
# forecast/services_pv_accuracy.py
##################################

from devices.models import DeviceMetric1h


def compare_forecast_run(run):

    device = run.generator_string.generator.device

    if not device:
        return []

    rows = []

    for forecast in run.values.order_by("timestamp"):

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
