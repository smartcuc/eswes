######################
# integrations/urls.py
######################

from django.urls import path


from .views_live import live_data
from .views_monitoring import EnergyHealthView

urlpatterns = [
#    path("live/power/", live_power),
    path("live/", live_data),
    path("energy-health/", EnergyHealthView.as_view()),
]
