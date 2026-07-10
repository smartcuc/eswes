####################
# energy/api/urls.py
####################

from django.urls import path
from .views_fake import fake_dashboard
from .views import dashboard_me, configure_device, chart_data
from .views import export_chart_xlsx, export_chart_csv

urlpatterns = [
    path("fake-dashboard/", fake_dashboard),
]


urlpatterns += [
    path("dashboard/me/", dashboard_me),
    path(
        "chart/",
        chart_data,
    ),
    path("chart/export/xlsx/", export_chart_xlsx),
    path("chart/export/csv/", export_chart_csv),
    path("devices/<int:device_id>/configure/", configure_device),
]
