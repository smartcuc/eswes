############################
# metering/urls_dashboard.py
############################


from django.urls import path
from metering.dashboard_api import MyDashboardView

urlpatterns = [
    # path("dashboard/me/", MyDashboardView.as_view(), name="dashboard-me"),
    path("me/", MyDashboardView.as_view(), name="dashboard-me"),
]
