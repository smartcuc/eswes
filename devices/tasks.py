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
    


@shared_task(bind=True)
def provision_home(self, home_id):
    import subprocess

    home = Home.objects.get(id=home_id)

    mqtt_host = os.getenv("MQTT_HOST")
    mqtt_port = os.getenv("MQTT_PORT", "8883")
    admin_user = os.getenv("MQTT_ADMIN_USER")
    admin_pass = os.getenv("MQTT_ADMIN_PASSWORD")
    cafile = os.getenv("MQTT_CAFILE")
    ctrl_path = os.getenv("MQTT_CTRL_PATH")

    try:
        subprocess.run([
            ctrl_path,
            "-h", mqtt_host,
            "-p", mqtt_port,
            "--cafile", cafile,
            "-u", admin_user,
            "-P", admin_pass,
            "dynsec", "createClient",
            home.mqtt_username,
            "-u", home.mqtt_username,
            "-p", home.mqtt_password,
        ], check=True)

        subprocess.run([
            "/usr/bin/mosquitto_ctrl", "dynsec", "addRoleACL",
            home.mqtt_username,
            "publishClientSend",
            f"home/{home.mqtt_token}/#"
        ], check=False)

        # ✅ jetzt als provisioned markieren
        home.mqtt_provisioned = True
        home.save(update_fields=["mqtt_provisioned"])

        return "OK"

    except Exception as e:
        raise self.retry(exc=e, countdown=5, max_retries=3)


@shared_task
def delete_mqtt_user(username):
    import subprocess

    subprocess.run([
        "/usr/bin/mosquitto_ctrl", "dynsec", "deleteClient",
        username
    ], check=False)


