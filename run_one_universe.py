#!/usr/bin/env python3
"""Run 8-factor backtest for a single universe to avoid OOM."""
import sys
sys.path.insert(0, '/root/.hermes/profiles/trader/scripts')

# Import everything from the fast script
exec(open('/root/.hermes/profiles/trader/scripts/backtest_8factor_indices_fast.py').read()
     .replace("if __name__ == \"__main__\":\n    main()", ""))

# Override main to run single universe
import yfinance as yf
import time
import json
import numpy as np
from datetime import datetime

universe_name = sys.argv[1] if len(sys.argv) > 1 else "S&P 500"

UNIVERSE_MAP = {
    "NASDAQ 100": get_nasdaq100,
    "S&P 500": get_sp500,
    "Russell 2000": get_russell2000,
}

t0 = time.time()

# Fetch VIX
print("Fetching VIX...")
vix_df = yf.Ticker("^VIX").history(start=START_DATE, end=END_DATE)
vix_map = {idx.strftime("%Y-%m-%d"): vix_df.loc[idx, "Close"] for idx in vix_df.index}

tickers = UNIVERSE_MAP[universe_name]()
print(f"\n{'='*60}")
print(f"  {universe_name} — {len(tickers)} tickers")
print(f"{'='*60}")

raw = run_backtest(universe_name, tickers, vix_map)
results = compute_summary(raw)

elapsed = time.time() - t0

# Print results
n = results["total_signals"]
oc = results.get("outcome_counts", {})
signals = results["signals"]

print(f"\n{'='*60}")
print(f"  R:R OUTCOMES — {universe_name} ({elapsed/60:.1f} min)")

# R:R table
print(f"\n{'Outcome':<12} {'Count':>6} {'%':>7} {'Avg R':>7}")
print("-" * 35)
for outcome in ["tp2_hit", "tp1_hit", "sl_hit", "expired"]:
    cnt = sum(1 for s in signals if s["outcome"] == outcome)
    pct = round(cnt / max(n, 1) * 100, 1)
    avg = round(np.mean([s["r_multiple"] for s in signals if s["outcome"] == outcome]), 2) if cnt > 0 else 0
    label = {"tp2_hit": "TP2 (3.0R)", "tp1_hit": "TP1 (1.5R)", "sl_hit": "Stop Loss", "expired": "Expired"}
    print(f"{label[outcome]:<12} {cnt:>6} {pct:>6.1f}% {avg:>+6.2f}")

wins = sum(1 for s in signals if s["outcome"] in ("tp1_hit", "tp2_hit"))
losses = sum(1 for s in signals if s["outcome"] == "sl_hit")
print("-" * 35)
print(f"{'Win Rate':<12} {wins:>6} {round(wins/max(wins+losses,1)*100,1):>6.1f}%")
print(f"{'Avg R':<12} {'':>6} {round(np.mean([s['r_multiple'] for s in signals]), 2):>+7.2f}")
print(f"{'Profit Factor':<12} {'':>6} {round(results['profit_factor'], 2):>7.2f}")

# Score bands
print(f"\n  SCORE BAND BREAKDOWN")
print(f"  {'Band':<8} {'Count':>6} {'Avg R':>7} {'Win%':>7} {'TP2%':>6} {'SL%':>6}")
all_bands = {"5-6": [], "6-7": [], "7-8": [], "8-10": []}
for s in signals:
    sc = s["composite"]
    if sc < 6: all_bands["5-6"].append(s)
    elif sc < 7: all_bands["6-7"].append(s)
    elif sc < 8: all_bands["7-8"].append(s)
    else: all_bands["8-10"].append(s)
for band_name, bs in all_bands.items():
    if bs:
        br = [s["r_multiple"] for s in bs]
        bw = sum(1 for s in bs if s["outcome"] in ("tp1_hit", "tp2_hit"))
        bt = bw + sum(1 for s in bs if s["outcome"] in ("sl_hit", "expired"))
        btp2 = sum(1 for s in bs if s["outcome"] == "tp2_hit")
        bsl = sum(1 for s in bs if s["outcome"] == "sl_hit")
        print(f"  {band_name:<8} {len(bs):>6} {np.mean(br):>+6.2f} "
              f"{round(bw/max(bt,1)*100,1):>6.1f}% {round(btp2/max(len(bs),1)*100,1):>5.1f}% "
              f"{round(bsl/max(len(bs),1)*100,1):>5.1f}%")

# Top 10 by R
print(f"\n  TOP 10 BY R:MULTIPLE")
for s in sorted(signals, key=lambda x: x["r_multiple"], reverse=True)[:10]:
    print(f"  {s['ticker']:<8} {s['date']}  score={s['composite']:.1f}  "
          f"{s['outcome']:>8}  {s['r_multiple']:>+6.2f}R  {s['ret_20d']:>+7.2f}%")

# Worst 5
print(f"\n  WORST 5 BY R:MULTIPLE")
for s in sorted(signals, key=lambda x: x["r_multiple"])[:5]:
    print(f"  {s['ticker']:<8} {s['date']}  score={s['composite']:.1f}  "
          f"{s['outcome']:>8}  {s['r_multiple']:>+6.2f}R")

# Factor contributions
print(f"\n  FACTOR CONTRIBUTIONS")
factors = ["trend", "vwap", "obv", "cmf", "mfi", "vix", "vp_quality", "candle"]
for f_name in factors:
    vals = [s[f_name] for s in signals]
    avg = np.mean(vals) if vals else 0
    pos_pct = sum(1 for v in vals if v > 0) / max(len(vals), 1) * 100
    bar = "█" * int(abs(avg) * 10)
    print(f"  {f_name:<12} avg={avg:>+6.2f}  pos={pos_pct:>5.1f}%  {bar}")

# Save JSON
out_path = f"/root/.hermes/profiles/trader/scripts/backtest_8factor_{universe_name.replace(' ', '_').replace('&','').lower()}.json"
with open(out_path, "w") as f:
    json.dump({k: v for k, v in results.items() if k != "signals"}, f, indent=2, default=str)
print(f"\n  📁 {out_path}")
