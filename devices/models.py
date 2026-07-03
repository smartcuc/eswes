#####################
# devices/models.py
#####################

import uuid
import secrets
from django.core.cache import cache

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


User = get_user_model()


# ============================================================
# ✅ HOME (MQTT + CORE)
# ============================================================

class Home(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="homes"
    )

    name = models.CharField(max_length=100)

    # ✅ MQTT (nur Transport!)
    mqtt_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    mqtt_username = models.CharField(max_length=100, blank=True)
    mqtt_password = models.CharField(max_length=100, blank=True)
    mqtt_provisioned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.mqtt_username:
            self.mqtt_username = str(self.mqtt_token)

        if not self.mqtt_password:
            self.mqtt_password = secrets.token_hex(16)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user_id})"


# ============================================================
# ✅ STRUCTURE (JETZT WIRKLICH UNABHÄNGIG ✅)
# ============================================================

class Floor(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# ============================================================
# ✅ SEMANTIC
# ============================================================

class DeviceRole(models.Model):
    key = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


class MetricDefinition(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class EnergySource(models.Model):
    key = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)

    def __str__(self):
        return self.label


class EnergyGroup(models.Model):
    key = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)

    def __str__(self):
        return self.label


# ============================================================
# ✅ DEVICE (NUR TECHNISCH!)
# ============================================================

class Device(models.Model):

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="devices"
    )

    identifier = models.CharField(max_length=100)
    
    # ✅ NEU: technischer Status
    configured = models.BooleanField(default=False, db_index=True)
    
    active = models.BooleanField(
        default=True,
        db_index=True,
    )

    pending_delete = models.BooleanField(
        default=False,
        db_index=True,
    )

    delete_after = models.DateTimeField(
        null=True,
        blank=True,
    )

    # 🔥 Lifecycle
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    # 🔥 Standard
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("home", "identifier")
        indexes = [
            models.Index(fields=["home", "identifier"]),
        ]

    def __str__(self):
        return self.identifier


# ============================================================
# ✅ DEVICE CONFIG (KERN)
# ============================================================

class DeviceConfig(models.Model):

    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        related_name="config"
    )

    # ✅ Anzeige
    name = models.CharField(max_length=255, blank=True)

    # ✅ Semantik
    role = models.ForeignKey(
        DeviceRole,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    measurement_type = models.CharField(
        max_length=50,
        blank=True
    )

    energy_source = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    energy_group = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    # ✅ Location (frei!)
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE
    )

    floor = models.ForeignKey(
        Floor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    room = models.ForeignKey(
        Room,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ derived
    def display_name(self):
        return self.name or self.device.identifier

    def is_classified(self):
        return (
            self.role is not None
            and bool(self.measurement_type)
            and bool(self.room or self.floor)
        )

    def __str__(self):
        return self.display_name()


# ============================================================
# ✅ DEVICE METRIC (UNVERÄNDERT)
# ============================================================

class DeviceMetric(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="metrics"
    )

    metric_key = models.CharField(max_length=64)
    unit = models.CharField(max_length=16)

    value = models.FloatField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)

    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        old_value = None

        if not is_new:
            old_value = (
                DeviceMetric.objects.filter(pk=self.pk)
                .values_list("value", flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        if not is_new:
            if (old_value is None and self.value is None):
                return
            if old_value == self.value:
                return

        if self.metric_key != "power":
            return

        user_id = self.device.home.user_id

        cache_key = f"ws_update_{user_id}"
        if cache.get(cache_key):
            return
        cache.set(cache_key, True, timeout=1)

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        async_to_sync(channel_layer.group_send)(
            f"energy_{user_id}",
            {
                "type": "send_energy_update",
                "data": {
                    "type": "metric_update",
                    "device_id": self.device_id,
                    "metric": self.metric_key,
                    "value": self.value,
                    "unit": self.unit,
                    "timestamp": self.timestamp.isoformat(),
                },
            },
        )


# ============================================================
# ✅ METRIC AGGREGATIONS
# ============================================================

class DeviceMetric1m(models.Model):
    device = models.ForeignKey("Device", on_delete=models.CASCADE)
    bucket = models.DateTimeField(db_index=True)

    avg = models.FloatField()
    min = models.FloatField()
    max = models.FloatField()
    count = models.IntegerField()

    class Meta:
        unique_together = ("device", "bucket")
        indexes = [
            models.Index(fields=["device", "bucket"]),
        ]


class DeviceMetric5m(models.Model):
    device = models.ForeignKey("Device", on_delete=models.CASCADE)
    bucket = models.DateTimeField(db_index=True)

    avg = models.FloatField()
    min = models.FloatField()
    max = models.FloatField()
    count = models.IntegerField()

    class Meta:
        unique_together = ("device", "bucket")
        indexes = [
            models.Index(fields=["device", "bucket"]),
        ]

    