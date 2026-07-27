############################################
# forecast/providers/sensor_community.py
############################################

import logging
import requests

logger = logging.getLogger(__name__)


def fetch_nearby_observations(
    lat,
    lon,
    radius_km=10,
):

    url = "https://data.sensor.community/static/v2/" "data.json"

    try:

        response = requests.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:

        logger.warning(
            "Sensor Community request failed: %s",
            exc,
        )

        return []
