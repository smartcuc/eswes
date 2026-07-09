####################
# energy/api/urls.py
####################

from django.urls import path
from .views_fake import fake_dashboard
from .views import dashboard_me, configure_device, chart_data

urlpatterns = [
    path("fake-dashboard/", fake_dashboard),
]


urlpatterns += [
    path("dashboard/me/", dashboard_me),
    path("chart/", chart_data,),
    path("devices/<int:device_id>/configure/", configure_device),
]
