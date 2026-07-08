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


# ✅ MQTT cleanup beim Home löschen
@receiver(post_delete, sender=Home)
def delete_home_mqtt(sender, instance, **kwargs):
    if instance.mqtt_username:
        delete_mqtt_user.delay(instance.mqtt_username)


# ✅ Realtime Update bei neuen Metrics


@receiver(post_save, sender=DeviceMetric)
def send_metric_update(sender, instance, created, **kwargs):
    # 💡 UTC-Sicherheit: Wir ignorieren den DB-Zeitstempel für den Live-Cache komplett.
    # Was JETZT im Signal ankommt, wird JETZT in Redis geschrieben.
    if instance.metric_key == "value":
        cache_key = f"device:{instance.device_id}:latest_power"
        cache.set(cache_key, float(instance.value), timeout=3600)

    # Channels / WebSockets abgesichert ausführen
    try:
        channel_layer = get_channel_layer()
        data = {
            "type": "metric_update",      
            "device_id": instance.device_id,
            "value": float(instance.value),
            # Falls dein Frontend einen Zeitstempel im ISO-Format braucht:
            "timestamp": timezone.now().isoformat() # Generiert die korrekte aktuelle Serverzeit
        }

        async_to_sync(channel_layer.group_send)(
            "energy",
            {
                "type": "send_energy_update",  
                "data": data
            }
        )
    except Exception as e:
        import logging
        logging.getLogger("django").error(f"Fehler im Channels-Signal: {e}")


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

    