####################
# devices/signals.py
####################

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

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
    