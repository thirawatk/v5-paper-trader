#!/usr/bin/env python3
"""Single-index backtest — NASDAQ 100 only. Quick run."""
import yfinance as yf
import pandas as pd
import numpy as np
import sys, time, json
from datetime import datetime, timedelta
from dataclasses import dataclass

sys.path.insert(0, '/root/.hermes/profiles/trader/scripts')
from backtest_8factor_indices_fast import (
    compute_atr, compute_ema, compute_vwap_bands, compute_obv,
    compute_cmf, compute_mfi, compute_volume_profile_quality_fast,
    score_signal, determine_rr_outcome, detect_candle_pattern,
    Signal, load_universe,
    START_DATE, BACKTEST_START, END_DATE,
    MIN_CONFLUENCE, STOP_ATR_MULT, TP1_R, TP2_R, MAX_HOLD_DAYS,
    FORWARD_DAYS, WEIGHTS, TOTAL_WEIGHT,
)

BASE = '/root/.hermes/profiles/trader/scripts'

def batch_download(tickers):
    """Download in small batches."""
    data = {}
    for i in range(0, len(tickers), 50):
        batch = tickers[i:i+50]
        try:
            result = yf.download(batch, start=START_DATE, end=END_DATE,
                                group_by='ticker', progress=False, threads=True)
        except Exception as e:
            print(f"  Batch error: {e}")
            continue
        for sym in batch:
            try:
                df = result[sym].copy() if len(batch) > 1 else result.copy()
                if df.empty or len(df) < 200:
                    continue
                df = df.dropna(how='all')
                data[sym] = df[['Open','High','Low','Close','Volume']].copy()
            except (KeyError, Exception):
                continue
        time.sleep(0.3)
    return data

def backtest_single(df, ticker, vix_map):
    df["ATR"] = compute_atr(df)
    df["EMA50"] = compute_ema(df["Close"], 50)
    df["EMA200"] = compute_ema(df["Close"], 200)
    df["VWAP"], df["VWAP_Upper"], df["VWAP_Lower"] = compute_vwap_bands(df)
    df["OBV"] = compute_obv(df)
    df["CMF"] = compute_cmf(df)
    df["MFI"] = compute_mfi(df)
    df["VP_Quality"] = compute_volume_profile_quality_fast(df)

    signals = []
    for idx in range(max(200, 50), len(df)):
        date = df.index[idx]
        date_str = date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else str(date)[:10]
        if date_str < BACKTEST_START:
            continue
        vix_val = 15.0
        for d_offset in range(6):
            cd = (date - timedelta(days=d_offset)).strftime("%Y-%m-%d")
            if cd in vix_map:
                vix_val = vix_map[cd]
                break
        scores = score_signal(df, vix_val, idx)
        close = df["Close"].iloc[idx]; atr = df["ATR"].iloc[idx]
        if scores.composite < MIN_CONFLUENCE or scores.direction != "long":
            continue
        if pd.isna(atr) or atr <= 0:
            continue
        rr = determine_rr_outcome(df, idx, close, atr)
        sig = Signal(
            date=date_str, close=round(close,2), atr=round(atr,2),
            composite=round(scores.composite,2), direction=scores.direction,
            long_signals=scores.long_signals,
            trend=round(scores.trend,2), vwap=round(scores.vwap,2),
            obv=round(scores.obv,2), cmf=round(scores.cmf,2),
            mfi=round(scores.mfi,2), vix=round(scores.vix,2),
            vp_quality=round(scores.vp_quality,2), candle=round(scores.candle,2),
            candle_pattern=detect_candle_pattern(df, idx),
            stop_loss=round(rr.get("exit_price",0) if rr["outcome"]=="sl_hit" else close-STOP_ATR_MULT*atr,2),
            tp1=round(close+TP1_R*STOP_ATR_MULT*atr,2),
            tp2=round(close+TP2_R*STOP_ATR_MULT*atr,2),
            outcome=rr["outcome"], bars_to_outcome=rr["bars"], r_multiple=rr["r_multiple"],
        )
        for d in FORWARD_DAYS:
            if idx + d < len(df):
                fc = df["Close"].iloc[idx+d]
                wl = df["Low"].iloc[idx:idx+d+1].min()
                setattr(sig, f"ret_{d}d", round(((fc-close)/close)*100, 2))
                setattr(sig, f"max_dd_{d}d", round(((wl-close)/close)*100, 2))
        signals.append(sig)
    return signals


print("="*70)
print("  8-FACTOR BACKTEST — NASDAQ 100")
print(f"  {BACKTEST_START} → {END_DATE} | Score ≥ {MIN_CONFLUENCE}")
print("="*70)

t_total = time.time()

# VIX
print("\n[0] VIX...")
vix_df = yf.Ticker("^VIX").history(start=START_DATE, end=END_DATE)
vix_map = {idx.strftime("%Y-%m-%d"): vix_df.loc[idx, "Close"] for idx in vix_df.index}

# NASDAQ 100
tickers = load_universe(f"{BASE}/nasdaq100_universe.txt")
print(f"\n[1] NASDAQ 100: {len(tickers)} tickers")

print(f"  Downloading...")
t0 = time.time()
data = batch_download(tickers)
print(f"  Downloaded {len(data)}/{len(tickers)} in {time.time()-t0:.0f}s")

print(f"  Backtesting...")
t0 = time.time()
all_signals = []
for i, (sym, df) in enumerate(data.items()):
    if (i+1) % 30 == 0:
        et = time.time() - t0
        eta = et/(i+1)*len(data) - et
        print(f"  [{i+1}/{len(data)}] {et:.0f}s elapsed, ~{eta:.0f}s remaining, {len(all_signals)} sigs so far")
    sigs = backtest_single(df, sym, vix_map)
    if sigs:
        all_signals.extend([{"ticker": sym, **s.__dict__} for s in sigs])

elapsed = time.time() - t_total
n = len(all_signals)
print(f"\n  COMPLETE: {n} signals in {elapsed:.0f}s ({elapsed/60:.1f} min)")

if n == 0:
    print("No signals found.")
    sys.exit(0)

# ── R:R STATS ──
outcomes = [s["outcome"] for s in all_signals]
r_vals = [s["r_multiple"] for s in all_signals]
tp2 = outcomes.count("tp2_hit"); tp1 = outcomes.count("tp1_hit")
sl = outcomes.count("sl_hit"); exp = outcomes.count("expired")
winning = tp2 + tp1
total_closed = winning + sl + exp
win_r = round(winning/max(total_closed,1)*100, 1)

winning_v = sum(s["r_multiple"] for s in all_signals if s["outcome"] in ("tp1_hit","tp2_hit"))
losing_v = abs(sum(s["r_multiple"] for s in all_signals if s["outcome"]=="sl_hit"))
pf = round(winning_v/max(losing_v,0.001), 2)
avg_r = round(np.mean(r_vals), 2)
bars = [s["bars_to_outcome"] for s in all_signals if s["bars_to_outcome"] > 0]
composites = [s["composite"] for s in all_signals]

print(f"\n{'▓'*70}")
print(f"  R:R OUTCOMES (Stop={STOP_ATR_MULT}×ATR | TP1={TP1_R}R | TP2={TP2_R}R | Max={MAX_HOLD_DAYS}d)")
print(f"{'▓'*70}")
print(f"  Signals:     {n}")
print(f"  TP2:         {tp2} ({round(tp2/n*100,1)}%)")
print(f"  TP1:         {tp1} ({round(tp1/n*100,1)}%)")
print(f"  Stop Loss:   {sl} ({round(sl/n*100,1)}%)")
print(f"  Expired:     {exp} ({round(exp/n*100,1)}%)")
print(f"  Win Rate:    {win_r}%")
print(f"  Avg R:       {avg_r:+.2f}")
print(f"  Profit Factor: {pf}")
print(f"  Avg Bars:    {round(np.mean(bars),1) if bars else 0}")
print(f"  Avg Score:   {round(np.mean(composites),2) if composites else 0}")

# ── SCORE BANDS ──
print(f"\n{'─'*70}")
print(f"  SCORE BANDS")
print(f"{'─'*70}")
print(f"  {'Band':<8} {'Count':>6} {'Avg R':>7} {'Win%':>7} {'TP2%':>6} {'SL%':>6}")
for lo, hi, label in [(5,6,"5-6"),(6,7,"6-7"),(7,8,"7-8"),(8,20,"8-10")]:
    bs = [s for s in all_signals if lo <= s["composite"] < hi]
    if not bs: continue
    br = [s["r_multiple"] for s in bs]
    bw = sum(1 for s in bs if s["outcome"] in ("tp1_hit","tp2_hit"))
    bt = bw + sum(1 for s in bs if s["outcome"] in ("sl_hit","expired"))
    btp2 = sum(1 for s in bs if s["outcome"]=="tp2_hit")
    bsl = sum(1 for s in bs if s["outcome"]=="sl_hit")
    print(f"  {label:<8} {len(bs):>6} {np.mean(br):>+6.2f} {round(bw/max(bt,1)*100,1):>6.1f}% "
          f"{round(btp2/max(len(bs),1)*100,1):>5.1f}% {round(bsl/max(len(bs),1)*100,1):>5.1f}%")

# ── FORWARD RETURNS ──
print(f"\n{'─'*70}")
print(f"  FORWARD RETURNS")
print(f"{'─'*70}")
for d in [5, 10, 20]:
    rets = [s[f"ret_{d}d"] for s in all_signals if s[f"ret_{d}d"] != 0]
    if rets:
        wr = sum(1 for r in rets if r > 0)/len(rets)*100
        print(f"  {d:>2}d: Win={wr:.1f}%  Avg={np.mean(rets):+.2f}%  Best={max(rets):+.2f}%  Worst={min(rets):+.2f}%")

# ── TOP/BOTTOM ──
print(f"\n{'─'*70}")
print(f"  TOP 10 BY R:MULTIPLE")
print(f"  {'Ticker':<8} {'Date':<12} {'Score':>6} {'Outcome':>8} {'R':>7} {'20d':>7} {'Bars':>5}")
print(f"  {'-'*58}")
for s in sorted(all_signals, key=lambda x: x["r_multiple"], reverse=True)[:10]:
    print(f"  {s['ticker']:<8} {s['date']:<12} {s['composite']:>5.1f} {s['outcome']:>8} "
          f"{s['r_multiple']:>+6.2f}R {s['ret_20d']:>+6.2f}% {s['bars_to_outcome']:>5}d")

print(f"\n  WORST 5 BY R:MULTIPLE")
print(f"  {'Ticker':<8} {'Date':<12} {'Score':>6} {'Outcome':>8} {'R':>7} {'Bars':>5}")
print(f"  {'-'*48}")
for s in sorted(all_signals, key=lambda x: x["r_multiple"])[:5]:
    print(f"  {s['ticker']:<8} {s['date']:<12} {s['composite']:>5.1f} {s['outcome']:>8} "
          f"{s['r_multiple']:>+6.2f}R {s['bars_to_outcome']:>5}d")

# ── FACTOR CONTRIBUTION ──
print(f"\n{'─'*70}")
print(f"  FACTOR CONTRIBUTION (avg score × weight)")
print(f"{'─'*70}")
factors = [("trend", 2.0), ("vwap", 1.5), ("obv", 1.0), ("cmf", 1.0),
           ("mfi", 1.0), ("vix", 1.5), ("vp_quality", 2.0), ("candle", 1.5)]
for f_name, w in factors:
    vals = [s[f_name] for s in all_signals]
    avg = np.mean(vals)
    pos = sum(1 for v in vals if v>0)/max(len(vals),1)*100
    contrib = avg * w
    bar = '█' * int(abs(avg) * 15)
    print(f"  {f_name:<12} avg={avg:>+6.2f} ×{w:.1f}={contrib:>+6.2f}  pos={pos:>5.1f}%  {bar}")

# Save
out = {"timestamp": datetime.now().isoformat(), "index": "NASDAQ 100",
       "total_signals": n, "avg_r": avg_r, "win_rate_r": win_r,
       "profit_factor": pf, "elapsed_seconds": round(elapsed),
       "tp2": tp2, "tp1": tp1, "sl": sl, "expired": exp,
       "signals": all_signals[:50]}
path = f"{BASE}/backtest_nasdaq100_results.json"
with open(path, "w") as f:
    json.dump(out, f, indent=2, default=str)
print(f"\n  📁 {path}")
print(f"\n  ⚠ Full 3-index run needs longer timeout. This shows NASDAQ 100 results.")
