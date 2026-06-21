##################
# devices/tasks.py
##################

import os
import subprocess
from celery import shared_task

from .models import Home


def mqtt_cmd(*args):
    return [
        os.getenv("MQTT_CTRL_PATH"),
        "-h", os.getenv("MQTT_HOST"),
        "-p", os.getenv("MQTT_PORT", "8883"),
        "--cafile", os.getenv("MQTT_CAFILE"),
        "-u", os.getenv("MQTT_ADMIN_USER"),
        "-P", os.getenv("MQTT_ADMIN_PASSWORD"),
        *args
    ]


@shared_task(bind=True)
def provision_home(self, home_id):
    home = Home.objects.get(id=home_id)

    try:
        # 1. Client erstellen
        subprocess.run(mqtt_cmd(
            "dynsec", "createClient",
            home.mqtt_username,
            "-u", home.mqtt_username,
            "-p", home.mqtt_password
        ), check=True)
      
        # 2. Rolle erstellen
        subprocess.run(mqtt_cmd(
            "dynsec", "createRole",
            home.mqtt_username
        ), check=True)

        # ✅ publishPattern (OHNE allow!)
        subprocess.run(mqtt_cmd(
            "dynsec", "addRoleACL",
            home.mqtt_username,
            "publishPattern",
            f"home/{home.mqtt_token}/#",
            "0"
        ), check=True)

        # subscribe
        subprocess.run(mqtt_cmd(
            "dynsec", "addRoleACL",
            home.mqtt_username,
            "subscribePattern",
            f"home/{home.mqtt_token}/#",
            "0"
        ), check=True)
            
        # 5. Rolle dem Client zuweisen
        subprocess.run(mqtt_cmd(
            "dynsec", "addClientRole",
            home.mqtt_username,
            home.mqtt_username
        ), check=True)

        home.mqtt_provisioned = True
        home.save(update_fields=["mqtt_provisioned"])

        return "OK"

    except Exception as e:
        raise self.retry(exc=e, countdown=5, max_retries=3)


@shared_task
def delete_mqtt_user(username):
    subprocess.run(mqtt_cmd(
        "dynsec", "deleteClient",
        username
    ), check=False)
