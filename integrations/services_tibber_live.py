######################################
# integrations/services_tibber_live.py
######################################

import asyncio
import json
import random
import websockets
import requests

from django.utils.dateparse import parse_datetime

from integrations.live_state import LIVE_STATE
from integrations.live_energy_pipeline import process_live_measurement

GRAPHQL_HTTP_URL = "https://api.tibber.com/v1-beta/gql"


# ✅ WebSocket URL dynamisch holen (einmal)
def get_ws_url(token):
    query = """
    {
      viewer {
        websocketSubscriptionUrl
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Django/ESWES 1.0",
    }

    resp = requests.post(GRAPHQL_HTTP_URL, json={"query": query}, headers=headers)
    data = resp.json()

    return data["data"]["viewer"]["websocketSubscriptionUrl"]


# ✅ EIN einzelner Stream (keine DB Writes)
async def tibber_live_stream_multi(token, meters):

    ws_url = get_ws_url(token)

    async with websockets.connect(
        ws_url,
        subprotocols=["graphql-transport-ws"],
        additional_headers={"Authorization": f"Bearer {token}"},
    ) as ws:

        # ✅ INIT
        await ws.send(json.dumps({"type": "connection_init"}))

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if data.get("type") == "connection_ack":
                print("✅ Tibber ACK")
                break

        # ✅ MULTI SUBSCRIBE
        for idx, meter in enumerate(meters):
            query = f"""
            subscription {{
              liveMeasurement(homeId: "{meter.tibber_home_id}") {{
                timestamp
                power
                accumulatedConsumption
              }}
            }}
            """

            await ws.send(
                json.dumps(
                    {"id": str(idx), "type": "subscribe", "payload": {"query": query}}
                )
            )

        print(f"⚡ Subscribed to {len(meters)} meters")

        # ✅ LOOP
        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if data.get("type") != "next":
                continue

            sub_id = data["id"]
            meter = meters[int(sub_id)]

            measurement = data["payload"]["data"]["liveMeasurement"]

            from integrations.live_energy_pipeline import (
                process_live_measurement,
                flush_ready_slots,
            )

            # ✅ Pipeline (IMMER AKTIV)
            process_live_measurement(str(meter.id), measurement)
            await flush_ready_slots()

            ts = parse_datetime(measurement["timestamp"])
            power = measurement["power"] or 0

            LIVE_STATE[str(meter.id)] = {
                "provider": "tibber",
                "power": power,
                "timestamp": ts.isoformat(),
            }

            short_id = str(meter.id).split("-")[0]
            print(f"⚡ {short_id} → {power} W")


# ✅ Reconnect + Backoff


async def tibber_live_stream_forever(token, meters):

    while True:
        try:
            await tibber_live_stream_multi(token, meters)

        except Exception as e:
            print("⚠️ Stream Fehler:", e)

            delay = random.uniform(5, 30)
            print(f"🔄 Reconnect in {delay:.1f}s")

            await asyncio.sleep(delay)
