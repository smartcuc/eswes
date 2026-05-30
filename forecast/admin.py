###################
# forecast/admin.py
###################


from django.contrib import admin
from .models import SolarForecast


@admin.register(SolarForecast)
class SolarForecastAdmin(admin.ModelAdmin):
    list_display = ("tenant", "timestamp", "forecast_kwh", "source", "created_at")
    list_filter = ("tenant", "source")
    raw_id_fields = ("tenant",)
