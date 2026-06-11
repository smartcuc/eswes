#############################
# integrations/mqtt_worker.py
#############################

import os
import logging
import paho.mqtt.client as mqtt  # 【5-050db1】

from django.db import close_old_connections

from integrations.models import InboundWebhookEvent
from integrations.tasks import process_inbound_webhook_event
from core.models import Meter
from integrations.mqtt_normalizer import normalize_message

logger = logging.getLogger(__name__)


def start_mqtt_ingest_thread():
    """
    Startet MQTT Client + loop_start() in einem Hintergrundthread.
    Muss in genau EINEM Worker laufen, sonst doppelte Ingestion.
    """

    broker = os.getenv("MQTT_HOST", "127.0.0.1")
    port = int(os.getenv("MQTT_PORT", "1883"))
    username = os.getenv("MQTT_USERNAME", "")
    password = os.getenv("MQTT_PASSWORD", "")
    topic = os.getenv(
        "MQTT_TOPIC", "device/+/realtime"
    )  # Beispiel: device/{SN}/realtime 【3-9d97a7】
    qos = int(os.getenv("MQTT_QOS", "1"))
    client_id = os.getenv("MQTT_CLIENT_ID", "eswes-celery-mqtt")
    profile = os.getenv("MQTT_PROFILE", "generic")

    enabled = os.getenv("MQTT_INGEST_ENABLED", "False") == "True"
    if not enabled:
        logger.info("mqtt.ingest.disabled")
        return None

    client = mqtt.Client(
        client_id=client_id, reconnect_on_failure=True
    )  # reconnect supported 【1-103c95】
    if username:
        client.username_pw_set(username, password)

    def on_connect(c, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info(
                "mqtt.connected", extra={"broker": broker, "topic": topic, "qos": qos}
            )
            c.subscribe(
                topic, qos=qos
            )  # subscribe in on_connect → resubscribe on reconnect 【2-e2a0a1】【6-097c04】
        else:
            logger.error("mqtt.connect.failed", extra={"rc": rc})

    def on_message(c, userdata, msg):
        # wichtig bei Threads: DB connections pflegen
        close_old_connections()

        serial, payload = normalize_message(msg.topic, msg.payload, profile=profile)
        if not serial or not payload:
            logger.warning("mqtt.unparseable", extra={"topic": msg.topic})
            return

        meter = (
            Meter.objects.filter(serial_number=serial).select_related("tenant").first()
        )
        if not meter or not meter.tenant:
            logger.warning(
                "mqtt.unknown_meter", extra={"serial": serial, "topic": msg.topic}
            )
            return

        evt = InboundWebhookEvent.objects.create(
            tenant=meter.tenant,
            event_type="MQTT",
            status=InboundWebhookEvent.Status.RECEIVED,
            payload=payload,
        )

        process_inbound_webhook_event.delay(str(evt.id))
        logger.info(
            "mqtt.event.created", extra={"event_id": str(evt.id), "serial": serial}
        )

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect_async(broker, port, keepalive=60)
    client.loop_start()  # Threaded loop, reconnect handled 【4-8b65b1】【1-103c95】

    return client
