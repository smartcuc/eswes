##########################
# integrations/apps.py
##########################

import os
from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "integrations"

    def ready(self):
        # ✅ verhindert mehrfaches Starten durch Django autoreload
        if os.environ.get("RUN_MAIN") != "true":
            return

        from .mqtt_worker import start_mqtt_ingest_thread
        start_mqtt_ingest_thread()
        