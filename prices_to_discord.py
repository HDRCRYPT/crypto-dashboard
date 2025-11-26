import requests
import datetime
import json
import os
import time

# ▼▼▼ YOUR DISCORD WEBHOOK URL ▼▼▼
WEBHOOK_URL = "https://discord.com/api/webhooks/1443147410950852762/8aTP8jGKcTj13Fzp841X9V6WNLXZRAHdi8CybnovdqaHt2rhjLkQ8D6KzWXVKf9bR6n8"

SAVE_FILE = "last_prices.json"
INTERVAL_MINUTES = 2  # how often to auto-post


# Colors + Emojis for Discord
UP = "🟢↑"
DOWN = "🔴↓"
FLAT = "⚪→"
FIRST = "·"  # first run / no comparison


def get_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd,gbp"}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Price fetch error:", e)
        return None


def load_last_prices():
    if not os.path.exists(SAVE_FILE):
        return {}
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_prices(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print("Save error:", e)


def movement_arrow(new, old):
    if old is None:
        return FIRST
    if new > old:
        return UP
    if new < old:
        return DOWN
    return FLAT


def create_message(data, last):
    if not data:
        return "❌ Failed to fetch prices."

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    coins = {
        "BTC": data["bitcoin"],
        "ETH": data["ethereum"],
        "SOL": data["solana"],
    }

    lines = [
        "📊 **Crypto Prices Update**",
        f"🕒 `{now}`",
        "",
    ]

    for symbol, values in coins.items():
        usd = values["usd"]
        gbp = values["gbp"]

        old_usd = last.get(symbol, {}).get("usd")
        arrow = movement_arrow(usd, old_usd)

        line = f"**{symbol}:** ${usd:,.2f} / £{gbp:,.2f} {arrow}"
        lines.append(line)

    return "\n".join(lines)


def send_to_discord(message):
    payload = {"content": message}

    try:
        r = requests.post(
            WEBHOOK_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        r.raise_for_status()
        print("✔️ Discord updated")
    except Exception as e:
        print("Discord error:", e)


def post_update():
    prices = get_prices()
    last = load_last_prices()

    message = create_message(prices, last)
    send_to_discord(message)

    formatted = {
        "BTC": {"usd": prices["bitcoin"]["usd"]},
        "ETH": {"usd": prices["ethereum"]["usd"]},
        "SOL": {"usd": prices["solana"]["usd"]},
    }
    save_prices(formatted)


def main():
    while True:
        post_update()
        print(f"⏱ Waiting {INTERVAL_MINUTES} minutes...")
        time.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
