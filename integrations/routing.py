#########################
# integrations/routing.py
#########################


from django.urls import re_path
from .consumers import EventStreamConsumer

websocket_urlpatterns = [
    re_path(r"^ws/events/$", EventStreamConsumer.as_asgi()),
]
