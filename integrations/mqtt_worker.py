#############################
# integrations/mqtt_worker.py
#############################

import os
import json
import logging

import paho.mqtt.client as mqtt

from django.db import close_old_connections
from django.contrib.auth import get_user_model

from devices.models import Device, DeviceMetric

logger = logging.getLogger(__name__)
User = get_user_model()


def start_mqtt_ingest_thread():
    """
    Startet MQTT Client + loop_start() in einem Hintergrundthread.
    """

    broker = os.getenv("MQTT_HOST", "127.0.0.1")
    port = int(os.getenv("MQTT_PORT", "1883"))
    username = os.getenv("MQTT_USERNAME", "")
    password = os.getenv("MQTT_PASSWORD", "")
    topic = os.getenv("MQTT_TOPIC", "user/+/device/+/realtime")
    qos = int(os.getenv("MQTT_QOS", "1"))
    client_id = os.getenv("MQTT_CLIENT_ID", "energy-mqtt")

    enabled = os.getenv("MQTT_INGEST_ENABLED", "False") == "True"
    if not enabled:
        logger.info("mqtt.ingest.disabled")
        return None

    client = mqtt.Client(client_id=client_id, reconnect_on_failure=True)

    if username:
        client.username_pw_set(username, password)

    # ✅ CONNECT

    def on_connect(c, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info(
                "mqtt.connected",
                extra={"broker": broker, "topic": topic, "qos": qos},
            )
            c.subscribe(topic, qos=qos)
        else:
            logger.error("mqtt.connect.failed", extra={"rc": rc})

    # ✅ MESSAGE HANDLING

    def on_message(c, userdata, msg):
        close_old_connections()

        # ✅ Parse JSON
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            logger.warning("mqtt.invalid_json", extra={"topic": msg.topic})
            return

        # ✅ Topic prüfen -> user/{id}/device/{id}/realtime
        parts = msg.topic.split("/")

        if len(parts) < 5:
            logger.warning("mqtt.invalid_topic", extra={"topic": msg.topic})
            return

        try:
            user_id = int(parts[1])
        except Exception:
            logger.warning("mqtt.invalid_user", extra={"topic": msg.topic})
            return

        device_id = parts[3]

        # ✅ User prüfen
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning("mqtt.unknown_user", extra={"user_id": user_id})
            return

        # ✅ Device holen oder erstellen
        device, created = Device.objects.get_or_create(
            user=user,
            identifier=device_id,
            defaults={"name": device_id},
        )

        if created:
            logger.info(
                "mqtt.device.discovered",
                extra={"user_id": user_id, "device": device_id},
            )

        # ✅ Payload validieren
        if "power" not in data:
            logger.warning(
                "mqtt.missing_power",
                extra={"device": device_id},
            )
            return

        power = data.get("power")

        if not isinstance(power, (int, float)):
            logger.warning(
                "mqtt.invalid_power_type",
                extra={"device": device_id, "value": power},
            )
            return

        # ✅ speichern
        DeviceMetric.objects.create(
            device=device,
            data=data,
        )

        logger.debug(
            "mqtt.metric.created",
            extra={"device": device_id, "power": power},
        )

    # ✅ Bind callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect_async(broker, port, keepalive=60)
    client.loop_start()

    return client
