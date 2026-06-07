from fastapi import FastAPI
from datetime import datetime
import redis
import json
import os

from dotenv import load_dotenv

# ✅ ENV laden
load_dotenv()

app = FastAPI()

# ✅ Redis Verbindung aus ENV
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

r = redis.from_url(redis_url, decode_responses=True)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/redis-test")
def redis_test():
    try:
        r.ping()
        return {"redis": "connected"}
    except Exception as e:
        return {"redis": "error", "detail": str(e)}


@app.post("/ingest/{stream}")
def ingest(stream: str, payload: dict):

    event = {"stream": stream, "data": payload, "ts": datetime.utcnow().isoformat()}

    # 🔥 HIER passiert der Unterschied
    r.lpush("stg_queue", json.dumps(event))

    return {"status": "queued", "stream": stream}
