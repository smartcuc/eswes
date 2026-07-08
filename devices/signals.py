####################
# devices/signals.py
####################

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone

from devices.models import DeviceConfig
from devices.serializers import DeviceSerializer

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Home, DeviceMetric
from .tasks import delete_mqtt_user

import logging

logger = logging.getLogger("django")


# ✅ MQTT cleanup beim Home löschen
@receiver(post_delete, sender=Home)
def delete_home_mqtt(sender, instance, **kwargs):
    if instance.mqtt_username:
        delete_mqtt_user.delay(instance.mqtt_username)


# ✅ Realtime Update bei neuen Metrics
@receiver(post_save, sender=DeviceMetric)
def send_metric_update(sender, instance, created, **kwargs):
    # 1. ZUERST IN REDIS SCHREIBEN (Zeitzonen- & UTC-Sicher)
    # Wir erlauben "value" und "power", damit Modbus/MQTT morgen beide funktionieren
    if str(instance.metric_key) in ["value", "power"] and instance.value is not None:
        try:
            cache_key = f"device:{instance.device_id}:latest_power"
            cache.set(cache_key, float(instance.value), timeout=3600)
        except Exception as cache_err:
            logger.error(f"[SIGNAL_CACHE_ERROR] Konnte Redis nicht beschreiben: {cache_err}")

    # 2. CHANNELS / WEBSOCKETS (Komplett isoliert im try-except)
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            data = {
                "type": "metric_update",      
                "device_id": instance.device_id, # Direkt device_id nutzen spart DB-Query
                "device_type": getattr(instance.device, "type", None), # Falls Frontend das braucht
                "value": float(instance.value) if instance.value is not None else 0.0,
                "timestamp": timezone.now().isoformat() # Garantiert aktuelle Serverzeit
            }

            async_to_sync(channel_layer.group_send)(
                "energy",
                {
                    "type": "send_energy_update",  
                    "data": data
                }
            )
    except Exception as e:
        logger.error(f"[SIGNAL_CHANNELS_ERROR] Fehler bei WebSocket-Übertragung: {e}")


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

    