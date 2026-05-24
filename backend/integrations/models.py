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
    received_at = models.DateTimeField(_("Received at"), auto_now_add=True)
    event_type = models.CharField(
        _("Event type"), max_length=64, default="METER_READING_BATCH"
    )
    payload = models.JSONField(_("Payload"), default=dict)
    signature_valid = models.BooleanField(_("Signature valid"), default=False)
    processed_at = models.DateTimeField(_("Processed at"), null=True, blank=True)
    status = models.CharField(
        _("Status"), max_length=16, choices=Status.choices, default=Status.OK
    )
    error_message = models.TextField(_("Error message"), blank=True, default="")

    class Meta:
        verbose_name = _("Inbound webhook event")
        verbose_name_plural = _("Inbound webhook events")
        indexes = [
            models.Index(
                fields=["tenant", "-received_at"], name="idx_event_tenant_recv"
            )
        ]
