import httpx
from shared.secrets import read_secret

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
ALPHAVANTAGE_URL = "https://www.alphavantage.co/query"

def fetch_global_quote(symbol, client=None):
    """
    Fetch global quote from AlphaVantage API.
    client: optional httpx.Client() to reuse connections
    """
    close_client = False
    if client is None:
        client = httpx.Client()
        close_client = True

    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHAVANTAGE_API_KEY}
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
    finally:
        if close_client:
            client.close()
