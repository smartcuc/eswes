##################
# energy/models.py
##################

import uuid
from django.db import models
from django.db.models import Q


# ---------------------------------------------------------------------
# Helper: wiederverwendbare Check-Constraints pro Model (unique names!)
# ---------------------------------------------------------------------
def owner_xor_constraints(prefix: str):
    """
    Liefert drei Constraints:
    1) XOR owner_user / owner_membership
    2) owner_user -> tenant NULL
    3) owner_membership -> tenant NOT NULL
    """
    return [
        models.CheckConstraint(
            name=f"{prefix}_owner_xor",
            condition=(
                (Q(owner_user__isnull=False) & Q(owner_membership__isnull=True))
                | (Q(owner_user__isnull=True) & Q(owner_membership__isnull=False))
            ),
        ),
        models.CheckConstraint(
            name=f"{prefix}_user_requires_no_tenant",
            condition=(Q(owner_user__isnull=True) | Q(tenant__isnull=True)),
        ),
        models.CheckConstraint(
            name=f"{prefix}_membership_requires_tenant",
            condition=(Q(owner_membership__isnull=True) | Q(tenant__isnull=False)),
        ),
    ]


# ---------------------------------------------------------------------
# Location (ownerfähig)
# ---------------------------------------------------------------------
class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=255, blank=True)

    street = models.CharField(max_length=255, blank=True)
    house_number = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, default="DE")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "city"]),
        ]
        constraints = owner_xor_constraints("location")

    def __str__(self):
        return (
            self.name
            or f"{self.street} {self.house_number}, {self.postal_code} {self.city}"
        )


# ---------------------------------------------------------------------
# EnergyAsset (Basis)
# ---------------------------------------------------------------------
class EnergyAsset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )

    ASSET_TYPE = [
        ("pv", "PV"),
        ("battery", "Battery"),
        ("ev", "EV"),
        ("other", "Other"),
    ]
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE)

    name = models.CharField(max_length=255)
    installed_power_kw = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    installed_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "asset_type"]),
            models.Index(fields=["owner_user", "asset_type"]),
            models.Index(fields=["owner_membership", "asset_type"]),
        ]
        constraints = owner_xor_constraints("energyasset")

    def __str__(self):
        return f"{self.name} ({self.asset_type})"


# ---------------------------------------------------------------------
# PV Details
# ---------------------------------------------------------------------
class EnergyAssetPV(models.Model):
    asset = models.OneToOneField(
        EnergyAsset, on_delete=models.CASCADE, related_name="pv"
    )

    module_manufacturer = models.CharField(max_length=100, blank=True)
    module_type = models.CharField(max_length=100, blank=True)

    inverter_manufacturer = models.CharField(max_length=100, blank=True)
    inverter_type = models.CharField(max_length=100, blank=True)

    tilt_angle = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # Grad
    azimuth = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # Grad (180=Süd)

    number_of_modules = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"PV Details for {self.asset_id}"


# ---------------------------------------------------------------------
# Battery Details
# ---------------------------------------------------------------------
class EnergyAssetBattery(models.Model):
    asset = models.OneToOneField(
        EnergyAsset, on_delete=models.CASCADE, related_name="battery"
    )

    capacity_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    usable_capacity_kwh = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    max_charge_kw = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    max_discharge_kw = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    efficiency = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # z.B. 0.92

    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Battery Details for {self.asset_id}"


# ---------------------------------------------------------------------
# EV Details (optional, falls EV als Asset modelliert wird)
# ---------------------------------------------------------------------
class EnergyAssetEV(models.Model):
    asset = models.OneToOneField(
        EnergyAsset, on_delete=models.CASCADE, related_name="ev"
    )

    battery_capacity_kwh = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    max_charging_power_kw = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # später: target_soc, departure_time, etc.
    def __str__(self):
        return f"EV Details for {self.asset_id}"


# ---------------------------------------------------------------------
# Mapping Asset ↔ Meter (optional aber sehr nützlich)
# ---------------------------------------------------------------------
class AssetMeter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    asset = models.ForeignKey(
        EnergyAsset, on_delete=models.CASCADE, related_name="meter_links"
    )
    meter = models.ForeignKey(
        "core.Meter", on_delete=models.CASCADE, related_name="asset_links"
    )

    RELATION_TYPE = [
        ("generation", "Generation"),
        ("consumption", "Consumption"),
        ("net", "Net (grid)"),
        ("other", "Other"),
    ]
    relation_type = models.CharField(
        max_length=20, choices=RELATION_TYPE, default="other"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("asset", "meter", "relation_type")
        indexes = [
            models.Index(fields=["meter", "relation_type"]),
        ]

    def __str__(self):
        return f"{self.asset} ↔ {self.meter} ({self.relation_type})"


# ---------------------------------------------------------------------
# Device (Smartplug, EV Charger, etc.) – ownerfähig
# ---------------------------------------------------------------------
class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # optional Zuordnung zu Standort / Asset
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )
    asset = models.ForeignKey(
        EnergyAsset, on_delete=models.SET_NULL, null=True, blank=True
    )

    name = models.CharField(max_length=255)

    DEVICE_TYPE = [
        ("meter", "Meter"),
        ("smartplug", "Smart Plug"),
        ("shelly", "Shelly Device"),
        ("pv", "PV Inverter"),
        ("battery", "Battery"),
        ("ev", "EV / Wallbox"),
        ("market", "Market / SpotPrice"),
        ("homeassistant", "HomeAssistant"),
        ("iobroker", "ioBroker"),
        ("ev_charger", "EV Charger"),
        ("battery_controller", "Battery Controller"),
        ("heat_pump", "Heat Pump"),
        ("other", "Other"),
    ]

    device_type = models.CharField(max_length=30, choices=DEVICE_TYPE)

    controllable = models.BooleanField(default=False)

    # später: Auth/Key für Device Ingest
    api_key_hash = models.CharField(max_length=64, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "device_type"]),
            models.Index(fields=["owner_user", "device_type"]),
            models.Index(fields=["owner_membership", "device_type"]),
        ]
        constraints = owner_xor_constraints("device")

    def __str__(self):
        return f"{self.name} ({self.device_type})"


# ---------------------------------------------------------------------
# SmartEnergySettings (Dynamikpreis-Modus: info/auto/hybrid) – ownerfähig
# ---------------------------------------------------------------------
class SmartEnergySettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    MODE = [
        ("info", "Information only"),
        ("auto", "Automatic control"),
        ("hybrid", "Hybrid"),
    ]
    optimization_mode = models.CharField(max_length=20, choices=MODE, default="info")

    allow_direct_control = models.BooleanField(default=False)

    # optionale Detailflags (später ausbauen)
    optimize_ev = models.BooleanField(default=True)
    optimize_battery = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = owner_xor_constraints("smartenergy")

    def __str__(self):
        scope = "standalone" if self.owner_user_id else "tenant"
        return f"SmartEnergySettings({scope}, mode={self.optimization_mode})"


# ---------------------------------------------------------------------
# DeviceCommand (Outbound Steuerung / später Spotpreis-Optimierung)
# ---------------------------------------------------------------------
class DeviceCommand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="commands"
    )
    ts_created = models.DateTimeField(auto_now_add=True)

    command = models.CharField(max_length=64)  # z.B. ev.set_charging_power_w
    payload = models.JSONField(default=dict, blank=True)

    STATUS = [
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("ack", "Acknowledged"),
        ("failed", "Failed"),
    ]
    status = models.CharField(max_length=16, choices=STATUS, default="queued")

    ts_sent = models.DateTimeField(null=True, blank=True)
    ts_ack = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["status", "ts_created"]),
            models.Index(fields=["device", "ts_created"]),
        ]

    def __str__(self):
        return f"{self.device} {self.command} ({self.status})"


# ---------------------------------------------------------------------
# DeviceMetric (Time-series Telemetrie pro Device)
# ---------------------------------------------------------------------
class DeviceMetric(models.Model):
    """
    Generische Telemetrie pro Gerät und Messgröße.
    Beispiele:
      - power_w, energy_wh (SmartPlug/Shelly)
      - pv_power_w, pv_energy_wh (PV)
      - battery_soc, battery_charge_w (Battery)
      - ev_soc, ev_charging_power_w (EV)
      - spot_price_eur_kwh (Market)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="metrics")
    ts = models.DateTimeField()

    metric = models.CharField(max_length=64)  # z.B. power_w, battery_soc, pv_power_w
    value = models.DecimalField(max_digits=18, decimal_places=6)

    unit = models.CharField(max_length=16, blank=True, default="")
    source = models.CharField(max_length=64, blank=True, default="mqtt")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("device", "ts", "metric")
        indexes = [
            models.Index(fields=["device", "ts"]),
            models.Index(fields=["metric", "ts"]),
            models.Index(fields=["ts"]),
        ]

    def __str__(self):
        return f"{self.device} {self.metric}@{self.ts}={self.value}{self.unit}"
