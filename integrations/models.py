##########################
# integrations/modeles.py
##########################

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class ApiClient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="api_clients",
        verbose_name=_("Tenant"),
    )
    name = models.CharField(_("Name"), max_length=200)
    api_key_hash = models.CharField(_("API key hash"), max_length=200)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("API client")
        verbose_name_plural = _("API clients")


class InboundWebhookEvent(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED"
        OK = "OK", _("OK")
        ERROR = "ERROR", _("Error")
        DUPLICATE = "DUPLICATE", _("Duplicate")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="inbound_events",
        verbose_name=_("Tenant"),
    )

    api_client = models.ForeignKey(
        ApiClient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name=_("API client"),
    )

    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    event_type = models.CharField(max_length=64, default="METER_READING_BATCH")
    payload = models.JSONField(default=dict)

    signature_valid = models.BooleanField(default=False)

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.RECEIVED,  # ✅ wichtig
    )

    error_message = models.TextField(blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "-received_at"]),
            models.Index(fields=["status"]),  # ✅ optional
        ]

    def __str__(self):
        return f"{self.event_type} ({self.status})"
