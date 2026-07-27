###################
# forecast/admin.py
###################

from django.contrib import admin

from .models import (
    SolarForecast,
    ForecastRun,
    ForecastValue,
)

from forecast.services_pv_accuracy import calculate_forecast_accuracy
from forecast.models_accuracy import ForecastRunAccuracy

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


@admin.register(ForecastRun)
class ForecastRunAdmin(admin.ModelAdmin):

    list_display = (
        "generator_string",
        "source",
        "generated_at",
        "horizon_hours",
        "resolution_minutes",
        "accuracy_mae",
        "accuracy_delta",
        "forecast_total",
        "actual_total",
        "created_at",
    )

    list_filter = (
        "source",
        "resolution_minutes",
    )

    ordering = ("-generated_at",)

    raw_id_fields = ("generator_string",)

    @admin.display(description="MAE (kWh)")
    def accuracy_mae(self, obj):

        accuracy = calculate_forecast_accuracy(obj)

        if accuracy.get("status"):
            return "-"

        return round(
            accuracy["mae_kwh"],
            3,
        )

    @admin.display(description="Δ %")
    def accuracy_delta(self, obj):

        accuracy = calculate_forecast_accuracy(obj)

        if accuracy.get("status"):
            return "-"

        return f"{accuracy['delta_percent']} %"

    @admin.display(description="Forecast kWh")
    def forecast_total(self, obj):

        accuracy = calculate_forecast_accuracy(obj)

        if accuracy.get("status"):
            return "-"

        return accuracy["total_forecast_kwh"]

    @admin.display(description="Actual kWh")
    def actual_total(self, obj):

        accuracy = calculate_forecast_accuracy(obj)

        if accuracy.get("status"):
            return "-"

        return accuracy["total_actual_kwh"]

@admin.register(ForecastRunAccuracy)
class ForecastRunAccuracyAdmin(admin.ModelAdmin):

    list_display = (
        "forecast_run",
        "mae_kwh",
        "delta_percent",
        "points",
        "calculated_at",
    )

    ordering = (
        "-calculated_at",
    )