#!/usr/bin/env python3
"""S&P 500 only — fast run."""
import yfinance as yf, pandas as pd, numpy as np, sys, time, json
from datetime import datetime, timedelta

sys.path.insert(0, '/root/.hermes/profiles/trader/scripts')
from backtest_8factor_indices_fast import *
from _nasdaq_only import batch_download, backtest_single  # reuse

BASE = '/root/.hermes/profiles/trader/scripts'

t_total = time.time()
vix_df = yf.Ticker("^VIX").history(start=START_DATE, end=END_DATE)
vix_map = {idx.strftime("%Y-%m-%d"): vix_df.loc[idx, "Close"] for idx in vix_df.index}

tickers = load_universe(f"{BASE}/sp500_universe.txt")
print(f"S&P 500: {len(tickers)} tickers")

t0 = time.time()
data = batch_download(tickers)
print(f"Downloaded {len(data)}/{len(tickers)} in {time.time()-t0:.0f}s")

t0 = time.time()
all_signals = []
for i, (sym, df) in enumerate(data.items()):
    if (i+1) % 50 == 0:
        et = time.time() - t0
        eta = et/(i+1)*len(data) - et
        print(f"  [{i+1}/{len(data)}] {et:.0f}s, ~{eta:.0f}s left, {len(all_signals)} sigs")
    sigs = backtest_single(df, sym, vix_map)
    if sigs:
        all_signals.extend([{"ticker": sym, **s.__dict__} for s in sigs])

elapsed = time.time() - t_total
n = len(all_signals)
print(f"\nCOMPLETE: {n} signals in {elapsed:.0f}s ({elapsed/60:.1f} min)")

outcomes = [s["outcome"] for s in all_signals]
r_vals = [s["r_multiple"] for s in all_signals]
tp2 = outcomes.count("tp2_hit"); tp1 = outcomes.count("tp1_hit")
sl = outcomes.count("sl_hit"); exp = outcomes.count("expired")
winning = tp2 + tp1; total_closed = winning + sl + exp
win_r = round(winning/max(total_closed,1)*100, 1)
winning_v = sum(s["r_multiple"] for s in all_signals if s["outcome"] in ("tp1_hit","tp2_hit"))
losing_v = abs(sum(s["r_multiple"] for s in all_signals if s["outcome"]=="sl_hit"))
pf = round(winning_v/max(losing_v,0.001), 2)
avg_r = round(np.mean(r_vals), 2)
bars = [s["bars_to_outcome"] for s in all_signals if s["bars_to_outcome"]>0]

print(f"\nR:R: Signals={n} TP2={tp2}({round(tp2/n*100,1)}%) TP1={tp1}({round(tp1/n*100,1)}%) SL={sl}({round(sl/n*100,1)}%) Exp={exp}({round(exp/n*100,1)}%)")
print(f"Win={win_r}% AvgR={avg_r:+.2f} PF={pf} AvgBars={round(np.mean(bars),1)}")

# Score bands
print(f"\nBANDS:")
for lo, hi, label in [(5,6,"5-6"),(6,7,"6-7"),(7,8,"7-8"),(8,20,"8-10")]:
    bs = [s for s in all_signals if lo <= s["composite"] < hi]
    if not bs: continue
    br = [s["r_multiple"] for s in bs]; bw = sum(1 for s in bs if s["outcome"] in ("tp1_hit","tp2_hit"))
    bt = bw + sum(1 for s in bs if s["outcome"] in ("sl_hit","expired"))
    print(f"  {label}: n={len(bs)} avgR={np.mean(br):+.2f} win={round(bw/max(bt,1)*100,1)}%")

# Top 10
print(f"\nTOP 5:")
for s in sorted(all_signals, key=lambda x: x["r_multiple"], reverse=True)[:5]:
    print(f"  {s['ticker']:<8} {s['date']} {s['composite']:.1f} {s['outcome']} {s['r_multiple']:+.2f}R {s['ret_20d']:+.2f}%")

# Save
out = {"index": "S&P 500", "total_signals": n, "avg_r": avg_r, "win_rate_r": win_r,
       "profit_factor": pf, "tp2": tp2, "tp1": tp1, "sl": sl, "expired": exp}
with open(f"{BASE}/backtest_sp500_results.json", "w") as f:
    json.dump(out, f, indent=2, default=str)
print(f"\nSaved.")
