############################################
# forecast / providers / sensor_community.py
############################################

import requests


def fetch_nearby_observations(
    lat,
    lon,
    radius_km=10,
):

    url = "https://data.sensor.community/static/v2/" "data.json"

    response = requests.get(
        url,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
