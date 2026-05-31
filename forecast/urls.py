##################
# forecast/urls.py
##################

from django.urls import path
from forecast.views import (
    forecast_list,
    forecast_sources,
    forecast_summary,
    forecast_recommendation,
    global_forecast,
)

urlpatterns = [
    path("", forecast_list, name="forecast-list"),
    path("sources/", forecast_sources, name="forecast-sources"),
    path("summary/", forecast_summary, name="forecast-summary"),
    path("recommendation/", forecast_recommendation, name="forecast-recommendation"),
    path("global/", global_forecast, name="forecast-global"),
]
