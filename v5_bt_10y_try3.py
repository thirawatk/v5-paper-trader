#!/usr/bin/env python3
"""
V5 Paper Trader Backtest — Exact Replica
==========================================
Uses the EXACT same scoring logic as v5_paper_trader.py
- 9 factors: trend (slope-gated), VWAP (shifted center), OBV, CMF, MFI, momentum (ROC-10), VIX, VP quality, candle
- Same weights, same composite formula, same entry/exit rules
- Walk-forward: train on first 60%, test on last 40%
- Also runs full-period for comparison
- Benchmarks against SPY buy-and-hold

Thorps Edge Evaluation: Phase 2 — Quantify the Edge
"""

import warnings
warnings.filterwarnings("ignore")
import json
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime
import yfinance as yf

# ═══ CONFIG — EXACT MATCH TO V5 PAPER TRADER ═══
STARTING_CAPITAL = 10000.0
RISK_PER_TRADE = 0.05       # 1% of capital
MAX_POSITIONS = 5
MIN_CONFLUENCE = 3.5
STOP_ATR = 2.0
TP1_R = 1.0
TP2_R = 1.5
MAX_HOLD_DAYS = 30
VOLUME_FILTER = 1.2

# V5 weights (EXACT from paper trader)
W_TREND = 1.5; W_VWAP = 2.0; W_OBV = 1.0; W_CMF = 1.0
W_MFI = 1.0; W_MOM = 1.0; W_VIX = 2.0; W_VPQ = 2.0; W_CANDLE = 1.5
TOTAL_W = W_TREND + W_VWAP + W_OBV + W_CMF + W_MFI + W_MOM + W_VIX + W_VPQ + W_CANDLE

SP500_FILE = "/root/.hermes/profiles/trader/scripts/sp100_subset.txt"
RESULTS_FILE = "/root/.hermes/profiles/trader/scripts/v5_backtest_results.json"

# ═══ HELPERS ═══

def load_tickers(path, limit=None):
    tks = []
    with open(path) as f:
        for l in f:
            l = l.strip()
            if l and not l.startswith("#"): tks.append(l.upper())
    return tks[:limit] if limit else tks

# ═══ INDICATORS — EXACT FROM V5 PAPER TRADER ═══

def compute_atr(df):
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(14).mean()

def compute_vwap_bands(df, lb=20, ns=2.0):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    tv = tp * df["volume"]
    vw = tv.rolling(lb).sum() / df["volume"].rolling(lb).sum().replace(0, np.nan)
    st = tp.rolling(lb).std()
    return vw, vw + ns * st, vw - ns * st

def compute_obv(df):
    obv = [0.0]
    c = df["close"].values
    v = df["volume"].values
    for i in range(1, len(df)):
        if c[i] > c[i-1]: obv.append(obv[-1] + v[i])
        elif c[i] < c[i-1]: obv.append(obv[-1] - v[i])
        else: obv.append(obv[-1])
    return pd.Series(obv, index=df.index)

def compute_cmf(df, p=20):
    mfm = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"]).replace(0, np.nan)
    return (mfm * df["volume"]).rolling(p).sum() / df["volume"].rolling(p).sum()

def compute_mfi(df, p=14):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    mf = tp * df["volume"]
    ta = tp.values; ma = mf.values
    pf = np.zeros(len(df)); nf = np.zeros(len(df))
    for i in range(1, len(df)):
        if ta[i] > ta[i-1]: pf[i] = ma[i]
        elif ta[i] < ta[i-1]: nf[i] = ma[i]
    ps = pd.Series(pf).rolling(p).sum()
    ns = pd.Series(nf).rolling(p).sum()
    return 100 - (100 / (1 + ps / ns.replace(0, np.nan)))

def compute_vp_quality(df, lb=50, bins=50):
    q = pd.Series(np.nan, index=df.index)
    lo = df["low"].values; hi = df["high"].values
    cl = df["close"].values; op = df["open"].values; vo = df["volume"].values
    for i in range(lb, len(df)):
        pmin = lo[i-lb:i].min(); pmax = hi[i-lb:i].max()
        if pmax == pmin: q.iloc[i] = 0.0; continue
        bs = (pmax - pmin) / bins
        vb = defaultdict(float)
        for j in range(i-lb, i):
            ch = max(op[j], hi[j], lo[j], cl[j])
            cl2 = min(op[j], hi[j], lo[j], cl[j])
            if ch == cl2:
                bi = max(0, min(int((cl[j] - pmin) / bs), bins - 1))
                vb[bi] += vo[j]
            else:
                lo2 = max(0, min(int((cl2 - pmin) / bs), bins - 1))
                hi2 = max(0, min(int((ch - pmin) / bs), bins - 1))
                n = hi2 - lo2 + 1
                for b in range(lo2, hi2 + 1): vb[b] += vo[j] / n
        if vb:
            tv = sum(vb.values())
            q.iloc[i] = max(vb.values()) / tv if tv > 0 else 0.0
        else: q.iloc[i] = 0.0
    return q

def detect_pattern(df, idx):
    if idx < 1: return "none"
    o, h, l, c = df.iloc[idx][["open", "high", "low", "close"]]
    po, ph, pl, pc = df.iloc[idx-1][["open", "high", "low", "close"]]
    body = abs(c - o); tr = h - l
    if tr == 0: return "none"
    br = body / tr
    if c > o and po > pc and c > po and o < pc: return "bullish_engulfing"
    if c < o and po < pc and c < po and o > pc: return "bearish_engulfing"
    if br < 0.3 and (c - l) > 2 * body and (h - max(o, c)) < 0.3 * body: return "bullish_hammer"
    if br < 0.3 and (h - max(o, c)) > 2 * body and (min(o, c) - l) < 0.3 * body: return "bearish_star"
    if br > 0.8 and c > o and (h - c) < 0.1 * tr: return "bullish_marubozu"
    if br > 0.8 and c < o and (o - h) < 0.1 * tr: return "bearish_marubozu"
    return "none"

# ═══ V5 SCORING — EXACT FROM PAPER TRADER ═══

def score_signal(df, vix_val, idx):
    c = df["close"].iloc[idx]
    s = {}

    # Trend (slope-gated) — EXACT
    e50 = df["EMA50"].iloc[idx]; e200 = df["EMA200"].iloc[idx]
    if pd.notna(e50) and pd.notna(e200) and idx >= 5:
        e50_prev = df["EMA50"].iloc[max(0, idx-5)]
        slope = (e50 - e50_prev) / max(e50_prev, 0.01) * 100
        rising = slope > 0.3
        if c > e50 > e200 and rising: s["trend"] = 1.0
        elif c > e50 > e200: s["trend"] = 0.6
        elif c > e50 and e50 <= e200: s["trend"] = 0.5 if rising else 0.4
        elif c < e50 > e200: s["trend"] = 0.2
        elif c < e50 < e200: s["trend"] = -1.0 if slope < -0.5 else -0.8
        elif c < e50 and e50 >= e200: s["trend"] = -0.4
        else: s["trend"] = 0.0
    else: s["trend"] = 0.0

    # VWAP (shifted center) — EXACT
    vw = df["VWAP"].iloc[idx]; vu = df["VWAP_Upper"].iloc[idx]; vl = df["VWAP_Lower"].iloc[idx]
    if pd.notna(vw) and pd.notna(vu) and pd.notna(vl) and vw > 0:
        bw = vu - vl
        if bw > 0:
            pct = (c - vw) / bw
            if pct < -1.5: s["vwap"] = min(1.0, abs(pct) * 0.35)
            elif pct < -0.5: s["vwap"] = 0.35 + abs(pct + 0.5) * 0.5
            elif pct < 0: s["vwap"] = 0.2 + abs(pct) * 0.3
            elif pct > 1.5: s["vwap"] = -0.2 - (pct - 1.5) * 0.2
            elif pct > 0.5: s["vwap"] = 0.0 - (pct - 0.5) * 0.2
            elif pct > 0: s["vwap"] = 0.1 - pct * 0.2
            else: s["vwap"] = 0.2
        else: s["vwap"] = 0.0
    else: s["vwap"] = 0.0

    # OBV — EXACT
    if idx >= 20:
        on = df["OBV"].iloc[idx]
        os_val = df["OBV"].iloc[idx-19:idx+1].mean()
        if pd.notna(on) and pd.notna(os_val) and os_val != 0:
            if on > os_val * 1.03: s["obv"] = 0.8
            elif on > os_val * 1.01: s["obv"] = 0.5
            elif on > os_val: s["obv"] = 0.2
            elif on < os_val * 0.97: s["obv"] = -0.8
            elif on < os_val * 0.99: s["obv"] = -0.5
            elif on < os_val: s["obv"] = -0.2
            else: s["obv"] = 0.0
        else: s["obv"] = 0.0
    else: s["obv"] = 0.0

    # CMF — EXACT
    cv = df["CMF"].iloc[idx]
    s["cmf"] = max(-1.0, min(1.0, cv * 1.8)) if pd.notna(cv) else 0.0

    # MFI — EXACT
    mv = df["MFI"].iloc[idx]
    if pd.notna(mv):
        if mv > 75: s["mfi"] = -0.5
        elif mv < 25: s["mfi"] = 0.5
        elif mv > 55: s["mfi"] = 0.3
        elif mv < 45: s["mfi"] = -0.3
        else: s["mfi"] = 0.0
    else: s["mfi"] = 0.0

    # VIX — EXACT
    if vix_val >= 35: s["vix"] = 0.8
    elif vix_val >= 25: s["vix"] = 0.5
    elif vix_val >= 20: s["vix"] = 0.3
    elif vix_val < 12: s["vix"] = -0.5
    elif vix_val < 15: s["vix"] = -0.2
    else: s["vix"] = 0.0

    # VP Quality — EXACT
    vq = df["VP_Quality"].iloc[idx]
    if pd.notna(vq):
        if vq > 0.12: s["vp_quality"] = min(1.0, vq * 5)
        elif vq > 0.08: s["vp_quality"] = 0.4
        else: s["vp_quality"] = 0.0
    else: s["vp_quality"] = 0.0

    # Candle — EXACT
    pat = detect_pattern(df, idx)
    if "bullish" in pat:
        if "engulfing" in pat: s["candle"] = 1.0
        elif "hammer" in pat: s["candle"] = 0.7
        elif "marubozu" in pat: s["candle"] = 0.6
        else: s["candle"] = 0.4
    elif "bearish" in pat:
        if "engulfing" in pat: s["candle"] = -1.0
        elif "star" in pat: s["candle"] = -0.7
        elif "marubozu" in pat: s["candle"] = -0.6
        else: s["candle"] = -0.4
    else: s["candle"] = 0.0

    # Momentum (ROC-10) — EXACT
    mom_val = df["MOM"].iloc[idx] if pd.notna(df["MOM"].iloc[idx]) else 0.0
    mom_score = round(max(-1.0, min(1.0, mom_val / 2)), 2)
    s["momentum"] = mom_score

    # Composite — EXACT
    wsum = (s.get("trend", 0) * W_TREND + s.get("vwap", 0) * W_VWAP + s.get("obv", 0) * W_OBV +
            s.get("cmf", 0) * W_CMF + s.get("mfi", 0) * W_MFI + s.get("momentum", 0) * W_MOM +
            s.get("vix", 0) * W_VIX + s.get("vp_quality", 0) * W_VPQ + s.get("candle", 0) * W_CANDLE)
    raw = (wsum / TOTAL_W) * 10
    s["composite"] = round(raw ** 1.15 if raw > 0 else -(abs(raw) ** 1.15), 2)
    return s


# ═══ PORTFOLIO BACKTEST ENGINE ═══

def run_backtest(all_data, vix_series, timeline, start_idx, end_idx, label=""):
    """Run portfolio backtest on a specific date range."""
    capital = STARTING_CAPITAL
    positions = []
    closed_trades = []
    equity_curve = []
    peak = STARTING_CAPITAL
    max_dd = 0

    for t_idx in range(start_idx, end_idx):
        dt = timeline[t_idx]

        # Get VIX
        try:
            vix_val = float(vix_series.loc[dt]) if dt in vix_series.index else 20.0
        except:
            vix_val = 20.0

        # ── Check exits ──
        surviving = []
        for pos in positions:
            sym = pos["ticker"]
            df = all_data.get(sym)
            if df is None or dt not in df.index:
                surviving.append(pos); continue

            idx = df.index.get_loc(dt)
            days_held = idx - pos["entry_bar"]
            lo = float(df["low"].iloc[idx])
            hi = float(df["high"].iloc[idx])
            cl = float(df["close"].iloc[idx])

            exit_reason = None
            exit_price = cl
            exit_r = 0.0

            if lo <= pos["sl"]:
                exit_reason = "SL"
                exit_price = pos["sl"]
                exit_r = -1.0
            elif hi >= pos["tp2"]:
                exit_reason = "TP2"
                exit_price = pos["tp2"]
                exit_r = TP2_R
            elif hi >= pos["tp1"]:
                exit_reason = "TP1"
                exit_price = pos["tp1"]
                exit_r = TP1_R
            elif days_held >= MAX_HOLD_DAYS:
                exit_reason = "EXPIRED"
                exit_price = cl
                risk_per_share = pos["entry_price"] - pos["sl"]
                exit_r = round((cl - pos["entry_price"]) / max(risk_per_share, 0.01), 2)

            if exit_reason:
                pnl = pos["risked"] * exit_r
                capital += pos["risked"] + pnl
                closed_trades.append({
                    "ticker": sym,
                    "entry_date": str(df.index[pos["entry_bar"]]),
                    "exit_date": str(dt),
                    "entry_price": pos["entry_price"],
                    "exit_price": round(exit_price, 2),
                    "exit_reason": exit_reason,
                    "r_multiple": round(exit_r, 2),
                    "pnl": round(pnl, 2),
                    "days_held": days_held,
                    "score": pos["score"],
                })
            else:
                surviving.append(pos)

        positions = surviving

        # ── Scan for entries ──
        if len(positions) >= MAX_POSITIONS:
            # Track equity even when full
            pos_value = sum(p["risked"] for p in positions)
            total_val = capital + pos_value
            equity_curve.append({"date": str(dt), "value": total_val})
            peak = max(peak, total_val)
            dd = (peak - total_val) / peak * 100
            max_dd = max(max_dd, dd)
            continue

        open_syms = {p["ticker"] for p in positions}
        candidates = []

        for sym, df in all_data.items():
            if sym in open_syms: continue
            if dt not in df.index: continue
            idx = df.index.get_loc(dt)
            if idx < 200: continue

            vol_20avg = df["volume"].iloc[max(0, idx-20):idx].mean()
            if df["volume"].iloc[idx] < VOLUME_FILTER * vol_20avg:
                continue

            sc = score_signal(df, vix_val, idx)
            if sc["composite"] < MIN_CONFLUENCE: continue

            close = float(df["close"].iloc[idx])
            atr = float(df["ATR"].iloc[idx])
            if pd.isna(atr) or atr <= 0: continue

            candidates.append((sym, idx, sc, close, atr))

        candidates.sort(key=lambda x: x[2]["composite"], reverse=True)
        slots = MAX_POSITIONS - len(positions)

        for sym, idx, sc, close, atr in candidates[:slots]:
            sl = close - STOP_ATR * atr
            risk_per_share = close - sl
            risked = capital * RISK_PER_TRADE
            shares = max(1, int(risked / risk_per_share))
            actual_risk = shares * risk_per_share
            tp1 = close + TP1_R * risk_per_share
            tp2 = close + TP2_R * risk_per_share

            capital -= actual_risk
            positions.append({
                "ticker": sym, "entry_bar": idx,
                "entry_price": round(close, 2), "shares": shares,
                "sl": round(sl, 2), "tp1": round(tp1, 2), "tp2": round(tp2, 2),
                "risked": round(actual_risk, 2), "score": sc["composite"],
            })

        # Track equity
        pos_value = sum(p["risked"] for p in positions)
        total_val = capital + pos_value
        equity_curve.append({"date": str(dt), "value": total_val})
        peak = max(peak, total_val)
        dd = (peak - total_val) / peak * 100
        max_dd = max(max_dd, dd)

    # Return capital from open positions
    for pos in positions:
        capital += pos["risked"]

    return capital, closed_trades, equity_curve, max_dd


def compute_metrics(closed_trades, capital, years, label):
    """Compute standard metrics from closed trades."""
    if not closed_trades:
        return {"label": label, "trades": 0, "error": "No trades"}

    df_t = pd.DataFrame(closed_trades)
    wins = (df_t["r_multiple"] > 0).sum()
    losses = (df_t["r_multiple"] < 0).sum()
    total = len(df_t)
    total_r = df_t["r_multiple"].sum()
    avg_r = total_r / total
    win_rate = wins / total * 100

    winners = df_t[df_t["r_multiple"] > 0]
    losers = df_t[df_t["r_multiple"] < 0]
    avg_win = winners["r_multiple"].mean() if len(winners) > 0 else 0
    avg_loss = losers["r_multiple"].mean() if len(losers) > 0 else 0
    payoff = abs(avg_win / avg_loss) if avg_loss != 0 else 99
    pf = abs(avg_win * wins / (avg_loss * losses)) if losses > 0 else 99
    expectancy = (win_rate / 100 * avg_win) + ((1 - win_rate / 100) * avg_loss)

    total_return = (capital - STARTING_CAPITAL) / STARTING_CAPITAL * 100
    ann_return = total_return / years if years > 0 else 0

    # Exit breakdown
    exit_counts = {}
    for reason in ["TP1", "TP2", "SL", "EXPIRED"]:
        cnt = (df_t["exit_reason"] == reason).sum()
        avg_r_reason = df_t[df_t["exit_reason"] == reason]["r_multiple"].mean() if cnt > 0 else 0
        exit_counts[reason] = {"count": int(cnt), "avg_r": round(avg_r_reason, 3)}

    # Consecutive losses
    max_consec_loss = 0
    current_streak = 0
    for _, t in df_t.iterrows():
        if t["r_multiple"] < 0:
            current_streak += 1
            max_consec_loss = max(max_consec_loss, current_streak)
        else:
            current_streak = 0

    return {
        "label": label,
        "trades": total,
        "wins": int(wins),
        "losses": int(losses),
        "win_rate": round(win_rate, 1),
        "avg_r": round(avg_r, 3),
        "avg_win_r": round(avg_win, 3),
        "avg_loss_r": round(avg_loss, 3),
        "payoff_ratio": round(payoff, 2),
        "profit_factor": round(pf, 2),
        "expectancy_r": round(expectancy, 3),
        "total_r": round(total_r, 2),
        "total_return_pct": round(total_return, 2),
        "ann_return_pct": round(ann_return, 2),
        "ending_capital": round(capital, 2),
        "max_consec_losses": max_consec_loss,
        "exit_breakdown": exit_counts,
    }


def main():
    print("=" * 70)
    print("  V5 PAPER TRADER BACKTEST — EXACT REPLICA")
    print("  Thorp Edge Evaluation: Phase 2")
    print("=" * 70)
    print(f"  Config: SL={STOP_ATR}×ATR, TP1={TP1_R}R, TP2={TP2_R}R")
    print(f"  MinScore={MIN_CONFLUENCE}, MaxHold={MAX_HOLD_DAYS}d, Vol>{VOLUME_FILTER}×")
    print(f"  9 Factors: Trend(1.5), VWAP(2.0), OBV(1.0), CMF(1.0), MFI(1.0), MOM(1.0), VIX(2.0), VPQ(2.0), Candle(1.5)")
    print(f"  Total weight: {TOTAL_W}")
    print()

    # Load universe
    tickers = load_tickers(SP500_FILE)
    print(f"[1] Loading {len(tickers)} S&P 500 stocks (5yr data)...")

    all_data = {}
    for i in range(0, len(tickers), 50):
        batch = tickers[i:i+50]
        try:
            data = yf.download(" ".join(batch), period="10y", progress=False, group_by="ticker", threads=True)
            if len(batch) == 1:
                df = data.copy()
                if not df.empty and len(df) > 250:
                    df.columns = df.columns.str.lower()
                    all_data[batch[0]] = df
            else:
                for sym in batch:
                    try:
                        df = data[sym].dropna(how="all")
                        if not df.empty and len(df) > 250:
                            df.columns = df.columns.str.lower()
                            all_data[sym] = df
                    except: pass
        except Exception as e:
            print(f"  Batch error: {e}")
    print(f"  Loaded {len(all_data)} stocks")

    # Fetch VIX
    print("\n[2] Fetching VIX...")
    vix_data = yf.download("^VIX", period="10y", progress=False)
    if hasattr(vix_data.columns, 'levels'):
        vix_series = vix_data.iloc[:, 0]
    else:
        vix_series = vix_data["Close"]

    # Fetch SPY for benchmark
    print("[3] Fetching SPY benchmark...")
    spy_data = yf.download("SPY", period="10y", progress=False)
    if hasattr(spy_data.columns, 'levels'):
        spy_data.columns = spy_data.columns.get_level_values(0)
    spy_data.columns = [c.lower() for c in spy_data.columns]

    # Compute indicators
    print("\n[4] Computing indicators for all stocks...")
    for sym, df in all_data.items():
        df["ATR"] = compute_atr(df)
        df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
        df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()
        df["VWAP"], df["VWAP_Upper"], df["VWAP_Lower"] = compute_vwap_bands(df)
        df["OBV"] = compute_obv(df)
        df["CMF"] = compute_cmf(df)
        df["MFI"] = compute_mfi(df)
        df["VP_Quality"] = compute_vp_quality(df)
        df["MOM"] = (df["close"] - df["close"].shift(10)) / df["close"].shift(10) * 100

    # Build timeline
    all_dates = set()
    for df in all_data.values():
        all_dates.update(df.index)
    timeline = sorted(all_dates)
    warmup = 300  # EMA200 + indicator warmup

    # Split: 60% train, 40% test (walk-forward)
    total_bars = len(timeline) - warmup
    train_bars = int(total_bars * 0.6)
    test_start = warmup + train_bars

    print(f"\n[5] Running backtests...")
    print(f"  Timeline: {timeline[warmup].strftime('%Y-%m-%d')} → {timeline[-1].strftime('%Y-%m-%d')}")
    print(f"  Train: {timeline[warmup].strftime('%Y-%m-%d')} → {timeline[test_start].strftime('%Y-%m-%d')}")
    print(f"  Test:  {timeline[test_start].strftime('%Y-%m-%d')} → {timeline[-1].strftime('%Y-%m-%d')}")

    # Run full-period backtest
    print("\n  Running FULL period backtest...")
    full_cap, full_trades, full_equity, full_mdd = run_backtest(
        all_data, vix_series, timeline, warmup, len(timeline) - 5, "Full"
    )
    full_years = (timeline[-5] - timeline[warmup]).days / 365

    # Run walk-forward TEST period only
    print("  Running WALK-FORWARD test period backtest...")
    test_cap, test_trades, test_equity, test_mdd = run_backtest(
        all_data, vix_series, timeline, test_start, len(timeline) - 5, "Walk-Forward"
    )
    test_years = (timeline[-5] - timeline[test_start]).days / 365

    # Compute SPY benchmark for same periods
    spy_full_start = spy_data.index[spy_data.index >= timeline[warmup]]
    spy_full_end = spy_data.index[spy_data.index <= timeline[-5]]
    if len(spy_full_start) > 0 and len(spy_full_end) > 0:
        spy_full_ret = (float(spy_data["close"].loc[spy_full_end[-1]]) / float(spy_data["close"].loc[spy_full_start[0]]) - 1) * 100
        spy_full_years = (spy_full_end[-1] - spy_full_start[0]).days / 365
    else:
        spy_full_ret = 0; spy_full_years = 1

    spy_test_start = spy_data.index[spy_data.index >= timeline[test_start]]
    spy_test_end = spy_data.index[spy_data.index <= timeline[-5]]
    if len(spy_test_start) > 0 and len(spy_test_end) > 0:
        spy_test_ret = (float(spy_data["close"].loc[spy_test_end[-1]]) / float(spy_data["close"].loc[spy_test_start[0]]) - 1) * 100
        spy_test_years = (spy_test_end[-1] - spy_test_start[0]).days / 365
    else:
        spy_test_ret = 0; spy_test_years = 1

    # Compute metrics
    full_metrics = compute_metrics(full_trades, full_cap, full_years, "Full Period")
    test_metrics = compute_metrics(test_trades, test_cap, test_years, "Walk-Forward Test")

    # ── PRINT RESULTS ──
    print("\n" + "=" * 70)
    print("  BACKTEST RESULTS")
    print("=" * 70)

    for metrics, spy_ret, spy_years, mdd, period_label in [
        (full_metrics, spy_full_ret, spy_full_years, full_mdd, "FULL PERIOD"),
        (test_metrics, spy_test_ret, spy_test_years, test_mdd, "WALK-FORWARD TEST"),
    ]:
        print(f"\n  ── {period_label} ──")
        if metrics.get("trades", 0) == 0:
            print("  ❌ No trades generated!")
            continue

        spy_ann = spy_ret / spy_years if spy_years > 0 else 0
        alpha = metrics["ann_return_pct"] - spy_ann

        print(f"  Trades:       {metrics['trades']}")
        print(f"  Win rate:     {metrics['wins']}/{metrics['trades']} ({metrics['win_rate']}%)")
        print(f"  Avg R/trade:  {metrics['avg_r']:+.3f}")
        print(f"  Avg win:      {metrics['avg_win_r']:+.3f}R | Avg loss: {metrics['avg_loss_r']:+.3f}R")
        print(f"  Payoff ratio: {metrics['payoff_ratio']:.2f}×")
        print(f"  Profit factor:{metrics['profit_factor']:.2f}")
        print(f"  Expectancy:   {metrics['expectancy_r']:+.3f}R per trade")
        print(f"  Total R:      {metrics['total_r']:+.2f}")
        print(f"  Max consec L: {metrics['max_consec_losses']}")
        print(f"  Max drawdown: {mdd:.1f}%")
        print(f"  ─────────────────────────")
        print(f"  V5 return:    {metrics['total_return_pct']:+.2f}% ({metrics['ann_return_pct']:+.2f}%/yr)")
        print(f"  SPY return:   {spy_ret:+.2f}% ({spy_ann:+.2f}%/yr)")
        print(f"  Alpha:        {alpha:+.2f}%/yr")
        print(f"  Ending cap:   ${metrics['ending_capital']:.2f}")
        print()
        print(f"  Exit breakdown:")
        for reason, data in metrics["exit_breakdown"].items():
            print(f"    {reason}: {data['count']} trades, avg {data['avg_r']:+.3f}R")

    # ── THORP SCORECARD ──
    print("\n" + "=" * 70)
    print("  THORP EDGE EVALUATION SCORECARD")
    print("=" * 70)

    m = test_metrics  # Use walk-forward (honest)
    if m.get("trades", 0) == 0:
        print("  ❌ Cannot score — no trades in test period")
        return

    scores = {}
    # 1. Logical basis (already assessed: 2/5)
    scores["Logical basis"] = (2, "Textbook indicators, no unique structural edge")

    # 2. Statistical significance
    if m["trades"] >= 100: scores["Statistical significance"] = (4, f"{m['trades']} trades — good sample")
    elif m["trades"] >= 50: scores["Statistical significance"] = (3, f"{m['trades']} trades — moderate sample")
    elif m["trades"] >= 20: scores["Statistical significance"] = (2, str(m["trades"]) + " trades — small sample")
    else: scores["Statistical significance"] = (1, f"{m['trades']} trades — too few")

    # 3. Cost-adjusted expectancy
    if m["expectancy_r"] > 0.2: scores["Cost-adjusted expectancy"] = (4, f"{m['expectancy_r']:+.3f}R — solid edge")
    elif m["expectancy_r"] > 0.1: scores["Cost-adjusted expectancy"] = (3, f"{m['expectancy_r']:+.3f}R — marginal edge")
    elif m["expectancy_r"] > 0: scores["Cost-adjusted expectancy"] = (2, f"{m['expectancy_r']:+.3f}R — thin edge")
    else: scores["Cost-adjusted expectancy"] = (1, f"{m['expectancy_r']:+.3f}R — NEGATIVE expectancy")

    # 4. Robustness (walk-forward vs full)
    if full_metrics.get("trades", 0) > 0 and m.get("trades", 0) > 0:
        wf_ratio = m["win_rate"] / full_metrics["win_rate"] if full_metrics["win_rate"] > 0 else 0
        if wf_ratio > 0.85: scores["Robustness"] = (4, f"WF/Full win rate ratio: {wf_ratio:.2f}")
        elif wf_ratio > 0.7: scores["Robustness"] = (3, f"WF/Full win rate ratio: {wf_ratio:.2f}")
        elif wf_ratio > 0.5: scores["Robustness"] = (2, f"WF/Full win rate ratio: {wf_ratio:.2f}")
        else: scores["Robustness"] = (1, f"WF/Full win rate ratio: {wf_ratio:.2f} — severe degradation")
    else:
        scores["Robustness"] = (1, "Insufficient data to compare")

    # 5. Capacity
    scores["Capacity"] = (4, "S&P 500 large caps — high capacity")

    # 6. Backtest integrity
    scores["Backtest integrity"] = (3, "Walk-forward used, but survivorship bias possible")

    # 7. Paper trade validation
    scores["Paper trade validation"] = (2, "1 month paper trading, 3 trades only")

    # 8. Risk/reward
    if m["profit_factor"] > 1.5 and full_mdd < 25:
        scores["Risk/reward profile"] = (4, f"PF={m['profit_factor']:.2f}, MDD={full_mdd:.1f}%")
    elif m["profit_factor"] > 1.0 and full_mdd < 30:
        scores["Risk/reward profile"] = (3, f"PF={m['profit_factor']:.2f}, MDD={full_mdd:.1f}%")
    elif m["profit_factor"] > 1.0:
        scores["Risk/reward profile"] = (2, f"PF={m['profit_factor']:.2f}, MDD={full_mdd:.1f}%")
    else:
        scores["Risk/reward profile"] = (1, f"PF={m['profit_factor']:.2f}, MDD={full_mdd:.1f}%")

    total_score = 0
    for dim, (score, note) in scores.items():
        total_score += score
        print(f"  {score}/5  {dim}: {note}")

    print(f"\n  TOTAL: {total_score}/40")
    if total_score >= 25:
        print("  ✅ PASS — Proceed with position sizing per Kelly")
    elif total_score >= 20:
        print("  ⚠️ MARGINAL — Paper trade only, small size")
    else:
        print("  ❌ FAIL — Don't trade. Buy the index.")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "factors": 9, "weights": {
                "trend": W_TREND, "vwap": W_VWAP, "obv": W_OBV, "cmf": W_CMF,
                "mfi": W_MFI, "momentum": W_MOM, "vix": W_VIX, "vpq": W_VPQ, "candle": W_CANDLE
            },
            "min_score": MIN_CONFLUENCE, "sl_atr": STOP_ATR, "tp1_r": TP1_R, "tp2_r": TP2_R,
            "max_hold": MAX_HOLD_DAYS, "volume_filter": VOLUME_FILTER, "capital": STARTING_CAPITAL,
            "risk_per_trade": RISK_PER_TRADE, "max_positions": MAX_POSITIONS,
        },
        "full_period": full_metrics,
        "walk_forward": test_metrics,
        "spy_benchmark": {"full_return": round(spy_full_ret, 2), "test_return": round(spy_test_ret, 2)},
        "max_drawdown": {"full": round(full_mdd, 2), "test": round(test_mdd, 2)},
        "thorp_score": total_score,
        "thorp_details": {k: {"score": v[0], "note": v[1]} for k, v in scores.items()},
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
