##########################
# integrations/api_urls.py
##########################
import logging

logger = logging.getLogger(__name__)

from django.urls import path
from .views import ingest_readings, EventListView

urlpatterns = [
    path("webhooks/meter-readings/", ingest_readings),
    path("events/", EventListView.as_view()),
]
