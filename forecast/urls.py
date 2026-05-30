##################
# forecast/urls.py
##################

from django.urls import path
from . import views

urlpatterns = [
    # Meter
    path("meter/<uuid:meter_id>/", views.meter_forecast),
    path("meter/<uuid:meter_id>/vs-actual/", views.meter_forecast_vs_actual),
    # User / Tenant
    path("user/", views.user_forecast),
    path("tenant/", views.tenant_forecast),
    # Global
    path("global/", views.global_forecast),
]
