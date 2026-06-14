#####################
# devices/models.py
#####################

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now

created_at = models.DateTimeField(default=now)


User = get_user_model()


class Device(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
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

    home = models.CharField(max_length=100, default="home-1")
    floor = models.CharField(max_length=100, null=True, blank=True)
    room = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DeviceMetric(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="metrics"
    )

    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.identifier} @ {self.created_at}"
    
