####################
# backend/celery.py
#####################

import os
from pathlib import Path
from dotenv import load_dotenv
from celery import Celery, bootsteps
from celery.schedules import crontab

# ✅ .env sauber laden
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ✅ Settings automatisch holen
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "backend.settings.base")
)

app = Celery("backend")

# ✅ Celery nimmt deine Django settings (CELERY_*)
app.config_from_object("django.conf:settings", namespace="CELERY")

# ✅ findet automatisch tasks.py in Apps
app.autodiscover_tasks()


# ✅ ✅ ✅ HIER richtig platzieren!
app.conf.beat_schedule = {
    "update-forecasts-every-hour": {
        "task": "forecast.tasks.update_all_forecasts",
        "schedule": crontab(hour=2, minute=0),  # jeden Tag um 02:00
    },
}


# =========================================================
# MQTT Worker Step
# =========================================================
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
