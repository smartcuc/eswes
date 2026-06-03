#############################
# integrations/live_engine.py
#############################

import asyncio
from collections import defaultdict

from metering.models import Meter
from integrations.services_tibber_live import tibber_live_stream_forever


async def run_live_engine(meters):

    tasks = []
    tibber_groups = defaultdict(list)

    for meter in meters:
        if meter.integration_type == "tibber":
            user = meter.owner_user

            if not user or not user.tibber_token:
                continue

            tibber_groups[user.tibber_token].append(meter)

    for token, group_meters in tibber_groups.items():

        print(f"🚀 Tibber stream for {len(group_meters)} meters")

        tasks.append(
            asyncio.create_task(tibber_live_stream_forever(token, group_meters))
        )

    if not tasks:
        print("⚠️ No live streams configured")
        return

    print(f"✅ Live Engine gestartet ({len(tasks)} streams)")

    await asyncio.gather(*tasks, return_exceptions=True)
