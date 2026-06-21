##################
# devices/tasks.py
##################

import os
from celery import shared_task
import subprocess

from .models import Home


@shared_task(bind=True)
def provision_home(self, home_id):
    try:
        home = Home.objects.get(id=home_id)

        subprocess.run([
            "/usr/bin/mosquitto_ctrl", "dynsec", "createClient",
            home.mqtt_username,
            "-u", home.mqtt_username,
            "-p", home.mqtt_password
        ], check=True)

        subprocess.run([
            "/usr/bin/mosquitto_ctrl", "dynsec", "addRoleACL",
            home.mqtt_username,
            "publishClientSend",
            f"home/{home.mqtt_token}/#"
        ], check=True)

        return "OK"

    except Exception as e:
        raise self.retry(exc=e, countdown=5, max_retries=3)


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
    import subprocess

    home = Home.objects.get(id=home_id)

    try:
        subprocess.run(mqtt_cmd(
            "dynsec", "createClient",
            home.mqtt_username,
            "-u", home.mqtt_username,
            "-p", home.mqtt_password
        ), check=True)
      
        subprocess.run(mqtt_cmd(
            "dynsec", "createRole",
            home.mqtt_username
        ), check=False)

        subprocess.run(mqtt_cmd(
            "dynsec", "addRoleACL",
            home.mqtt_username,
            "publishClientSend",
            f"home/{home.mqtt_token}/#"
        ), check=True)

        # publish
        subprocess.run(mqtt_cmd(
            "dynsec", "addRoleACL",
            home.mqtt_username,
            "publishClientSend",
            f"home/{home.mqtt_token}/#"
        ), check=True)

        # subscribe ✅ FIXED
        subprocess.run(mqtt_cmd(
            "dynsec", "addRoleACL",
            home.mqtt_username,
            "subscribePattern",
            f"home/{home.mqtt_token}/#"
        ), check=True)
            
        subprocess.run(mqtt_cmd(
            "dynsec", "addClientRole",
            home.mqtt_username,
            home.mqtt_username
        ), check=True)

        # ✅ jetzt als provisioned markieren
        home.mqtt_provisioned = True
        home.save(update_fields=["mqtt_provisioned"])

        return "OK"

    except Exception as e:
        raise self.retry(exc=e, countdown=5, max_retries=3)


@shared_task
def delete_mqtt_user(username):
    import subprocess
    
    subprocess.run(mqtt_cmd(
        "dynsec", "deleteClient",
        username
    ), check=False)



