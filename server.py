from flask import Flask, jsonify, render_template
import requests
import json
import os
from datetime import datetime


app = Flask(__name__)
@app.route("/")
def dashboard():
    return render_template("dashboard.html")



SAVE_FILE = "last_prices.json"


def get_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd,gbp"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def load_last_prices():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {}


def compare(new, old):
    if old is None: return "·"
    if new > old: return "↑"
    if new < old: return "↓"
    return "→"


@app.route("/api/prices")
def prices_endpoint():
    data = get_prices()
    last = load_last_prices()

    result = {}
    for name, symbol in {
        "bitcoin": "BTC",
        "ethereum": "ETH",
        "solana": "SOL"
    }.items():

        usd = data[name]["usd"]
        gbp = data[name]["gbp"]
        old = last.get(symbol, {}).get("usd")

        arrow = compare(usd, old)

        result[symbol] = {
            "usd": usd,
            "gbp": gbp,
            "arrow": arrow
        }

    # Save new prices for next compare
    with open(SAVE_FILE, "w") as f:
        json.dump({s: {"usd": result[s]["usd"]} for s in result}, f)

    return jsonify({
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prices": result
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
