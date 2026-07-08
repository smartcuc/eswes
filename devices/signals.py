####################
# devices/signals.py
####################

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache

from devices.models import DeviceConfig
from devices.serializers import DeviceSerializer

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Home, DeviceMetric
from .tasks import delete_mqtt_user


# ✅ MQTT cleanup beim Home löschen
@receiver(post_delete, sender=Home)
def delete_home_mqtt(sender, instance, **kwargs):
    if instance.mqtt_username:
        delete_mqtt_user.delay(instance.mqtt_username)


# ✅ Realtime Update bei neuen Metrics
@receiver(post_save, sender=DeviceMetric)
def send_metric_update(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()

    # 💡 NEU: Live-Wert für das HTTP-Dashboard in Redis spiegeln
    if instance.metric_key == "value":
        cache_key = f"device:{instance.device_id}:latest_power"
        cache.set(cache_key, float(instance.value), timeout=3600)  # 1 Stunde TTL

    # ✅ Daten sauber bauen
    data = {
        "type": "metric_update",      # für frontend filter
        "device_id": instance.device.id,
        "device_type": getattr(instance.device, "type", None),
        "value": instance.value,
    }

    # ✅ wichtig: Gruppenname muss exakt zum Consumer passen
    async_to_sync(channel_layer.group_send)(
        "energy",
        {
            "type": "send_energy_update",  # ✅ MUSS zum Consumer passen!
            "data": data
        }
    )
    

@receiver(post_save, sender=DeviceConfig)
def send_device_update(sender, instance, created, **kwargs):

    # optional: nur wenn echte Felder gesetzt sind
    if not instance.role and not instance.room and not instance.floor:
        return

    channel_layer = get_channel_layer()

    device = instance.device

    data = {
        "type": "device_update",
        "device": DeviceSerializer(device).data
    }

    async_to_sync(channel_layer.group_send)(
        "devices",
        {
            "type": "send_device_update",
            "data": data
        }
    )

    