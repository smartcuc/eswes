########################
# metering/models.py
########################

import uuid
from django.db import models
from django.utils import timezone


# 🟢 Tenant (falls noch nicht vorhanden: anpassen!)
class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Member(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# 🔵 Meter
class Meter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    serial_number = models.CharField(
        max_length=100, unique=True, null=True, blank=True  # ✅ temporär erlaubt
    )

    meter_type = models.CharField(max_length=50, default="electricity")
    manufacturer = models.CharField(max_length=100, blank=True)

    installed_at = models.DateTimeField(null=True, blank=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.serial_number} ({self.tenant})"


# 🧩 MeterRegister (OBIS Mapping)
class MeterRegister(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name="registers")

    obis_code = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("meter", "obis_code")

    def __str__(self):
        return f"{self.meter.serial_number} - {self.obis_code}"


# 🔴 Interval Reading
class IntervalReading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)

    # ✅ Zeit vom Gerät (OBIS / DLMS)
    ts_start = models.DateTimeField()

    # ✅ NEU: Zeitpunkt, wann dein System den Wert empfangen hat
    received_at = models.DateTimeField(default=timezone.now)

    # ✅ Late Data Flag
    is_late = models.BooleanField(default=False)

    # ✅ Duplicate Detection
    is_duplicate = models.BooleanField(default=False)

    # ✅ optional: Delay in Sekunden
    ingestion_delay_seconds = models.IntegerField(null=True, blank=True)

    ts_end = models.DateTimeField(null=True, blank=True)

    obis_code = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.CharField(max_length=20, default="kWh")

    source = models.CharField(max_length=20, default="WEBHOOK")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("meter", "ts_start", "obis_code")

        indexes = [
            models.Index(fields=["tenant", "ts_start"]),
            models.Index(fields=["meter", "ts_start"]),
        ]

    def __str__(self):
        return f"{self.meter.serial_number} {self.obis_code} {self.value}"


class AggregatedReading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    member = models.ForeignKey("Member", on_delete=models.CASCADE, null=True)
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)

    obis_code = models.CharField(max_length=20)

    period_start = models.DateTimeField()
    period_type = models.CharField(max_length=10)

    value = models.DecimalField(max_digits=14, decimal_places=3)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("meter", "obis_code", "period_start", "period_type")
