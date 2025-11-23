import os
import json
import time
import httpx
import redis

from shared.secrets import read_secret  # reading docker swarm secrets

# read docker swarm secrets
API_KEY = read_secret("alphavantage_api_key")
# SLACK_WEBHOOK = read_secret("slack_webhook")  # optional
REDIS_PASSWORD = read_secret("redis_password")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # default redis host
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# configuration
ALPHAVANTAGE_URL = os.getenv("ALPHAVANTAGE_URL", "https://www.alphavantage.co/query")
REQUESTS_PER_MIN = int(os.getenv("REQUESTS_PER_MIN", "5"))
REQUESTS_PER_DAY = int(os.getenv("REQUESTS_PER_DAY", "500"))
BATCH_SLEEP_SECONDS = int(os.getenv("BATCH_SLEEP_SECONDS", "60"))
TICKERS_FILE = os.getenv("TICKERS_FILE", "/input/tickers.txt")  # default mounted path

# connect to redis using host + password from secret
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

# load tickers from file
def load_tickers(path=TICKERS_FILE):
    with open(path) as f:
        return [t.strip() for t in f if t.strip()]


# fetch quote from alphavantage
def fetch_global_quote(symbol, client):
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    
    resp = client.get(ALPHAVANTAGE_URL, params=params)
    data = resp.json()
    
    if "Note" in data:
        raise RuntimeError("ALPHAVANTAGE_RATE_LIMIT")
    g = data.get("Global Quote", {})
    
    try:
        price = float(g.get("05. price") or 0.0)
        prev = float(g.get("08. previous close") or 0.0)
        return {"price": price, "previous_close": prev}
    except:
        return None


# store previous close in redis
def store_prev_close(symbol, prev):
    r.set(f"prev_close:{symbol}", json.dumps({"prev_close": prev}), ex=36*3600)


# main premarket loader
def main():
    tickers = load_tickers()
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
            store_prev_close(t, res["previous_close"])
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
