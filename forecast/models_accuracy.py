#############################
# forecast/models_accuracy.py
#############################

import uuid

from django.db import models


class ForecastRunAccuracy(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    forecast_run = models.OneToOneField(
        "forecast.ForecastRun",
        on_delete=models.CASCADE,
        related_name="accuracy",
    )

    points = models.IntegerField()

    mae_kwh = models.FloatField()

    max_error_kwh = models.FloatField()

    total_forecast_kwh = models.FloatField()

    total_actual_kwh = models.FloatField()

    delta_kwh = models.FloatField()

    delta_percent = models.FloatField()

    calculated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.forecast_run} " f"(MAE={self.mae_kwh:.3f})"


