######################
# devices/consumers.py
######################

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EnergyConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = "energy"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_energy_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    
    # ✅ ✅ ✅ NEU
    async def send_device_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

        