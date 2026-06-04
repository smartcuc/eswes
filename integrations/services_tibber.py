#################################
# integrations/services_tibber.py
#################################

import requests
from django.conf import settings
from django.utils.dateparse import parse_datetime

from metering.models import IntervalReading

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
          consumption(resolution: QUARTER_HOURLY, last: {hours * 4})
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
    token = get_tibber_token(user)

    nodes = fetch_tibber_consumption(
        home_id=home_id,
        token=token,
        hours=hours,
    )

    effective_tenant = tenant if tenant is not None else meter.tenant_id

    from django.db import connection

    sql = """
    INSERT INTO metering_intervalreading (
        id,
        meter_id,
        ts_start,
        obis_code,
        value,
        unit,
        source,
        created_at,
        received_at,
        is_late,
        is_duplicate
    )
    VALUES (
        gen_random_uuid(),
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        now(),
        now(),
        false,
        false
    )
    ON CONFLICT DO NOTHING;
    """

    written = 0

    for node in nodes:
        consumption = node.get("consumption")
        if consumption is None:
            continue

        ts_start = parse_datetime(node["from"])

        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                [
                    str(meter.id),
                    ts_start,
                    "1.8.0",
                    consumption,
                    "kWh",
                    "tibber",
                ],
            )

        written += 1

    return {"status": "ok", "written": written}
