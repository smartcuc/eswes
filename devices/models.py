#####################
# devices/models.py
#####################

import uuid
from django.core.cache import cache

from django.db import models
from django.contrib.auth import get_user_model

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


User = get_user_model()


# ============================================================
# ✅ HOME / STRUCTURE
# ============================================================

class Home(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="homes"
    )
    name = models.CharField(max_length=100)


class Floor(models.Model):
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="floors"
    )
    name = models.CharField(max_length=50)


class Room(models.Model):
    floor = models.ForeignKey(
        Floor,
        on_delete=models.CASCADE,
        related_name="rooms"
    )
    name = models.CharField(max_length=50)


# ============================================================
# ✅ SEMANTIC LAYER (DAS IST DEIN GAMECHANGER)
# ============================================================

class DeviceRole(models.Model):
    """
    Energie-Richtung (für Sankey!)
    """
    key = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


class MetricDefinition(models.Model):
    """
    Definiert mögliche Messwerte (DB-driven UI!)
    """
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class DeviceType(models.Model):
    """
    Gerätetyp (Wärmepumpe, PV, Batterie...)
    """
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    # 👉 entscheidet Sankey-Verhalten!
    role = models.ForeignKey(
        DeviceRole,
        on_delete=models.PROTECT,
        related_name="device_types"
    )

    def __str__(self):
        return self.name


class DeviceTypeMetric(models.Model):
    """
    Welche Metrics ein Type haben darf
    """
    device_type = models.ForeignKey(
        DeviceType,
        on_delete=models.CASCADE,
        related_name="allowed_metrics"
    )
    metric = models.ForeignKey(
        MetricDefinition,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("device_type", "metric")


# ============================================================
# ✅ DEVICE (DEIN KERNOBJEKT)
# ============================================================

class Device(models.Model):

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="devices"
    )

    identifier = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    # ✅ SEMANTIK
    type = models.ForeignKey(
        DeviceType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="devices"
    )

    # optional (kann später automatisch kommen)
    role = models.ForeignKey(
        DeviceRole,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    # ✅ LOCATION
    room = models.ForeignKey(
        Room,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="devices"
    )

    # ✅ SETUP STATUS
    configured = models.BooleanField(default=False)

    # ✅ timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DeviceSelectedMetric(models.Model):
    """
    Welche Metrics DAS Gerät wirklich nutzt
    """
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="selected_metrics"
    )
    metric = models.ForeignKey(
        MetricDefinition,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("device", "metric")


# ============================================================
# ✅ MESSDATEN (bestehend, aber sauber gekoppelt)
# ============================================================

class DeviceMetric(models.Model):
    device = models.ForeignKey(
        "devices.Device",
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

        # ✅ Sicherer Zugriff auf alten Wert
        if not is_new:
            old_value = (
                DeviceMetric.objects.filter(pk=self.pk)
                .values_list("value", flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        # =====================================================
        # ✅ Nur neue oder geänderte Werte
        # =====================================================
        if not is_new:
            if (old_value is None and self.value is None):
                return
            if old_value == self.value:
                return

        # =====================================================
        # ✅ Nur relevante Metrics
        # =====================================================
        if self.metric_key != "power":
            return

        user_id = self.device.home.user_id

        # =====================================================
        # ✅ Throttle (pro User)
        # =====================================================
        cache_key = f"ws_update_{user_id}"

        if cache.get(cache_key):
            return

        cache.set(cache_key, True, timeout=1)

        # =====================================================
        # ✅ Sichere Channel Layer Nutzung
        # =====================================================
        channel_layer = get_channel_layer()

        if not channel_layer:
            return  # ✅ verhindert crash bei fehlender config

        # =====================================================
        # ✅ Event senden
        # =====================================================
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
                    "device_type": self.device.type.key if self.device.type else None,
                },
            },
        )
