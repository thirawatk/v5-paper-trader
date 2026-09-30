#!/usr/bin/env python3
"""S&P 500 standalone — uses same optimized engine."""
import yfinance as yf, pandas as pd, numpy as np, sys, time, json
from datetime import datetime, timedelta
from collections import Counter

sys.path.insert(0, '/root/.hermes/profiles/trader/scripts')

# Import all needed from optimized modules
from backtest_8factor_all_fixed import *

BASE = '/root/.hermes/profiles/trader/scripts'

t_total = time.time()
print("S&P 500 BACKTEST")
print("="*60)

# VIX
vix_df = yf.Ticker("^VIX").history(start=START_DATE, end=END_DATE)
vix_map = {idx.strftime("%Y-%m-%d"): vix_df.loc[idx, "Close"] for idx in vix_df.index}

sigs = process_index("S&P 500", f"{BASE}/sp500_universe.txt", vix_map)
n = len(sigs)
elapsed = time.time() - t_total

print(f"\nCOMPLETE: {n} signals in {elapsed/60:.1f} min")

if n == 0:
    print("No signals.")
    sys.exit(0)

outcomes = [s["outcome"] for s in sigs]
r_vals = [s["r_multiple"] for s in sigs]
tp2 = outcomes.count("tp2_hit"); tp1 = outcomes.count("tp1_hit")
sl = outcomes.count("sl_hit"); exp = outcomes.count("expired")
winning = tp2 + tp1; total_cl = winning + sl + exp
wr = round(winning/max(total_cl,1)*100, 1)
wv = sum(s["r_multiple"] for s in sigs if s["outcome"] in ("tp1_hit","tp2_hit"))
lv = abs(sum(s["r_multiple"] for s in sigs if s["outcome"]=="sl_hit"))
pf = round(wv/max(lv,0.001), 2)
ar = round(np.mean(r_vals), 2)
bars = [s["bars_to_outcome"] for s in sigs if s["bars_to_outcome"]>0]
ab = round(np.mean(bars), 1) if bars else 0

print(f"\nR:R: n={n} | TP2={tp2}({round(tp2/n*100,1)}%) TP1={tp1}({round(tp1/n*100,1)}%) SL={sl}({round(sl/n*100,1)}%) Exp={exp}({round(exp/n*100,1)}%)")
print(f"Win={wr}% | AvgR={ar:+.2f} | PF={pf} | AvgBars={ab}")

# Score bands
print(f"\nSCORE BANDS:")
for lo, hi, label in [(5,6,"5-6"),(6,7,"6-7"),(7,8,"7-8"),(8,20,"8-10")]:
    bs = [s for s in sigs if lo <= s["composite"] < hi]
    if not bs: continue
    br = [s["r_multiple"] for s in bs]
    bw = sum(1 for s in bs if s["outcome"] in ("tp1_hit","tp2_hit"))
    bt = bw + sum(1 for s in bs if s["outcome"] in ("sl_hit","expired"))
    print(f"  {label}: n={len(bs)} avgR={np.mean(br):+.2f} win={round(bw/max(bt,1)*100,1)}%")

# Forward returns
for d in [5,10,20]:
    rets = [s[f"ret_{d}d"] for s in sigs if s[f"ret_{d}d"] != 0]
    if rets:
        print(f"  {d:>2}d fwd: Win={sum(1 for r in rets if r>0)/len(rets)*100:.1f}%  Avg={np.mean(rets):+.2f}%")

# Top 5
print(f"\nTOP 5:")
for s in sorted(sigs, key=lambda x: x["r_multiple"], reverse=True)[:5]:
    print(f"  {s['ticker']:<8} {s['date']} sc={s['composite']:.1f} {s['outcome']} {s['r_multiple']:+.2f}R {s['ret_20d']:+.2f}%")

# Factor contrib
print(f"\nFACTOR CONTRIBUTION:")
for f_name, w in [("trend",2.0),("vwap",1.5),("obv",1.0),("cmf",1.0),("mfi",1.0),("vix",1.5),("vp_quality",2.0),("candle",1.5)]:
    vals = [s[f_name] for s in sigs]
    avg = np.mean(vals)
    pos = sum(1 for v in vals if v>0)/max(len(vals),1)*100
    print(f"  {f_name:<12} avg={avg:>+6.2f}  pos={pos:>5.1f}%  {'█'*int(abs(avg)*10)}")

# Most signaled
print(f"\nTOP TICKERS:")
tc = Counter(s["ticker"] for s in sigs)
for ticker, count in tc.most_common(10):
    art = np.mean([s["r_multiple"] for s in sigs if s["ticker"]==ticker])
    print(f"  {ticker:<8}: {count:>3} sigs, avg R={art:+.2f}")

# Save
out = {"index": "S&P 500", "total_signals": n, "avg_r": ar, "win_rate_r": wr,
       "profit_factor": pf, "tp2": tp2, "tp1": tp1, "sl": sl, "expired": exp,
       "elapsed_s": round(elapsed)}
with open(f"{BASE}/backtest_sp500_results.json", "w") as f:
    json.dump(out, f, indent=2, default=str)
print(f"\nSaved.")
