##########################################################
# scripts/fake_energy_stream.py
##########################################################

import time
import random
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
TOPIC = "energy/devices/main"

client = mqtt.Client()
#client.connect(BROKER)
client.connect("127.0.0.1", 1883, 60)
client.loop_start()

battery_soc = 50

while True:
    hour = time.localtime().tm_hour

    # PV Produktion (nur tagsüber)
    pv = max(0, (hour - 6) * (18 - hour)) / 36 * 10
    pv += random.uniform(-0.5, 0.5)

    # Hausverbrauch
    load = random.uniform(1, 4)

    # Batterie Logik
    if pv > load:
        battery = random.uniform(0.5, 2.0)  # laden
        battery_soc = min(100, battery_soc + battery * 0.2)
    else:
        battery = -random.uniform(0.5, 2.0)  # entladen
        battery_soc = max(0, battery_soc + battery * 0.2)

    payload = {
        "pv_power": round(pv, 2),
        "load_power": round(load, 2),
        "battery_power": round(battery, 2),
        "battery_soc": round(battery_soc, 1),
    }

    client.publish(TOPIC, json.dumps(payload))

    print(payload)

    time.sleep(2)

