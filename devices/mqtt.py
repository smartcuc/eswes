#################
# devices/mqtt.py
#################

import os

def mqtt_cmd(*args):
    return [
        os.getenv("MQTT_CTRL_PATH"),
        "-h", os.getenv("MQTT_HOST"),
        "-p", os.getenv("MQTT_PORT", "8883"),
        "--cafile", os.getenv("MQTT_CAFILE"),
        "-u", os.getenv("MQTT_ADMIN_USER"),
        "-P", os.getenv("MQTT_ADMIN_PASSWORD"),
        *args,
    ]
