########################
# metering/models.py
########################


import uuid
from django.db import models
from django.utils import timezone
from django.db.models import Q
from core.ownership import owner_xor_constraints


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Member(models.Model):
    """
    Membership = User ↔ Tenant + Rolle
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    tenant = models.ForeignKey("metering.Tenant", on_delete=models.CASCADE)

    ROLE_CHOICES = [("admin", "Admin"), ("manager", "Manager"), ("viewer", "Viewer")]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "tenant")
        indexes = [models.Index(fields=["tenant"])]

    def __str__(self):
        return f"{self.tenant} / {self.user} ({self.role})"


class MemberEnergyProfile(models.Model):
    member = models.OneToOneField(
        Member, on_delete=models.CASCADE, related_name="energy_profile"
    )

    ENERGY_ROLE = [
        ("consumer", "Consumer"),
        ("producer", "Producer"),
        ("prosumer", "Prosumer"),
    ]
    energy_role = models.CharField(
        max_length=20, choices=ENERGY_ROLE, default="consumer"
    )

    grid_connection_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Meter(models.Model):
    """
    Owner-Pattern:
      - Standalone: owner_user gesetzt, tenant NULL
      - Tenant: owner_member gesetzt, tenant gesetzt
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "metering.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_member = models.ForeignKey(
        "metering.Member", on_delete=models.CASCADE, null=True, blank=True
    )

    serial_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    meter_type = models.CharField(max_length=50, default="electricity")
    manufacturer = models.CharField(max_length=100, blank=True)

    installed_at = models.DateTimeField(null=True, blank=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "serial_number"]),
            models.Index(fields=["tenant"]),
        ]
        constraints = owner_xor_constraints("meter")

    def __str__(self):
        return f"{self.serial_number} ({self.tenant or 'standalone'})"


class MeterRegister(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name="registers")
    obis_code = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("meter", "obis_code")
        indexes = [models.Index(fields=["meter", "obis_code"])]

    def __str__(self):
        return f"{self.meter.serial_number} - {self.obis_code}"


class IntervalReading(models.Model):
    """
    Raw time-series (value = kWh pro Intervall).
    Timescale/Hypertable: Partition auf ts_start.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "metering.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)

    ts_start = models.DateTimeField()
    ts_end = models.DateTimeField(null=True, blank=True)

    received_at = models.DateTimeField(default=timezone.now)

    obis_code = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.CharField(max_length=20, default="kWh")

    source = models.CharField(max_length=20, default="MQTT")

    is_late = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)
    ingestion_delay_seconds = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("meter", "ts_start", "obis_code")
        indexes = [
            models.Index(fields=["tenant", "ts_start"]),
            models.Index(fields=["meter", "ts_start"]),
            models.Index(fields=["tenant", "obis_code", "ts_start"]),
        ]


class AggregatedReading(models.Model):
    """
    Derived layer: time_bucket Aggregationen (15min/hour/day).
    Timescale/Hypertable: Partition auf period_start.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "metering.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)

    member = models.ForeignKey(
        "metering.Member", on_delete=models.CASCADE, null=True, blank=True
    )

    obis_code = models.CharField(max_length=20)
    period_start = models.DateTimeField()
    period_type = models.CharField(max_length=10)

    value = models.DecimalField(max_digits=14, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("meter", "obis_code", "period_start", "period_type")
        indexes = [
            models.Index(fields=["tenant", "period_type", "period_start"]),
            models.Index(fields=["meter", "period_type", "period_start"]),
        ]


class BalanceSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "metering.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )

    meter = models.ForeignKey("metering.Meter", on_delete=models.CASCADE)

    period_start = models.DateTimeField()

    consumption_kwh = models.DecimalField(max_digits=14, decimal_places=3)
    generation_kwh = models.DecimalField(max_digits=14, decimal_places=3)
    self_consumption_kwh = models.DecimalField(max_digits=14, decimal_places=3)
    grid_import_kwh = models.DecimalField(max_digits=14, decimal_places=3)
    grid_export_kwh = models.DecimalField(max_digits=14, decimal_places=3)

    created_at = models.DateTimeField()

    class Meta:
        db_table = "metering_balanceslot"  # ✅ GANZ WICHTIG!
