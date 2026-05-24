import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="sites",
        verbose_name=_("Tenant"),
    )
    name = models.CharField(_("Name"), max_length=200)
    timezone = models.CharField(_("Timezone"), max_length=64, default="Europe/Berlin")
    address_line1 = models.CharField(
        _("Address line 1"), max_length=200, blank=True, default=""
    )
    address_line2 = models.CharField(
        _("Address line 2"), max_length=200, blank=True, default=""
    )
    postal_code = models.CharField(
        _("Postal code"), max_length=32, blank=True, default=""
    )
    city = models.CharField(_("City"), max_length=64, blank=True, default="")
    country = models.CharField(_("Country"), max_length=2, blank=True, default="DE")

    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        indexes = [models.Index(fields=["tenant", "name"], name="idx_site_tenant_name")]

    def __str__(self):
        return self.name


class Meter(models.Model):
    class Direction(models.TextChoices):
        CONSUMPTION = "CONSUMPTION", _("Consumption")
        GENERATION = "GENERATION", _("Generation")
        BIDIRECTIONAL = "BIDIRECTIONAL", _("Bidirectional")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="meters",
        verbose_name=_("Tenant"),
    )
    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, related_name="meters", verbose_name=_("Site")
    )
    serial = models.CharField(_("Serial/Identifier"), max_length=128, db_index=True)
    direction = models.CharField(
        _("Direction"), max_length=16, choices=Direction.choices
    )
    interval_minutes = models.PositiveSmallIntegerField(
        _("Interval minutes"), default=15
    )  # 15-Min Standard 【1-f9d64c】
    active_from = models.DateField(_("Active from"), null=True, blank=True)
    active_to = models.DateField(_("Active to"), null=True, blank=True)

    class Meta:
        verbose_name = _("Meter")
        verbose_name_plural = _("Meters")
        indexes = [
            models.Index(
                fields=["tenant", "site", "serial"], name="idx_meter_tenant_site_serial"
            )
        ]

    def __str__(self):
        return f"{self.serial} ({self.direction})"


class IntervalReadingRaw(models.Model):
    """
    Immutable RAW ingest layer (Webhook/Polling).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="raw_events",
        verbose_name=_("Tenant"),
    )
    meter = models.ForeignKey(
        Meter,
        on_delete=models.CASCADE,
        related_name="raw_events",
        verbose_name=_("Meter"),
    )
    received_at = models.DateTimeField(_("Received at"), auto_now_add=True)
    payload = models.JSONField(_("Payload"), default=dict)
    source = models.CharField(_("Source"), max_length=32, default="WEBHOOK")
    dedupe_key = models.CharField(
        _("Dedupe key"), max_length=128, db_index=True, blank=True, default=""
    )

    class Meta:
        verbose_name = _("Raw reading event")
        verbose_name_plural = _("Raw reading events")
        indexes = [
            models.Index(
                fields=["tenant", "meter", "-received_at"],
                name="idx_raw_tenant_meter_recv",
            )
        ]


class IntervalReading(models.Model):
    """
    15-Minuten Time Series Werte (curated).
    Unique(meter, ts_start) => idempotent.
    """

    class Quality(models.TextChoices):
        RAW = "RAW", _("Raw")
        VALIDATED = "VALIDATED", _("Validated")
        ESTIMATED = "ESTIMATED", _("Estimated")
        EDITED = "EDITED", _("Edited")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="interval_readings",
        verbose_name=_("Tenant"),
    )
    meter = models.ForeignKey(
        Meter,
        on_delete=models.CASCADE,
        related_name="interval_readings",
        verbose_name=_("Meter"),
    )
    ts_start = models.DateTimeField(_("Interval start"), db_index=True)
    value_kwh = models.DecimalField(_("Energy (kWh)"), max_digits=14, decimal_places=6)
    quality = models.CharField(
        _("Quality"), max_length=12, choices=Quality.choices, default=Quality.RAW
    )
    source = models.CharField(_("Source"), max_length=32, default="WEBHOOK")
    received_at = models.DateTimeField(_("Received at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Interval reading")
        verbose_name_plural = _("Interval readings")
        constraints = [
            models.UniqueConstraint(fields=["meter", "ts_start"], name="uniq_meter_ts"),
        ]
        indexes = [
            models.Index(
                fields=["tenant", "meter", "-ts_start"], name="idx_tenant_meter_ts"
            ),
        ]
