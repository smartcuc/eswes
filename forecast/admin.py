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

    search_fields = (
        "generator_string__name",
        "generator_string__generator__name",
    )

    ordering = ("-generated_at",)
    date_hierarchy = "generated_at"

    raw_id_fields = ("generator_string",)


@admin.register(ForecastValue)
class ForecastValueAdmin(admin.ModelAdmin):

    list_display = (
        "generator_string",
        "timestamp",
        "forecast_kwh",
        "forecast_run",
        "created_at",
    )

    ordering = ("-timestamp",)

    raw_id_fields = ("forecast_run",)

    @admin.display(ordering="forecast_run__generator_string")
    def generator_string(self, obj):
        return obj.forecast_run.generator_string
