import redis
import os
from time import sleep

from shared.secrets import read_secret  # optional: if you put helper in shared

REDIS_PASSWORD = read_secret("redis_password")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
TICKERS_FILE = os.getenv("TICKERS_FILE", "/input/tickers.txt")

r = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD, decode_responses=True)

def load_tickers():
    with open(TICKERS_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def main():
    tickers = load_tickers()
    print(f"premarket: loading {len(tickers)} tickers")

    r.delete("tickers")
    for t in tickers:
        r.rpush("tickers", t)

    r.delete("signals")
    print("premarket: initialization done")

if __name__ == "__main__":
    main()
