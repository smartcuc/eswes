###################
# forecast/admin.py
###################


from django.contrib import admin
from .models import SolarForecast


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
