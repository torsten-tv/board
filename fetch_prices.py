import yfinance as yf
import json
from datetime import datetime, timezone

TICKERS = [
    "BTC-USD",    # BTCUSDT
    "ETH-USD",    # ETHUSDT
    "ORBS-USD",   # ORBS
    "GC=F",       # GOLD (Futures)
    "SI=F",       # XAGUSD (Silber Futures)
    "IAG",        # Iamgold Corp
    "IMG.TO",     # Iamgold TSX
    "BZ=F",       # UKOIL (Brent Crude)
    "WLD-USD",    # WLDUSDT
    "SAP",        # SAP SE
    "NEM",        # Newmont Corp
    "ABX.TO",     # Barrick Gold TSX
    "GDX",        # VanEck Gold Miners ETF
    "CCJ",        # Cameco
    "UEC",        # Uranium Energy
]

# Mapping: original ticker → Yahoo symbol
TICKER_MAP = {
    "BTC-USD":   "BTCUSDT",
    "ETH-USD":   "ETHUSDT",
    "ORBS-USD":  "ORBS",
    "GC=F":      "GOLD",
    "SI=F":      "XAGUSD",
    "IAG":       "IAG",
    "IMG.TO":    "IMG",
    "BZ=F":      "UKOIL",
    "WLD-USD":   "WLDUSDT",
    "SAP":       "SAP",
    "NEM":       "NEM",
    "ABX.TO":    "ABX",
    "GDX":       "GDX",
    "CCJ":       "CCJ",
    "UEC":       "UEC",
}

results = {}
data = yf.download(
    tickers=" ".join(TICKERS),
    period="2d",
    interval="1d",
    group_by="ticker",
    auto_adjust=True,
    progress=False,
)

for yahoo_sym, board_ticker in TICKER_MAP.items():
    try:
        if len(TICKERS) == 1:
            df = data
        else:
            df = data[yahoo_sym] if yahoo_sym in data.columns.get_level_values(0) else None

        if df is None or df.empty:
            continue

        df = df.dropna(subset=["Close"])
        if len(df) < 1:
            continue

        price_today = float(df["Close"].iloc[-1])
        price_prev  = float(df["Close"].iloc[-2]) if len(df) >= 2 else price_today
        change      = round(price_today - price_prev, 4)
        change_pct  = round((change / price_prev) * 100, 2) if price_prev else 0

        results[board_ticker] = {
            "price":      round(price_today, 4),
            "change":     change,
            "change_pct": change_pct,
        }

    except Exception as e:
        print(f"Fehler bei {yahoo_sym}: {e}")

output = {
    "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "prices":  results,
}

with open("prices.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"✓ {len(results)} Kurse gespeichert → prices.json")
print(f"  Stand: {output['updated']}")
for t, v in results.items():
    sign = "+" if v["change"] >= 0 else ""
    print(f"  {t:12} {v['price']:>12.4f}  {sign}{v['change_pct']:.2f}%")
