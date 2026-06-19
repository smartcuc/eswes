#############################
# integrations/mqtt_worker.py
#############################

import os
import json
import logging

import paho.mqtt.client as mqtt

from django.db import close_old_connections
from django.utils import timezone

from devices.models import Device, Home
from integrations.live_state import LIVE_STATE
from integrations.mqtt_buffer import push_metric

logger = logging.getLogger(__name__)


def start_mqtt_ingest_thread():

    broker = os.getenv("MQTT_HOST", "127.0.0.1")
    port = int(os.getenv("MQTT_PORT", "1883"))
    username = os.getenv("MQTT_USERNAME", "")
    password = os.getenv("MQTT_PASSWORD", "")
    topic = os.getenv("MQTT_TOPIC", "home/+/device/+")
    qos = int(os.getenv("MQTT_QOS", "1"))

    enabled = os.getenv("MQTT_INGEST_ENABLED", "false").lower() in ["true", "1", "yes"]

    if not username:
        logger.error("mqtt.no_auth_configured")
        return None

    if not enabled:
        logger.info("mqtt.ingest.disabled")
        return None

    client = mqtt.Client(reconnect_on_failure=True)

    client.username_pw_set(username, password)
    #client.tls_set()

    
    def on_connect(c, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info(
                "mqtt.connected",
                extra={"topic": topic, "qos": qos}
            )
            c.subscribe(topic, qos=qos)
        else:
            logger.error(
                "mqtt.connect.failed",
                extra={"rc": rc}
            )


    
    def on_message(c, userdata, msg):
        close_old_connections()

        try:
            logger.debug(
                "mqtt.message.received",
                extra={"topic": msg.topic}
            )

            parts = msg.topic.split("/")

            # ✅ Topic validieren
            if len(parts) != 4 or parts[0] != "home":
                logger.warning(
                    "mqtt.invalid_topic",
                    extra={"topic": msg.topic}
                )
                return

            home_token = parts[1]
            device_id = parts[3]

            # ✅ Home laden
            home = Home.objects.filter(mqtt_token=home_token).first()
            if not home:
                logger.warning(
                    "mqtt.unknown_home",
                    extra={"token": home_token}
                )
                return

            # ✅ Device (Auto Discovery)
            device, created = Device.objects.get_or_create(
                user=home.user,
                home=home,
                identifier=device_id,
                defaults={"name": device_id},
            )

            if created:
                logger.info(
                    "mqtt.device.discovered",
                    extra={"device": device.identifier}
                )

            # ✅ Payload parsen
            try:
                data = json.loads(msg.payload.decode("utf-8"))
            except Exception:
                logger.warning(
                    "mqtt.invalid_json",
                    extra={"payload": msg.payload[:100]}
                )
                return

            power = data.get("power")
            energy = data.get("energy")

            # ✅ Validierung
            if power is None:
                logger.debug(
                    "mqtt.message.ignored.no_power",
                    extra={"topic": msg.topic}
                )
                return

            if not isinstance(power, (int, float)):
                logger.warning(
                    "mqtt.invalid_power_type",
                    extra={"value": power}
                )
                return

            timestamp = timezone.now()
            user_id = str(home.user_id)

            # ✅ Redis Buffer
            push_metric({
                "device_id": device.identifier,
                "user_id": user_id,
                "power": power,
                "energy": energy,
                "timestamp": timestamp.isoformat(),
            })

            # ✅ Live State     
            LIVE_STATE[f"device_{device.id}"] = {
                "type": "device",
                "user_id": user_id,
                "power": power,
                "energy": energy,
                "timestamp": timestamp.isoformat(),
            }

            logger.debug(
                "mqtt.metric.buffered",
                extra={"device": device.identifier, "power": power}
            )

        except Exception:
            logger.exception(
                "mqtt.message.error",
                extra={"topic": msg.topic}
            )

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect_async(broker, port, keepalive=60)
    client.loop_start()

    return client

