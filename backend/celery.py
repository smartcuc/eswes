#####################
# backend/celery.py
#####################

import logging

logger = logging.getLogger(__name__)

"""
Celery App Initialisierung.

- Lädt Django settings via DJANGO_SETTINGS_MODULE
- Konfiguriert Celery über Django settings (CELERY_*)
- Auto-discover: findet tasks.py in INSTALLED_APPS
"""

import os
from celery import Celery
from celery import bootsteps

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


class MQTTIngestStep(bootsteps.StartStopStep):
    requires = {"celery.worker.components:Pool"}

    def __init__(self, worker, **kwargs):
        self.client = None
        super().__init__(worker, **kwargs)

    def start(self, worker):
        # Nur starten, wenn ENV enabled
        if os.getenv("MQTT_INGEST_ENABLED", "False") == "True":
            from integrations.mqtt_worker import start_mqtt_ingest_thread

            self.client = start_mqtt_ingest_thread()

    def stop(self, worker):
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass


app.steps["worker"].add(MQTTIngestStep)
