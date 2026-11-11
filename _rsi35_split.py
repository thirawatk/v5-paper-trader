"""Regime split of sub-35 RSI names for the 12 Nov report (checks the 'all downtrend' claim)."""
import json
from daily_market_scan import fetch_market_rows, load_universe, COLS
from _breadth_1112 import regime_of

universe = set(load_universe())
counts = {}
for row in fetch_market_rows():
    d = row.get("d")
    if not d or len(d) < len(COLS):
        continue
    r = dict(zip(COLS, d))
    if r["name"] not in universe:
        continue
    if any(r.get(k) is None for k in ("close", "rsi", "sma20", "sma50", "sma200")):
        continue
    if r["close"] <= 1 or r["rsi"] >= 35:
        continue
    reg = regime_of(r["close"], r["sma20"], r["sma50"], r["sma200"])
    counts[reg] = counts.get(reg, 0) + 1
print(json.dumps(counts))
