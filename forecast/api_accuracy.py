##########################
# forecast/api_accuracy.py
##########################

from rest_framework.response import Response
from rest_framework.decorators import api_view

from forecast.models_accuracy import (
    ForecastRunAccuracy,
)


@api_view(["GET"])
def forecast_accuracy(request):

    rows = ForecastRunAccuracy.objects.select_related(
        "forecast_run",
        "forecast_run__generator_string",
    ).order_by("-calculated_at")[:100]

    return Response(
        [
            {
                "generator": str(row.forecast_run.generator_string),
                "generated_at": row.forecast_run.generated_at,
                "points": row.points,
                "mae_kwh": row.mae_kwh,
                "max_error_kwh": row.max_error_kwh,
                "delta_percent": row.delta_percent,
                "forecast_kwh": row.total_forecast_kwh,
                "actual_kwh": row.total_actual_kwh,
            }
            for row in rows
        ]
    )
