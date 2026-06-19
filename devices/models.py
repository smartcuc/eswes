#####################
# devices/models.py
#####################

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Home(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="homes"
    )

    name = models.CharField(max_length=100, default="Home")

    mqtt_token = models.CharField(
        max_length=64,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user_id})"


class Device(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="devices"
    )

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="devices"
    )

    identifier = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    ROLE_CHOICES = [
        ("pv", "PV"),
        ("load", "Load"),
        ("battery", "Battery"),
        ("grid", "Grid"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        null=True,
        blank=True,
    )

    configured = models.BooleanField(default=False)

    home_label = models.CharField(max_length=100, default="home-1")
    floor = models.CharField(max_length=100, null=True, blank=True)
    room = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "identifier")

    def __str__(self):
        return self.name


class DeviceMetric(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="metrics"
    )

    timestamp = models.DateTimeField()
    power_w = models.FloatField(null=True, blank=True)
    energy_kwh = models.FloatField(null=True, blank=True)

    data = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.identifier} @ {self.timestamp}"