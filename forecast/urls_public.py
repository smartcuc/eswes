#########################
# forecast/urls_public.py
#########################

from django.urls import path
from forecast.views_public import (
    public_forecast_list,
    public_forecast_recommendation,
)

urlpatterns = [
    path("forecast/", public_forecast_list, name="public-forecast-list"),
    path(
        "forecast/recommendation/",
        public_forecast_recommendation,
        name="public-forecast-recommendation",
    ),
]
