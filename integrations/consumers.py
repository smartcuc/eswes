###########################
# integrations/consumers.py
###########################

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("events", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("events", self.channel_name)

    async def send_event(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class EventStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("events", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("events", self.channel_name)

    async def send_event(self, event):
        # event["data"] kommt aus Celery group_send
        await self.send(text_data=json.dumps(event["data"]))
