import requests
import datetime
import tkinter as tk

# Coins and currencies
COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
}

CURRENCIES = ["usd", "gbp"]
REFRESH_MS = 120_000  # 2 minutes

# Style C — Crypto Minimal Palette
BG = "#181818"        # deep charcoal
TEXT = "#EEEEEE"      # clean bright neutral
UP_COLOR = "#7CFFB2"  # mint green
DOWN_COLOR = "#FF8A8A" # soft pastel red
NEUTRAL = "#C8C8C8"   # cool light grey
ACCENT = "#EEEEEE"

# Font scaling (75% of old sizes)
TITLE_FONT = ("Inter", 18, "bold")
SECTION_FONT = ("Inter", 16, "bold")
LABEL_FONT = ("Inter", 14)
PRICE_FONT = ("Inter", 14)

prev_prices = {}

def get_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(COINS), "vs_currencies": ",".join(CURRENCIES)}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return {}

def format_price(coin_id, currency, data):
    key = f"{coin_id}_{currency}"

    if coin_id not in data or currency not in data[coin_id]:
        return "N/A", NEUTRAL

    price = data[coin_id][currency]
    prev = prev_prices.get(key)

    # Determine color + arrow
    if prev is None:
        color = NEUTRAL
        arrow = "·"
    elif price > prev:
        color = UP_COLOR
        arrow = "↑"
    elif price < prev:
        color = DOWN_COLOR
        arrow = "↓"
    else:
        color = NEUTRAL
        arrow = "→"

    prev_prices[key] = price

    symbol = "£" if currency == "gbp" else "$"
    return f"{symbol}{price:,.2f} {arrow}", color

class PriceApp:
    def __init__(self, root):
        self.root = root

        # Window styling
        root.title("Crypto Prices")
        root.configure(bg=BG)
        root.geometry("360x300")
        root.resizable(False, False)

        # Title
        self.title_label = tk.Label(
            root, text="Crypto Prices", font=TITLE_FONT, fg=ACCENT, bg=BG
        )
        self.title_label.pack(pady=(10, 5))

        # Last updated
        self.last_updated = tk.Label(
            root, text="Updating...", font=LABEL_FONT, fg=NEUTRAL, bg=BG
        )
        self.last_updated.pack(pady=(0, 15))

        # USD Section
        self.usd_frame = tk.Frame(root, bg=BG)
        self.usd_frame.pack(anchor="w", padx=20)

        tk.Label(
            self.usd_frame,
            text="USD",
            font=SECTION_FONT,
            fg=ACCENT,
            bg=BG
        ).pack(anchor="w", pady=(0, 3))

        self.usd_rows = {}
        for coin_id, symbol in COINS.items():
            row = tk.Frame(self.usd_frame, bg=BG)
            row.pack(anchor="w", pady=1)
            tk.Label(row, text=f"{symbol}:", fg=TEXT, bg=BG, font=LABEL_FONT).pack(
                side="left", padx=(0, 8)
            )
            price_label = tk.Label(row, text="—", fg=NEUTRAL, bg=BG, font=PRICE_FONT)
            price_label.pack(side="left")
            self.usd_rows[coin_id] = price_label

        # GBP Section
        self.gbp_frame = tk.Frame(root, bg=BG)
        self.gbp_frame.pack(anchor="w", padx=20, pady=(15, 0))

        tk.Label(
            self.gbp_frame,
            text="GBP",
            font=SECTION_FONT,
            fg=ACCENT,
            bg=BG
        ).pack(anchor="w", pady=(0, 3))

        self.gbp_rows = {}
        for coin_id, symbol in COINS.items():
            row = tk.Frame(self.gbp_frame, bg=BG)
            row.pack(anchor="w", pady=1)
            tk.Label(row, text=f"{symbol}:", fg=TEXT, bg=BG, font=LABEL_FONT).pack(
                side="left", padx=(0, 8)
            )
            price_label = tk.Label(row, text="—", fg=NEUTRAL, bg=BG, font=PRICE_FONT)
            price_label.pack(side="left")
            self.gbp_rows[coin_id] = price_label

        self.update_prices()

    def update_prices(self):
        data = get_prices()

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_updated.config(text=f"Last updated: {now}")

        if data:
            for coin_id in COINS:
                # USD
                txt, col = format_price(coin_id, "usd", data)
                self.usd_rows[coin_id].config(text=txt, fg=col)

                # GBP
                txt, col = format_price(coin_id, "gbp", data)
                self.gbp_rows[coin_id].config(text=txt, fg=col)
        else:
            self.last_updated.config(text=f"{now} • API ERROR", fg=DOWN_COLOR)

        # FIXED: No parentheses here!
        self.root.after(REFRESH_MS, self.update_prices)

if __name__ == "__main__":
    root = tk.Tk()
    app = PriceApp(root)
    root.mainloop()
