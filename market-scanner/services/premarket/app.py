import os
import time
import redis
from shared.secrets import read_secret
from shared.alphavantage import fetch_global_quote
from shared.utils import connect_redis, store_prev_close, load_tickers

REDIS_PASSWORD = read_secret("redis_password")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
TICKERS_FILE = os.getenv("TICKERS_FILE", "/input/tickers.txt")
REQUESTS_PER_MIN = int(os.getenv("REQUESTS_PER_MIN", "5"))
REQUESTS_PER_DAY = int(os.getenv("REQUESTS_PER_DAY", "500"))
BATCH_SLEEP_SECONDS = int(os.getenv("BATCH_SLEEP_SECONDS", "60"))

# r = connect_redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    # password=REDIS_PASSWORD,
    decode_responses=True
)

def main():
    tickers = load_tickers(TICKERS_FILE)
    r.delete("tickers")
    r.delete("signals")
    for t in tickers:
        r.rpush("tickers", t)

    import httpx
    client = httpx.Client()
    calls = 0
    daily = 0

    for t in tickers:
        try:
            res = fetch_global_quote(t, client)
        except RuntimeError:
            print("rate limit hit — sleeping")
            time.sleep(BATCH_SLEEP_SECONDS)
            continue

        if res:
            store_prev_close(r, t, res["previous_close"])
            print("stored", t, res["previous_close"])

        calls += 1
        daily += 1

        if calls >= REQUESTS_PER_MIN:
            time.sleep(BATCH_SLEEP_SECONDS)
            calls = 0
        if daily >= REQUESTS_PER_DAY:
            break

    client.close()
    print("premarket finished")

if __name__ == "__main__":
    main()
