########################
# metering/models.py
########################
from django.db import models


class IntervalReading(models.Model):
    id = models.UUIDField(primary_key=True)

    meter_id = models.UUIDField()
    tenant_id = models.UUIDField(null=True)

    ts_start = models.DateTimeField()

    obis_code = models.CharField(max_length=32)
    value = models.FloatField()

    unit = models.CharField(max_length=16)
    source = models.CharField(max_length=32)

    created_at = models.DateTimeField()
    received_at = models.DateTimeField()

    is_late = models.BooleanField()
    is_duplicate = models.BooleanField()

    class Meta:
        db_table = "metering_intervalreading"
        managed = False
        constraints = []


class AggregatedReading(models.Model):
    id = models.UUIDField(primary_key=True)

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
        constraints = []


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
