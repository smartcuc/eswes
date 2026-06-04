############################
# metering/urls_dashboard.py
############################

from django.urls import path
from metering.dashboard_api import (
    MyDashboardView,
    MyDashboardTimeseriesView,
)

urlpatterns = [
    path("me/", MyDashboardView.as_view(), name="dashboard-me"),
    path(
        "me/timeseries/",
        MyDashboardTimeseriesView.as_view(),
        name="dashboard-timeseries",
    ),
]
