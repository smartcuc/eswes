####################
# devices/routing.py
####################

from django.urls import path
from .consumers import EnergyConsumer

websocket_urlpatterns = [
    path("ws/energy/", EnergyConsumer.as_asgi()),
]
