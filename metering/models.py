########################
# metering/models.py
########################

from django.db import models
from django.conf import settings
import uuid

# =========================================================
# ✅ DOMAIN MODELS
# =========================================================


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "metering_tenant"
        managed = False


class Meter(models.Model):
    id = models.UUIDField(primary_key=True)

    serial_number = models.CharField(max_length=255, null=True)
    meter_type = models.CharField(max_length=64, null=True)

    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column="owner_user_id",
    )

    tenant_id = models.UUIDField(null=True, blank=True)

    # ✅ DAS FEHLT DIR
    tibber_home_id = models.UUIDField(null=True, blank=True)

    # ✅ DAS HIER
    data_resolution = models.CharField(
        max_length=32,
        default="none",
    )

    class Meta:
        db_table = "metering_meter"
        managed = False


class Member(models.Model):
    id = models.UUIDField(primary_key=True)
    tenant_id = models.UUIDField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "metering_member"
        managed = False


class MemberEnergyProfile(models.Model):
    id = models.UUIDField(primary_key=True)
    member_id = models.UUIDField()
    profile_type = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        db_table = "metering_memberenergyprofile"
        managed = False


class MeterRegister(models.Model):
    id = models.UUIDField(primary_key=True)
    meter_id = models.UUIDField()
    obis_code = models.CharField(max_length=32)

    class Meta:
        db_table = "metering_meterregister"
        managed = False


# =========================================================
# ✅ TIMESERIES
# =========================================================


class IntervalReading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    meter_id = models.UUIDField()
    tenant_id = models.UUIDField(null=True)

    ts_start = models.DateTimeField()

    obis_code = models.CharField(max_length=32)
    value = models.FloatField()

    unit = models.CharField(max_length=16)
    source = models.CharField(max_length=32)

    created_at = models.DateTimeField()
    received_at = models.DateTimeField()

    is_late = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)

    class Meta:
        db_table = "metering_intervalreading"
        managed = False


class AggregatedReading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    meter_id = models.UUIDField()
    tenant_id = models.UUIDField(null=True)

    period_start = models.DateTimeField()
    period_type = models.CharField(max_length=16)

    obis_code = models.CharField(max_length=32)
    value = models.FloatField()

    unit = models.CharField(max_length=16)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "metering_aggregatedreading"
        managed = False


# =========================================================
# ✅ BALANCE (DAS HAT DIR GEFehlt)
# =========================================================


class BalanceSlot(models.Model):
    id = models.UUIDField(primary_key=True)

    meter_id = models.UUIDField()
    tenant_id = models.UUIDField(null=True)

    period_start = models.DateTimeField()

    consumption_kwh = models.FloatField()
    generation_kwh = models.FloatField()

    self_consumption_kwh = models.FloatField()
    grid_import_kwh = models.FloatField()
    grid_export_kwh = models.FloatField()

    created_at = models.DateTimeField()

    class Meta:
        db_table = "metering_balanceslot"
        managed = False
