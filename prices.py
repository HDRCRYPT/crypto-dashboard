import requests
import time
import datetime
import os

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# CoinGecko coin IDs -> display ticker
COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
}

# Currencies we want
CURRENCIES = ["usd", "gbp"]


def get_prices():
    """
    Fetch BTC/ETH/SOL in USD and GBP in a single API call.
    Returns:
    {
        "bitcoin": {"usd": 86000, "gbp": 67000},
        "ethereum": {"usd": 2800, "gbp": 2190},
        ...
    }
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(COINS.keys()),
        "vs_currencies": ",".join(CURRENCIES),
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching prices: {e}{RESET}")
        return {}


def print_price_block(title, prices, previous):
    """Print a block of prices for one currency (USD or GBP)."""

    print(f"\n{title}")

    for coin_id, symbol in COINS.items():
        if coin_id not in prices:
            print(f"{symbol}: {RED}N/A{RESET}")
            continue

        price = prices[coin_id]

        prev = previous.get(coin_id)

        # Determine color + arrow
        if prev is None:
            color = YELLOW
            arrow = "·"
        elif price > prev:
            color = GREEN
            arrow = "↑"
        elif price < prev:
            color = RED
            arrow = "↓"
        else:
            color = YELLOW
            arrow = "→"

        # Currency symbol
        curr_symbol = "£" if title == "GBP" else "$"

        print(f"{symbol}: {color}{curr_symbol}{price:,.2f} {arrow}{RESET}")


def main():
    previous_usd = {}
    previous_gbp = {}

    try:
        while True:
            data = get_prices()
            os.system("clear")

            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{now}] Crypto Prices\n")

            if not data:
                print(f"{RED}No data returned from API.{RESET}")
            else:
                # Extract price dictionaries
                usd_prices = {c: data[c]["usd"] for c in COINS if "usd" in data[c]}
                gbp_prices = {c: data[c]["gbp"] for c in COINS if "gbp" in data[c]}

                # Print USD section
                print_price_block("USD", usd_prices, previous_usd)

                # Print GBP section
                print_price_block("GBP", gbp_prices, previous_gbp)

                # Store previous for arrow logic
                previous_usd = usd_prices
                previous_gbp = gbp_prices

            print("\nUpdating again in 2 minutes... (Ctrl+C to quit)")
            time.sleep(120)

    except KeyboardInterrupt:
        print("\nExiting... bye!")


if __name__ == "__main__":
    main()
