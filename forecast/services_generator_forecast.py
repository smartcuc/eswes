###############################################
# Python1forecast/services_generator_forecast.py
################################################

from collections import defaultdict

from forecast.models import SolarForecast


def get_generator_forecast(generator):

    buckets = defaultdict(float)

    for string in generator.strings.all():

        forecasts = SolarForecast.objects.filter(
            generator_string=string,
            source="physics",
        )

        for row in forecasts:
            buckets[row.timestamp] += float(row.forecast_kwh)

    return [
        {
            "timestamp": ts,
            "forecast_kw": value,
        }
        for ts, value in sorted(buckets.items())
    ]
