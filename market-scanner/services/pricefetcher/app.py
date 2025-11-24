import os
import json
import time
import redis
from shared.secrets import read_secret
from shared.alphavantage import fetch_global_quote
from shared.utils import connect_redis

# REDIS_PASSWORD = read_secret("redis_password")
REDIS_HOST = os.getenv("APP_REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("APP_REDIS_PORT", 6379))
REQUESTS_PER_MIN = int(os.getenv("REQUESTS_PER_MIN", 5))
BATCH_SLEEP_SECONDS = int(os.getenv("BATCH_SLEEP_SECONDS", 60))

# r = connect_redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def main():
    tickers = r.lrange("tickers", 0, -1)
    print(f"pricefetcher: fetching {len(tickers)} tickers")

    import httpx
    client = httpx.Client()
    calls = 0

    for t in tickers:
        try:
            q = fetch_global_quote(t, client)
        except RuntimeError:
            print("rate limit hit — sleeping")
            time.sleep(BATCH_SLEEP_SECONDS)
            continue

        if q:
            r.hset("quotes", t, json.dumps(q))
            print("fetched", t, q)

        calls += 1
        if calls >= REQUESTS_PER_MIN:
            time.sleep(BATCH_SLEEP_SECONDS)
            calls = 0

    client.close()
    print("pricefetcher finished")

if __name__ == "__main__":
    main()
