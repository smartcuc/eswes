##########################
# energy/mqtt_publisher.py
##########################


import json
import logging
import paho.mqtt.client as mqtt
from django.conf import settings

logger = logging.getLogger("energy.mqtt_publish")


class MqttPublisher:
    def __init__(self):
        self.host = getattr(settings, "MQTT_HOST", "127.0.0.1")
        self.port = int(getattr(settings, "MQTT_PORT", 1883))
        self.username = getattr(settings, "MQTT_USERNAME", "")
        self.password = getattr(settings, "MQTT_PASSWORD", "")
        self.use_tls = getattr(settings, "MQTT_TLS", False)

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if self.username:
            self.client.username_pw_set(self.username, self.password)
        if self.use_tls:
            self.client.tls_set()

        self.client.connect(self.host, self.port, keepalive=30)

    def publish_json(
        self, topic: str, payload: dict, qos: int = 1, retain: bool = False
    ):
        msg = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        res = self.client.publish(topic, msg, qos=qos, retain=retain)
        res.wait_for_publish()
        if res.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT publish failed rc={res.rc} topic={topic}")
        logger.info("published topic=%s qos=%s", topic, qos)
