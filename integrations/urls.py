######################
# integrations/urls.py
######################

from django.urls import path
from integrations.views_live import live_power

urlpatterns = [
    path("live/power/", live_power),
]
