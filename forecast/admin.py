###################
# forecast/admin.py
###################

from django.contrib import admin

from .models import (
    SolarForecast,
    ForecastRun,
    ForecastValue,
)


@admin.register(SolarForecast)
class SolarForecastAdmin(admin.ModelAdmin):

    list_display = (
        "generator_string",
        "timestamp",
        "forecast_kwh",
        "source",
    )

    list_filter = ("source",)

    raw_id_fields = ("generator_string",)


@admin.register(ForecastRun)
class ForecastRunAdmin(admin.ModelAdmin):

    list_display = (
        "generator_string",
        "source",
        "generated_at",
        "horizon_hours",
        "resolution_minutes",
        "created_at",
    )

    list_filter = (
        "source",
        "resolution_minutes",
    )

    ordering = ("-generated_at",)

    raw_id_fields = ("generator_string",)


@admin.register(ForecastValue)
class ForecastValueAdmin(admin.ModelAdmin):

    list_display = (
        "forecast_run",
        "timestamp",
        "forecast_kwh",
        "created_at",
    )

    ordering = ("-timestamp",)

    raw_id_fields = ("forecast_run",)
