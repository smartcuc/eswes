####################
# devices/signals.py
####################

from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Home
from .tasks import delete_mqtt_user


@receiver(post_delete, sender=Home)
def delete_home_mqtt(sender, instance, **kwargs):
    delete_mqtt_user.delay(instance.mqtt_username)

