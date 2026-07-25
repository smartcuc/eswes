####################
# forecast/models.py
####################

import uuid
from django.db import models

from producer.models import GeneratorString

class SolarForecast(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    generator_string = models.ForeignKey(
        "producer.GeneratorString",
        on_delete=models.CASCADE,
        related_name="solar_forecasts",
        null=True,
        blank=True,
    )

    timestamp = models.DateTimeField()
    forecast_kwh = models.DecimalField(max_digits=12, decimal_places=3)

    source = models.CharField(max_length=50, default="forecast")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_forecast_per_source",
                fields=["generator_string", "timestamp", "source"],
            )
        ]
        indexes = [
            models.Index(
                fields=["generator_string", "timestamp"],
                name="forecast_string_ts_idx",
            ),

            models.Index(
                fields=["generator_string", "source", "timestamp"],
                name="forecast_string_source_ts_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.generator_string} "
            f"{self.timestamp} "
            f"→ {self.forecast_kwh} kWh"
        )


class WeatherForecast(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    home = models.ForeignKey(
        "devices.Home",
        on_delete=models.CASCADE,
        related_name="weather_forecasts",
    )

    ts = models.DateTimeField()

    temperature_c = models.FloatField(
        null=True,
        blank=True,
    )

    cloud_cover_pct = models.FloatField(
        null=True,
        blank=True,
    )

    shortwave_radiation_wm2 = models.FloatField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["home", "ts"],
                name="unique_weather_forecast_per_home_ts",
            )
        ]

        indexes = [
            models.Index(
                fields=["home", "ts"],
                name="weather_home_ts_idx",
            ),
        ]

    def __str__(self):
        return f"{self.home} @ {self.ts}"


class WeatherObservation(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    home = models.ForeignKey(
        "devices.Home",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="weather_observations",
    )

    latitude = models.FloatField()
    longitude = models.FloatField()

    timestamp = models.DateTimeField()

    provider = models.CharField(
        max_length=50,
    )

    station_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    temperature_c = models.FloatField(
        null=True,
        blank=True,
    )

    humidity_pct = models.FloatField(
        null=True,
        blank=True,
    )

    pressure_hpa = models.FloatField(
        null=True,
        blank=True,
    )

    cloud_cover_pct = models.FloatField(
        null=True,
        blank=True,
    )

    shortwave_radiation_wm2 = models.FloatField(
        null=True,
        blank=True,
    )

    rainfall_mm = models.FloatField(
        null=True,
        blank=True,
    )

    wind_speed_ms = models.FloatField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "provider",
                    "station_id",
                    "timestamp",
                ],
                name="weather_obs_unique_station_ts",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "latitude",
                    "longitude",
                    "timestamp",
                ],
                name="weather_obs_loc_ts_idx",
            ),
            models.Index(
                fields=[
                    "provider",
                    "timestamp",
                ],
                name="weather_obs_provider_ts_idx",
            ),
        ]

    def __str__(self):
        return f"{self.provider} " f"{self.timestamp}"


class ForecastRun(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    generator_string = models.ForeignKey(
        "producer.GeneratorString",
        on_delete=models.CASCADE,
        related_name="forecast_runs",
    )

    source = models.CharField(
        max_length=50,
    )

    horizon_hours = models.PositiveIntegerField(
        default=24,
    )

    resolution_minutes = models.PositiveIntegerField(
        default=60,
    )

    model_version = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    generated_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "generator_string",
                    "generated_at",
                ],
                name="forecast_run_string_gen_idx",
            ),
        ]

    def __str__(self):
        return f"{self.generator_string} " f"{self.source} " f"{self.generated_at}"


class ForecastValue(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    forecast_run = models.ForeignKey(
        ForecastRun,
        on_delete=models.CASCADE,
        related_name="values",
    )

    timestamp = models.DateTimeField()

    forecast_kwh = models.DecimalField(
        max_digits=12,
        decimal_places=3,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "forecast_run",
                    "timestamp",
                ],
                name="forecast_value_run_ts_unique",
            )
        ]

        indexes = [
            models.Index(
                fields=[
                    "forecast_run",
                    "timestamp",
                ],
                name="forecast_value_run_ts_idx",
            ),
        ]

    def __str__(self):
        return f"{self.timestamp} " f"→ {self.forecast_kwh}"
