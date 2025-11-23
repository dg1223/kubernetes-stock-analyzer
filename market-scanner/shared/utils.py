import json
import redis

def connect_redis(host="redis", port=6379, password=None):
    return redis.Redis(host=host, port=port, password=password, decode_responses=True)

def store_prev_close(r, symbol, prev, expire_seconds=36*3600):
    r.set(f"prev_close:{symbol}", json.dumps({"prev_close": prev}), ex=expire_seconds)

def load_tickers(path):
    with open(path) as f:
        return [t.strip() for t in f if t.strip()]
