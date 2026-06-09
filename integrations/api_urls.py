##########################
# integrations/api_urls.py
##########################

import logging

logger = logging.getLogger(__name__)

from django.urls import path

from integrations.views.ingest import ingest_readings
from integrations.views.events import EventListView
from integrations.views.energy_flow import EnergyFlowView

urlpatterns = [
    path("webhooks/meter-readings/", ingest_readings),
    path("events/", EventListView.as_view()),
    path("energy-flow/<slug:tenant_slug>/", EnergyFlowView.as_view()),
]