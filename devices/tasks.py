##################
# devices/tasks.py
##################

from celery import shared_task
import subprocess

from .models import Home


@shared_task(bind=True)
def provision_home(self, home_id):
    try:
        home = Home.objects.get(id=home_id)

        subprocess.run([
            "mosquitto_ctrl", "dynsec", "createClient",
            home.mqtt_username,
            "-u", home.mqtt_username,
            "-p", home.mqtt_password
        ], check=True)

        subprocess.run([
            "mosquitto_ctrl", "dynsec", "addRoleACL",
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

    try:
        subprocess.run([
            "mosquitto_ctrl", "dynsec", "createClient",
            home.mqtt_username,
            "-u", home.mqtt_username,
            "-p", home.mqtt_password
        ], check=False)

        subprocess.run([
            "mosquitto_ctrl", "dynsec", "addRoleACL",
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
        "mosquitto_ctrl", "dynsec", "deleteClient",
        username
    ], check=False)


