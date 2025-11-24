import redis
import json
import os

def load_secret(path):
    with open(path, "r") as f:
        return f.read().strip()

REDIS_HOST = os.getenv("APP_REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("APP_REDIS_PORT", 6379))
# REDIS_PASSWORD = load_secret("/run/secrets/redis_password")

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def main():
    print("alertdispatcher: listening for alerts")

    while True:
        item = redis_client.blpop("signals", timeout=5)
        if not item:
            break

        _, raw = item
        alert = json.loads(raw)
        print(f"ALERT: {alert['ticker']} dropped {alert['drop_pct']:.2f}%")

if __name__ == "__main__":
    main()
