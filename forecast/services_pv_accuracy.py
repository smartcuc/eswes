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

        rows.append(
            {
                "timestamp": forecast.timestamp,
                "forecast_kwh": float(forecast.forecast_kwh),
                "actual_wh": (float(actual.energy_wh) if actual else None),
            }
        )

    return rows
