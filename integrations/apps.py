##########################
# integrations/apps.py
##########################

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IntegrationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "integrations"
    verbose_name = _("Integrations")


class IntegrationsConfig(AppConfig):
    name = "integrations"

    def ready(self):
        from .mqtt_worker import start_mqtt_ingest_thread
        start_mqtt_ingest_thread()