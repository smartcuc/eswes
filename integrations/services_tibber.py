#################################
# integrations/services_tibber.py
#################################

import requests
from django.conf import settings
from django.utils.dateparse import parse_datetime


from core.models import IntervalReading


TIBBER_API_URL = "https://api.tibber.com/v1-beta/gql"


##----temp-------
def get_tibber_home(token):
    query = """
    {
      viewer {
        homes {
          id
          appNickname
        }
      }
    }
    """

    resp = requests.post(
        TIBBER_API_URL,
        json={"query": query},
        headers=tibber_headers(token),
    )

    data = resp.json()
    return data


###################################


def tibber_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_tibber_token(user=None):
    """
    DEV: Fallback aus settings/.env
    PROD: später user-spezifisch
    """
    if user:
        token = getattr(user, "tibber_token", None)
        if token:
            return token

    return settings.TIBBER_DEFAULT_TOKEN


def fetch_tibber_consumption(home_id, token, hours=24):
    query = f"""
    {{
      viewer {{
        home(id: "{home_id}") {{
          consumption(resolution: HOURLY, last: {hours}) {{
            nodes {{
              from
              to
              consumption
            }}
          }}
        }}
      }}
    }}
    """

    resp = requests.post(
        TIBBER_API_URL,
        json={"query": query},
        headers=tibber_headers(token),
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        raise ValueError(data["errors"])

    home = data["data"]["viewer"]["home"]
    if not home:
        raise ValueError("No Tibber home data returned")

    return home["consumption"]["nodes"]


def upsert_tibber_interval_readings(meter, home_id, user=None, hours=24, tenant=None):
    """
    User-basierter Standard:
    - meter: Pflicht
    - user: optional für user-spezifischen Token
    - tenant: optional; falls nicht gesetzt, wird meter.tenant verwendet (kann None sein)
    """
    token = get_tibber_token(user)

    if not token:
        raise ValueError("No Tibber token available")

    effective_tenant = tenant if tenant is not None else getattr(meter, "tenant", None)

    nodes = fetch_tibber_consumption(
        home_id=home_id,
        token=token,
        hours=hours,
    )

    written = 0
    skipped = 0

    for node in nodes:
        consumption = node.get("consumption")
        if consumption is None:
            skipped += 1
            continue

        ts_start = parse_datetime(node["from"])
        ts_end = parse_datetime(node["to"])

        IntervalReading.objects.update_or_create(
            meter=meter,
            ts_start=ts_start,
            obis_code="1.8.0",
            defaults={
                "tenant": effective_tenant,
                "ts_end": ts_end,
                "value": consumption,
                "unit": "kWh",
                "source": "TIBBER",
            },
        )

        written += 1

    return {
        "status": "ok",
        "written": written,
        "skipped": skipped,
        "total": len(nodes),
    }
