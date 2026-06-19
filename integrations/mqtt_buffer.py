#############################
# integrations/mqtt_buffer.py
#############################

import json
import redis
import uuid
import os

# ✅ aus .env holen (inkl. Passwort)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

r = redis.Redis.from_url(REDIS_URL)

BUFFER_KEY = "mqtt:buffer"


def _json_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def push_metric(data: dict):
    r.lpush(BUFFER_KEY, json.dumps(data, default=_json_serializer))
