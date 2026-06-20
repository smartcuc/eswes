#####################
# devices/models.py
#####################

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# ============================================================
# ✅ HOME
# ============================================================

class Home(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="homes"
    )

    name = models.CharField(max_length=100, default="Home")

    mqtt_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user_id})"


# ============================================================
# ✅ DEVICE ROLE
# ============================================================

class DeviceRole(models.Model):
    key = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


# ============================================================
# ✅ FLOOR
# ============================================================

class Floor(models.Model):
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="floors"
    )
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# ============================================================
# ✅ ROOM
# ============================================================

class Room(models.Model):
    floor = models.ForeignKey(
        Floor,
        on_delete=models.CASCADE,
        related_name="rooms"
    )
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# ============================================================
# ✅ DEVICE
# ============================================================

class Device(models.Model):
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="devices"
    )

    identifier = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    role = models.ForeignKey(
        DeviceRole,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    configured = models.BooleanField(default=False)

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
        return self.name


# ============================================================
# ✅ DEVICE METRIC
# ============================================================

class DeviceMetric(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="metrics"
    )

    timestamp = models.DateTimeField()

    metric = models.CharField(max_length=64)
    value = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=16, blank=True)

    # 🔥 flexible Daten
    data = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["device", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.device.identifier} @ {self.timestamp}"
    