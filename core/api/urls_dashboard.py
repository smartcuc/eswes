####################################
# core/api/urls_dashboard.py
####################################

from django.urls import path

from core.api.dashboard import (
    DashboardSummaryView,
    DashboardTimeseriesView,
)

urlpatterns = [
    path("summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("timeseries/", DashboardTimeseriesView.as_view(), name="dashboard-timeseries"),
]
