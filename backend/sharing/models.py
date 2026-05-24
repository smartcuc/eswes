import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Community(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="communities",
        verbose_name=_("Tenant"),
    )
    name = models.CharField(_("Name"), max_length=200)
    timezone = models.CharField(_("Timezone"), max_length=64, default="Europe/Berlin")
    resolution_minutes = models.PositiveSmallIntegerField(
        _("Resolution (minutes)"), default=15
    )  # Sharing 15m üblich 【3-5e7426】
    active_from = models.DateField(_("Active from"), null=True, blank=True)
    active_to = models.DateField(_("Active to"), null=True, blank=True)

    class Meta:
        verbose_name = _("Community")
        verbose_name_plural = _("Communities")
        indexes = [models.Index(fields=["tenant", "name"], name="idx_comm_tenant_name")]

    def __str__(self):
        return self.name


class CommunityMember(models.Model):
    """
    Member ist ein Customer in der Community.
    Ein Member kann Producer, Consumer oder beides sein (Prosumer).
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        MEMBER = "MEMBER", _("Member")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name=_("Community"),
    )
    customer = models.ForeignKey(
        "core.Customer",
        on_delete=models.CASCADE,
        related_name="community_memberships",
        verbose_name=_("Customer"),
    )
    role = models.CharField(
        _("Role"), max_length=16, choices=Role.choices, default=Role.MEMBER
    )
    start_date = models.DateField(_("Start date"), null=True, blank=True)
    end_date = models.DateField(_("End date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Community member")
        verbose_name_plural = _("Community members")
        constraints = [
            models.UniqueConstraint(
                fields=["community", "customer"], name="uniq_comm_customer"
            ),
        ]


class CommunityAsset(models.Model):
    """
    Asset repräsentiert Erzeuger/Anlagen (PV, Wind, CHP, Battery, ...).
    Multi-Producer => mehrere Assets/Meters pro Community.
    """

    class AssetType(models.TextChoices):
        PV = "PV", _("PV")
        WIND = "WIND", _("Wind")
        CHP = "CHP", _("CHP")
        BATTERY = "BATTERY", _("Battery")
        GRID = "GRID", _("Grid")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="assets",
        verbose_name=_("Community"),
    )
    owner = models.ForeignKey(
        CommunityMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_assets",
        verbose_name=_("Owner"),
    )
    asset_type = models.CharField(
        _("Asset type"), max_length=16, choices=AssetType.choices
    )
    name = models.CharField(_("Name"), max_length=200)
    metadata = models.JSONField(_("Metadata"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Community asset")
        verbose_name_plural = _("Community assets")


class AssetMeterLink(models.Model):
    """
    Verknüpft Assets mit Zählern; ein Asset kann mehrere Zähler haben.
    role=GENERATION/CONSUMPTION/IMPORT/EXPORT
    """

    class Role(models.TextChoices):
        GENERATION = "GENERATION", _("Generation")
        CONSUMPTION = "CONSUMPTION", _("Consumption")
        IMPORT = "IMPORT", _("Import")
        EXPORT = "EXPORT", _("Export")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(
        CommunityAsset,
        on_delete=models.CASCADE,
        related_name="meter_links",
        verbose_name=_("Asset"),
    )
    meter = models.ForeignKey(
        "metering.Meter",
        on_delete=models.CASCADE,
        related_name="asset_links",
        verbose_name=_("Meter"),
    )
    role = models.CharField(_("Role"), max_length=16, choices=Role.choices)

    class Meta:
        verbose_name = _("Asset meter link")
        verbose_name_plural = _("Asset meter links")
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "meter", "role"], name="uniq_asset_meter_role"
            ),
        ]


class AllocationRuleSet(models.Model):
    """
    Allokationsregel pro Zeitraum (pro-rata, fixed %, priority, hybrid).
    """

    class Method(models.TextChoices):
        PRO_RATA = "PRO_RATA", _("Pro rata by consumption")
        FIXED_PERCENT = "FIXED_PERCENT", _("Fixed percent")
        PRIORITY = "PRIORITY", _("Priority")
        HYBRID = "HYBRID", _("Hybrid")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="rule_sets",
        verbose_name=_("Community"),
    )
    method = models.CharField(
        _("Method"), max_length=32, choices=Method.choices, default=Method.PRO_RATA
    )
    valid_from = models.DateField(_("Valid from"))
    valid_to = models.DateField(_("Valid to"), null=True, blank=True)
    config = models.JSONField(_("Config"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Allocation rule set")
        verbose_name_plural = _("Allocation rule sets")
        indexes = [
            models.Index(
                fields=["community", "valid_from"], name="idx_ruleset_comm_from"
            )
        ]


class AllocationIntervalResult(models.Model):
    """
    Ergebnis pro Community/Member/Slot.
    self_consumed_kwh: Anteil aus Community-Erzeugung
    grid_import_kwh: Restbezug
    export_share_kwh: optional Anteil am Überschuss (für Producer Owner etc.)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="alloc_results",
        verbose_name=_("Tenant"),
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="alloc_results",
        verbose_name=_("Community"),
    )
    member = models.ForeignKey(
        CommunityMember,
        on_delete=models.CASCADE,
        related_name="alloc_results",
        verbose_name=_("Member"),
    )
    ts_start = models.DateTimeField(_("Interval start"), db_index=True)

    self_consumed_kwh = models.DecimalField(
        _("Self-consumed (kWh)"), max_digits=14, decimal_places=6, default=0
    )
    grid_import_kwh = models.DecimalField(
        _("Grid import (kWh)"), max_digits=14, decimal_places=6, default=0
    )
    export_share_kwh = models.DecimalField(
        _("Export share (kWh)"), max_digits=14, decimal_places=6, default=0
    )

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Allocation interval result")
        verbose_name_plural = _("Allocation interval results")
        constraints = [
            models.UniqueConstraint(
                fields=["community", "member", "ts_start"], name="uniq_alloc_slot"
            ),
        ]
        indexes = [
            models.Index(fields=["community", "-ts_start"], name="idx_alloc_comm_ts"),
        ]


class AllocationProducerBreakdown(models.Model):
    """
    Optional: Producer Attribution (wer hat wieviel geliefert).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alloc = models.ForeignKey(
        AllocationIntervalResult,
        on_delete=models.CASCADE,
        related_name="producer_breakdown",
        verbose_name=_("Allocation"),
    )
    asset = models.ForeignKey(
        CommunityAsset, on_delete=models.CASCADE, verbose_name=_("Asset")
    )
    kwh = models.DecimalField(_("kWh"), max_digits=14, decimal_places=6)

    class Meta:
        verbose_name = _("Allocation producer breakdown")
        verbose_name_plural = _("Allocation producer breakdowns")
