######################
# integrations/urls.py
######################

from django.urls import path

from integrations.views_live import live_power
from .views_monitoring import EnergyHealthView

urlpatterns = [
    path("live/power/", live_power),
    path("energy-health/", EnergyHealthView.as_view()),
]
