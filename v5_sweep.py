#!/usr/bin/env python3
"""
V5 Backtest Parameter Sweep — Options 3 & 4
=============================================
Test MAX_POSITIONS (2,3,5) and TP2_R (1.5, 2.5) independently + combined.
Uses pre-computed indicators from v5_backtest_exact.py cache if available,
otherwise recomputes. Runs walk-forward only (honest test).
"""

import warnings
warnings.filterwarnings("ignore")
import json, time
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime
import yfinance as yf

# ═══ BASE CONFIG ═══
STARTING_CAPITAL = 1000.0
RISK_PER_TRADE = 0.01
MIN_CONFLUENCE = 4.0
STOP_ATR = 2.0
TP1_R = 1.2
MAX_HOLD_DAYS = 30
VOLUME_FILTER = 1.2

# V5 weights (EXACT)
W_TREND = 1.5; W_VWAP = 2.0; W_OBV = 1.0; W_CMF = 1.0
W_MFI = 1.0; W_MOM = 1.0; W_VIX = 2.0; W_VPQ = 2.0; W_CANDLE = 1.5
TOTAL_W = W_TREND + W_VWAP + W_OBV + W_CMF + W_MFI + W_MOM + W_VIX + W_VPQ + W_CANDLE

SP500_FILE = "/root/.hermes/profiles/trader/scripts/sp500_universe.txt"

# ═══ INDICATORS (identical to v5_backtest_exact.py) ═══

def load_tickers(path, limit=None):
    tks = []
    with open(path) as f:
        for l in f:
            l = l.strip()
            if l and not l.startswith("#"): tks.append(l.upper())
    return tks[:limit] if limit else tks

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
    obv = [0.0]; c = df["close"].values; v = df["volume"].values
    for i in range(1, len(df)):
        if c[i] > c[i-1]: obv.append(obv[-1] + v[i])
        elif c[i] < c[i-1]: obv.append(obv[-1] - v[i])
        else: obv.append(obv[-1])
    return pd.Series(obv, index=df.index)

def compute_cmf(df, p=20):
    mfm = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"]).replace(0, np.nan)
    return (mfm * df["volume"]).rolling(p).sum() / df["volume"].rolling(p).sum()

def compute_mfi(df, p=14):
    tp = (df["high"] + df["low"] + df["close"]) / 3; mf = tp * df["volume"]
    ta = tp.values; ma = mf.values; pf = np.zeros(len(df)); nf = np.zeros(len(df))
    for i in range(1, len(df)):
        if ta[i] > ta[i-1]: pf[i] = ma[i]
        elif ta[i] < ta[i-1]: nf[i] = ma[i]
    ps = pd.Series(pf).rolling(p).sum(); ns = pd.Series(nf).rolling(p).sum()
    return 100 - (100 / (1 + ps / ns.replace(0, np.nan)))

def compute_vp_quality(df, lb=50, bins=50):
    q = pd.Series(np.nan, index=df.index)
    lo = df["low"].values; hi = df["high"].values; cl = df["close"].values; op = df["open"].values; vo = df["volume"].values
    for i in range(lb, len(df)):
        pmin = lo[i-lb:i].min(); pmax = hi[i-lb:i].max()
        if pmax == pmin: q.iloc[i] = 0.0; continue
        bs = (pmax - pmin) / bins; vb = defaultdict(float)
        for j in range(i-lb, i):
            ch = max(op[j], hi[j], lo[j], cl[j]); cl2 = min(op[j], hi[j], lo[j], cl[j])
            if ch == cl2:
                bi = max(0, min(int((cl[j] - pmin) / bs), bins - 1)); vb[bi] += vo[j]
            else:
                lo2 = max(0, min(int((cl2 - pmin) / bs), bins - 1)); hi2 = max(0, min(int((ch - pmin) / bs), bins - 1))
                n = hi2 - lo2 + 1
                for b in range(lo2, hi2 + 1): vb[b] += vo[j] / n
        if vb:
            tv = sum(vb.values()); q.iloc[i] = max(vb.values()) / tv if tv > 0 else 0.0
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

def score_signal(df, vix_val, idx):
    c = df["close"].iloc[idx]; s = {}
    e50 = df["EMA50"].iloc[idx]; e200 = df["EMA200"].iloc[idx]
    if pd.notna(e50) and pd.notna(e200) and idx >= 5:
        e50_prev = df["EMA50"].iloc[max(0, idx-5)]
        slope = (e50 - e50_prev) / max(e50_prev, 0.01) * 100; rising = slope > 0.3
        if c > e50 > e200 and rising: s["trend"] = 1.0
        elif c > e50 > e200: s["trend"] = 0.6
        elif c > e50 and e50 <= e200: s["trend"] = 0.5 if rising else 0.4
        elif c < e50 > e200: s["trend"] = 0.2
        elif c < e50 < e200: s["trend"] = -1.0 if slope < -0.5 else -0.8
        elif c < e50 and e50 >= e200: s["trend"] = -0.4
        else: s["trend"] = 0.0
    else: s["trend"] = 0.0
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
    if idx >= 20:
        on = df["OBV"].iloc[idx]; os_val = df["OBV"].iloc[idx-19:idx+1].mean()
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
    cv = df["CMF"].iloc[idx]
    s["cmf"] = max(-1.0, min(1.0, cv * 1.8)) if pd.notna(cv) else 0.0
    mv = df["MFI"].iloc[idx]
    if pd.notna(mv):
        if mv > 75: s["mfi"] = -0.5
        elif mv < 25: s["mfi"] = 0.5
        elif mv > 55: s["mfi"] = 0.3
        elif mv < 45: s["mfi"] = -0.3
        else: s["mfi"] = 0.0
    else: s["mfi"] = 0.0
    if vix_val >= 35: s["vix"] = 0.8
    elif vix_val >= 25: s["vix"] = 0.5
    elif vix_val >= 20: s["vix"] = 0.3
    elif vix_val < 12: s["vix"] = -0.5
    elif vix_val < 15: s["vix"] = -0.2
    else: s["vix"] = 0.0
    vq = df["VP_Quality"].iloc[idx]
    if pd.notna(vq):
        if vq > 0.12: s["vp_quality"] = min(1.0, vq * 5)
        elif vq > 0.08: s["vp_quality"] = 0.4
        else: s["vp_quality"] = 0.0
    else: s["vp_quality"] = 0.0
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
    mom_val = df["MOM"].iloc[idx] if pd.notna(df["MOM"].iloc[idx]) else 0.0
    mom_score = round(max(-1.0, min(1.0, mom_val / 2)), 2)
    s["momentum"] = mom_score
    wsum = (s.get("trend", 0) * W_TREND + s.get("vwap", 0) * W_VWAP + s.get("obv", 0) * W_OBV +
            s.get("cmf", 0) * W_CMF + s.get("mfi", 0) * W_MFI + s.get("momentum", 0) * W_MOM +
            s.get("vix", 0) * W_VIX + s.get("vp_quality", 0) * W_VPQ + s.get("candle", 0) * W_CANDLE)
    raw = (wsum / TOTAL_W) * 10
    s["composite"] = round(raw ** 1.15 if raw > 0 else -(abs(raw) ** 1.15), 2)
    return s


# ═══ BACKTEST ENGINE (parameterized) ═══

def run_backtest(all_data, vix_series, timeline, start_idx, end_idx, max_pos, tp2_r):
    capital = STARTING_CAPITAL
    positions = []
    closed_trades = []
    peak = STARTING_CAPITAL
    max_dd = 0

    for t_idx in range(start_idx, end_idx):
        dt = timeline[t_idx]
        try:
            vix_val = float(vix_series.loc[dt]) if dt in vix_series.index else 20.0
        except:
            vix_val = 20.0

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

            exit_reason = None; exit_price = cl; exit_r = 0.0
            if lo <= pos["sl"]:
                exit_reason = "SL"; exit_price = pos["sl"]; exit_r = -1.0
            elif hi >= pos["tp2"]:
                exit_reason = "TP2"; exit_price = pos["tp2"]; exit_r = tp2_r
            elif hi >= pos["tp1"]:
                exit_reason = "TP1"; exit_price = pos["tp1"]; exit_r = TP1_R
            elif days_held >= MAX_HOLD_DAYS:
                exit_reason = "EXPIRED"; exit_price = cl
                risk_per_share = pos["entry_price"] - pos["sl"]
                exit_r = round((cl - pos["entry_price"]) / max(risk_per_share, 0.01), 2)

            if exit_reason:
                pnl = pos["risked"] * exit_r
                capital += pos["risked"] + pnl
                closed_trades.append({
                    "ticker": sym, "exit_reason": exit_reason,
                    "r_multiple": round(exit_r, 2), "pnl": round(pnl, 2),
                    "days_held": days_held,
                })
            else:
                surviving.append(pos)
        positions = surviving

        if len(positions) >= max_pos:
            total_val = capital + sum(p["risked"] for p in positions)
            peak = max(peak, total_val); max_dd = max(max_dd, (peak - total_val) / peak * 100)
            continue

        open_syms = {p["ticker"] for p in positions}
        candidates = []
        for sym, df in all_data.items():
            if sym in open_syms: continue
            if dt not in df.index: continue
            idx = df.index.get_loc(dt)
            if idx < 200: continue
            vol_20avg = df["volume"].iloc[max(0, idx-20):idx].mean()
            if df["volume"].iloc[idx] < VOLUME_FILTER * vol_20avg: continue
            sc = score_signal(df, vix_val, idx)
            if sc["composite"] < MIN_CONFLUENCE: continue
            close = float(df["close"].iloc[idx])
            atr = float(df["ATR"].iloc[idx])
            if pd.isna(atr) or atr <= 0: continue
            candidates.append((sym, idx, sc, close, atr))

        candidates.sort(key=lambda x: x[2]["composite"], reverse=True)
        slots = max_pos - len(positions)
        for sym, idx, sc, close, atr in candidates[:slots]:
            sl = close - STOP_ATR * atr
            risk_per_share = close - sl
            risked = capital * RISK_PER_TRADE
            shares = max(1, int(risked / risk_per_share))
            actual_risk = shares * risk_per_share
            tp1 = close + TP1_R * risk_per_share
            tp2 = close + tp2_r * risk_per_share
            capital -= actual_risk
            positions.append({
                "ticker": sym, "entry_bar": idx,
                "entry_price": round(close, 2), "shares": shares,
                "sl": round(sl, 2), "tp1": round(tp1, 2), "tp2": round(tp2, 2),
                "risked": round(actual_risk, 2), "score": sc["composite"],
            })

        total_val = capital + sum(p["risked"] for p in positions)
        peak = max(peak, total_val); max_dd = max(max_dd, (peak - total_val) / peak * 100)

    for pos in positions:
        capital += pos["risked"]

    return capital, closed_trades, max_dd


def analyze(closed_trades, capital, years, max_dd):
    if not closed_trades:
        return {"trades": 0}
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
    max_consec = 0; streak = 0
    for _, t in df_t.iterrows():
        if t["r_multiple"] < 0: streak += 1; max_consec = max(max_consec, streak)
        else: streak = 0
    exits = {}
    for r in ["TP1", "TP2", "SL", "EXPIRED"]:
        cnt = (df_t["exit_reason"] == r).sum()
        avg = df_t[df_t["exit_reason"] == r]["r_multiple"].mean() if cnt > 0 else 0
        exits[r] = {"count": int(cnt), "avg_r": round(avg, 3)}
    return {
        "trades": total, "wins": int(wins), "win_rate": round(win_rate, 1),
        "avg_r": round(avg_r, 3), "avg_win": round(avg_win, 3), "avg_loss": round(avg_loss, 3),
        "payoff": round(payoff, 2), "pf": round(pf, 2), "expectancy": round(expectancy, 3),
        "total_r": round(total_r, 2), "total_return": round(total_return, 2),
        "ann_return": round(ann_return, 2), "ending_cap": round(capital, 2),
        "max_dd": round(max_dd, 1), "max_consec_loss": max_consec, "exits": exits,
    }


def main():
    print("=" * 70)
    print("  V5 PARAMETER SWEEP — Options 3 & 4")
    print("  Walk-forward: Jan 2025 → Jul 2026 (189 days test)")
    print("=" * 70)

    # Load data (same as backtest_exact)
    tickers = load_tickers(SP500_FILE)
    print(f"\n[1] Loading {len(tickers)} stocks...")
    all_data = {}
    for i in range(0, len(tickers), 50):
        batch = tickers[i:i+50]
        try:
            data = yf.download(" ".join(batch), period="5y", progress=False, group_by="ticker", threads=True)
            if len(batch) == 1:
                df = data.copy()
                if not df.empty and len(df) > 250:
                    df.columns = df.columns.str.lower(); all_data[batch[0]] = df
            else:
                for sym in batch:
                    try:
                        df = data[sym].dropna(how="all")
                        if not df.empty and len(df) > 250:
                            df.columns = df.columns.str.lower(); all_data[sym] = df
                    except: pass
        except: pass
    print(f"  Loaded {len(all_data)} stocks")

    print("[2] Fetching VIX & SPY...")
    vix_data = yf.download("^VIX", period="5y", progress=False)
    vix_series = vix_data.iloc[:, 0] if hasattr(vix_data.columns, 'levels') else vix_data["Close"]
    spy_data = yf.download("SPY", period="5y", progress=False)
    if hasattr(spy_data.columns, 'levels'):
        spy_data.columns = spy_data.columns.get_level_values(0)
    spy_data.columns = [c.lower() for c in spy_data.columns]

    print("[3] Computing indicators...")
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
    for df in all_data.values(): all_dates.update(df.index)
    timeline = sorted(all_dates)
    warmup = 300
    total_bars = len(timeline) - warmup
    train_bars = int(total_bars * 0.6)
    test_start = warmup + train_bars
    end_idx = len(timeline) - 5
    test_years = (timeline[end_idx-1] - timeline[test_start]).days / 365

    # SPY benchmark for test period
    spy_test_s = spy_data.index[spy_data.index >= timeline[test_start]]
    spy_test_e = spy_data.index[spy_data.index <= timeline[end_idx-1]]
    spy_test_ret = (float(spy_data["close"].loc[spy_test_e[-1]]) / float(spy_data["close"].loc[spy_test_s[0]]) - 1) * 100 if len(spy_test_s) > 0 and len(spy_test_e) > 0 else 0
    spy_ann = spy_test_ret / test_years if test_years > 0 else 0

    # ── Configs to test ──
    configs = [
        {"name": "BASELINE (5 pos, TP2=2.5R)", "max_pos": 5, "tp2_r": 2.5},
        {"name": "Option 3a: 3 positions",      "max_pos": 3, "tp2_r": 2.5},
        {"name": "Option 3b: 2 positions",      "max_pos": 2, "tp2_r": 2.5},
        {"name": "Option 4: TP2=1.5R",          "max_pos": 5, "tp2_r": 1.5},
        {"name": "Combined: 3 pos + TP2=1.5R",  "max_pos": 3, "tp2_r": 1.5},
        {"name": "Combined: 2 pos + TP2=1.5R",  "max_pos": 2, "tp2_r": 1.5},
    ]

    print(f"\n[4] Running {len(configs)} configurations (walk-forward)...\n")
    results = []
    for cfg in configs:
        t0 = time.time()
        cap, trades, mdd = run_backtest(all_data, vix_series, timeline, test_start, end_idx, cfg["max_pos"], cfg["tp2_r"])
        elapsed = time.time() - t0
        m = analyze(trades, cap, test_years, mdd)
        m["name"] = cfg["name"]
        m["max_pos"] = cfg["max_pos"]
        m["tp2_r"] = cfg["tp2_r"]
        m["alpha"] = round(m["ann_return"] - spy_ann, 2) if m["trades"] > 0 else 0
        results.append(m)
        print(f"  {cfg['name']}: {m['trades']} trades, {m['win_rate']}% WR, {m['total_return']:+.1f}%, MDD={m['max_dd']:.1f}% ({elapsed:.0f}s)")

    # ── COMPARISON TABLE ──
    print("\n" + "=" * 90)
    print("  COMPARISON TABLE — Walk-Forward (Jan 2025 → Jul 2026)")
    print("=" * 90)
    print(f"  SPY Benchmark: {spy_test_ret:+.1f}% ({spy_ann:+.1f}%/yr)\n")

    hdr = f"  {'Config':<30} {'Trades':>6} {'WR%':>6} {'AvgR':>7} {'PF':>6} {'Exp':>7} {'MDD%':>7} {'Return':>9} {'Ann%':>8} {'Alpha':>8}"
    print(hdr)
    print("  " + "-" * 88)

    for m in results:
        if m["trades"] == 0:
            print(f"  {m['name']:<30} {'NO TRADES':>6}")
            continue
        print(f"  {m['name']:<30} {m['trades']:>6} {m['win_rate']:>5.1f}% {m['avg_r']:>+6.3f} {m['pf']:>5.2f} {m['expectancy']:>+6.3f} {m['max_dd']:>6.1f}% {m['total_return']:>+8.2f}% {m['ann_return']:>+7.2f}% {m['alpha']:>+7.2f}%")

    # ── EXIT BREAKDOWN ──
    print(f"\n  {'Config':<30} {'TP1':>8} {'TP2':>8} {'SL':>8} {'EXPIRED':>8}")
    print("  " + "-" * 62)
    for m in results:
        if m["trades"] == 0: continue
        e = m["exits"]
        tp1_pct = e["TP1"]["count"] / m["trades"] * 100
        tp2_pct = e["TP2"]["count"] / m["trades"] * 100
        sl_pct = e["SL"]["count"] / m["trades"] * 100
        exp_pct = e["EXPIRED"]["count"] / m["trades"] * 100
        print(f"  {m['name']:<30} {e['TP1']['count']:>4}({tp1_pct:>4.0f}%) {e['TP2']['count']:>4}({tp2_pct:>4.0f}%) {e['SL']['count']:>4}({sl_pct:>4.0f}%) {e['EXPIRED']['count']:>4}({exp_pct:>4.0f}%)")

    # ── BEST CONFIG ──
    valid = [m for m in results if m["trades"] > 0]
    if valid:
        best_exp = max(valid, key=lambda x: x["expectancy"])
        best_ret = max(valid, key=lambda x: x["total_return"])
        best_alpha = max(valid, key=lambda x: x["alpha"])
        best_dd = min(valid, key=lambda x: x["max_dd"])

        print(f"\n  Best expectancy: {best_exp['name']} ({best_exp['expectancy']:+.3f}R)")
        print(f"  Best return:     {best_ret['name']} ({best_ret['total_return']:+.2f}%)")
        print(f"  Best alpha:      {best_alpha['name']} ({best_alpha['alpha']:+.2f}%/yr)")
        print(f"  Lowest MDD:      {best_dd['name']} ({best_dd['max_dd']:.1f}%)")

    # Save
    with open("/root/.hermes/profiles/trader/scripts/v5_sweep_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved: v5_sweep_results.json")


if __name__ == "__main__":
    main()
