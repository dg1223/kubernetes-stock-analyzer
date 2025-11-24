import os
import json
import redis
from shared.secrets import read_secret
from shared.utils import connect_redis

REDIS_PASSWORD = read_secret("redis_password")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
DROP_THRESHOLD = float(os.getenv("DROP_THRESHOLD", 3.0))

# r = connect_redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    # password=REDIS_PASSWORD,
    decode_responses=True
)

def main():
    quotes = r.hgetall("quotes")
    alerts = []

    for ticker, raw in quotes.items():
        q = json.loads(raw)
        drop_pct = (q["price"] - q["previous_close"]) / q["previous_close"] * 100
        if drop_pct <= -DROP_THRESHOLD:
            event = {"ticker": ticker, "drop_pct": drop_pct, "current_price": q["price"]}
            r.rpush("signals", json.dumps(event))
            alerts.append(event)

    print(f"coordinator: generated {len(alerts)} alerts")

if __name__ == "__main__":
    main()
