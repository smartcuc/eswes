import redis
from datetime import datetime
import json
import os


from dotenv import load_dotenv

# ✅ ENV laden
load_dotenv()

# ✅ Redis verbinden
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

r = redis.from_url(redis_url, decode_responses=True)


def process_event(event):
    """
    Hier passiert später deine Logik
    """
    print("📦 Event empfangen:")
    print(event)

    # 👉 Dummy Verarbeitung
    print(f"→ Stream: {event['stream']}")
    print(f"→ Timestamp: {event['ts']}")


def run_worker():
    print("🚀 Worker gestartet... wartet auf Events")

    while True:
        try:
            # ✅ blockiert bis Event kommt
            item = r.brpop("stg_queue", timeout=5)

            if not item:
                continue

            _, payload = item

            event = json.loads(payload)

            process_event(event)

        except Exception as e:
            print("❌ Fehler im Worker:", e)


if __name__ == "__main__":
    run_worker()
