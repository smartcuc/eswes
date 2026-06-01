##################################
# integrations/services_sungrow.py
##################################

import requests


class SungrowClient:
    def __init__(self, base_url, username, password, app_key):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.app_key = app_key
        self.token = None

    def authenticate(self):
        """
        Token holen (vereinfachtes Beispiel – musst du ggf. anpassen)
        """
        url = f"{self.base_url}/login"
        payload = {
            "username": self.username,
            "password": self.password,
        }

        headers = {
            "appkey": self.app_key,
        }

        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()

        data = resp.json()
        self.token = data.get("access_token")

        return self.token

    def get_latest_power(self, plant_id):
        """
        Minimal: aktueller Leistungswert holen
        """
        url = f"{self.base_url}/getPower"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "appkey": self.app_key,
        }

        payload = {
            "plantId": plant_id,
        }

        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()

        return resp.json()
