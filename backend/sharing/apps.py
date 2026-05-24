from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SharingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sharing"
    verbose_name = _("Energy Sharing")
