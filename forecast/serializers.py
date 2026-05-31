#########################
# forecast/serializers.py
#########################

from rest_framework import serializers
from forecast.models import SolarForecast


class SolarForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolarForecast
        fields = [
            "tenant",
            "timestamp",
            "forecast_kwh",
            "source",
        ]
