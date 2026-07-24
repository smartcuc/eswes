####################################
# forecast/services_home_forecast.py
####################################

from collections import defaultdict

from forecast.models import SolarForecast


def get_home_forecast(home):

    buckets = defaultdict(float)

    for generator in home.generator_systems.all():

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

