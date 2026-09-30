#!/usr/bin/env python3
"""
V5 4h/1h Backtest — Round 4: Recalibrated
===========================================
- 5 factors: Trend, VWAP, OBV, CMF, Candle (equal weights)
- Dropped: VIX (daily only), VP_Quality (unstable on 4h)
- Portfolio-level: 5-position cap, walk-forward, realistic
"""

import json, os, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import yfinance as yf

# ═══ CONFIG ═══
UNIVERSE_SIZE = 50
STARTING_CAPITAL = 1000.0
RISK_PER_TRADE = 0.01
MAX_POSITIONS = 5
MIN_CONFLUENCE = 5.5
STOP_ATR = 3.5
TP_R = 1.3
MAX_HOLD_BARS = 120
VOLUME_FILTER = 1.5

# Equal weights for 5 factors
W_TREND=2.0; W_VWAP=2.0; W_OBV=2.0; W_CMF=2.0; W_CANDLE=2.0
TOTAL_W = W_TREND + W_VWAP + W_OBV + W_CMF + W_CANDLE

SP500_FILE = "/root/.hermes/profiles/trader/scripts/sp500_universe.txt"

# ═══ HELPERS ═══

def load_tickers(path, limit=None):
    tks = []
    with open(path) as f:
        for l in f:
            l = l.strip()
            if l and not l.startswith("#"): tks.append(l.upper())
    return tks[:limit] if limit else tks

# ═══ INDICATORS ═══

def compute_atr(df, period=14):
    high, low, close = df["high"], df["low"], df["close"]
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()

def compute_vwap_bands(df, period=20):
    typical = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (typical * df["volume"]).rolling(period).sum() / df["volume"].rolling(period).sum()
    std = typical.rolling(period).std()
    return vwap, vwap + 2 * std, vwap - 2 * std

def compute_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i-1]:
            obv.append(obv[-1] + df["volume"].iloc[i])
        elif df["close"].iloc[i] < df["close"].iloc[i-1]:
            obv.append(obv[-1] - df["volume"].iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)

def compute_cmf(df, period=20):
    mf_mult = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"]).replace(0, np.nan)
    mf_vol = mf_mult * df["volume"]
    return mf_vol.rolling(period).sum() / df["volume"].rolling(period).sum()

def detect_pattern(df_4h, idx):
    if idx < 3: return "none"
    o, h, l, c = df_4h["open"].iloc[idx], df_4h["high"].iloc[idx], df_4h["low"].iloc[idx], df_4h["close"].iloc[idx]
    body = abs(c - o)
    upper = h - max(o, c)
    lower = min(o, c) - l
    rgb = body / (h - l) if h != l else 0

    if body > 0 and rgb > 0.6:
        if c > o and lower < body * 0.1: return "bullish marubozu"
        if c < o and upper < body * 0.1: return "bearish marubozu"
    if lower > body * 2 and upper < body * 0.3:
        return "bullish hammer" if c > o else "bullish hammer"
    if upper > body * 2 and lower < body * 0.3:
        return "bearish shooting star"

    if idx > 0:
        po, pc = df_4h["open"].iloc[idx-1], df_4h["close"].iloc[idx-1]
        if c > o and po > pc and o <= pc and c >= po: return "bullish engulfing"
        if c < o and pc > po and o >= pc and c <= po: return "bearish engulfing"
    return "none"

# ═══ SCORING (5 factors) ═══

def score_signal(df_4h, idx):
    s = {}
    close = float(df_4h["close"].iloc[idx])

    # Trend: EMA50 vs EMA200 + slope
    ema50 = df_4h["EMA50"].iloc[idx]
    ema200 = df_4h["EMA200"].iloc[idx]
    if pd.notna(ema200) and ema200 > 0:
        ratio = close / ema200
        if ratio > 1.05: s["trend"] = 0.8
        elif ratio > 1.02: s["trend"] = 0.5
        elif ratio > 1.00: s["trend"] = 0.2
        elif ratio > 0.98: s["trend"] = -0.2
        else: s["trend"] = -0.5
        if idx > 5 and ema50 > df_4h["EMA50"].iloc[idx-5]: s["trend"] += 0.2
    else:
        s["trend"] = 0.0

    # VWAP: band-aware continuous
    vwap = df_4h["VWAP"].iloc[idx]
    upper = df_4h["VWAP_Upper"].iloc[idx]
    lower = df_4h["VWAP_Lower"].iloc[idx]
    if pd.notna(vwap) and pd.notna(upper) and pd.notna(lower) and (upper - lower) > 0:
        pos = (close - vwap) / (upper - lower)
        s["vwap"] = min(1.0, max(-1.0, (pos + 0.2) * 3))
    else:
        s["vwap"] = 0.0

    # OBV: divergence
    obv = df_4h["OBV"].iloc[idx]
    if idx > 10:
        obv_sma = df_4h["OBV"].iloc[idx-10:idx+1].mean()
        if obv > obv_sma * 1.02: s["obv"] = 0.6
        elif obv > obv_sma: s["obv"] = 0.3
        elif obv > obv_sma * 0.98: s["obv"] = -0.2
        else: s["obv"] = -0.5
    else: s["obv"] = 0.0

    # CMF
    cmf = df_4h["CMF"].iloc[idx]
    if pd.notna(cmf):
        if cmf > 0.15: s["cmf"] = 0.8
        elif cmf > 0.05: s["cmf"] = 0.4
        elif cmf > -0.05: s["cmf"] = 0.0
        elif cmf > -0.15: s["cmf"] = -0.3
        else: s["cmf"] = -0.6
    else: s["cmf"] = 0.0

    # Candle
    pat = detect_pattern(df_4h, idx)
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

    # Composite (5 factors, equal weights)
    wsum = (s.get("trend",0)*W_TREND + s.get("vwap",0)*W_VWAP + s.get("obv",0)*W_OBV +
            s.get("cmf",0)*W_CMF + s.get("candle",0)*W_CANDLE)
    raw = (wsum / TOTAL_W) * 10
    s["composite"] = round(raw**1.15 if raw > 0 else -(abs(raw)**1.15), 2)
    return s

# ═══ PORTFOLIO-LEVEL BACKTEST ═══

def backtest():
    tickers = load_tickers(SP500_FILE, UNIVERSE_SIZE)
    print(f"Portfolio Backtest: {len(tickers)} stocks, 4h/1h")
    print(f"Config: SL={STOP_ATR}×ATR, TP={TP_R}R, MaxH={MAX_HOLD_BARS}, MinScore={MIN_CONFLUENCE}")
    print(f"Factors: Trend + VWAP + OBV + CMF + Candle (equal weights)\n")

    # Fetch 1h data
    print(f"[1] Fetching 1h data for {len(tickers)} stocks...")
    all_1h = {}
    all_4h = {}
    for i in range(0, len(tickers), 10):
        batch = tickers[i:i+10]
        try:
            data = yf.download(" ".join(batch), period="730d", interval="1h",
                              progress=False, group_by="ticker", threads=True)
            if len(batch) == 1:
                df = data.copy()
                if not df.empty and len(df) > 100:
                    df.columns = df.columns.str.lower()
                    all_1h[batch[0]] = df
            else:
                for sym in batch:
                    try:
                        df = data[sym].dropna(how="all")
                        if not df.empty and len(df) > 100:
                            df.columns = df.columns.str.lower()
                            all_1h[sym] = df
                    except: pass
        except Exception as e:
            print(f"  Batch error: {e}")
    print(f"  Loaded {len(all_1h)} stocks\n")

    # Build 4h data with indicators
    print("[2] Computing 4h indicators...")
    for sym, df_1h in all_1h.items():
        df_4h = df_1h.resample("4h").agg({
            "open": "first", "high": "max", "low": "min",
            "close": "last", "volume": "sum"
        }).dropna()
        if len(df_4h) < 200: continue

        df_4h["ATR"] = compute_atr(df_4h, 14)
        df_4h["EMA50"] = df_4h["close"].ewm(span=50, adjust=False).mean()
        df_4h["EMA200"] = df_4h["close"].ewm(span=200, adjust=False).mean()
        df_4h["VWAP"], df_4h["VWAP_Upper"], df_4h["VWAP_Lower"] = compute_vwap_bands(df_4h, 20)
        df_4h["OBV"] = compute_obv(df_4h)
        df_4h["CMF"] = compute_cmf(df_4h, 20)
        all_4h[sym] = df_4h

    print(f"  Computed for {len(all_4h)} stocks\n")

    # Build unified timeline of all 4h bars across all stocks
    print("[3] Running portfolio backtest...")
    all_bars = set()
    for df_4h in all_4h.values():
        all_bars.update(df_4h.index)
    timeline = sorted(all_bars)
    
    # Only backtest from bar 200 (after warmup) to leave room
    start_idx = 200
    end_idx = len(timeline) - 5
    
    capital = STARTING_CAPITAL
    peak = STARTING_CAPITAL
    positions = []  # [{ticker, entry_idx, entry_price, shares, sl, tp, risked, score, entry_bar}]
    closed_trades = []

    signal_count = 0
    bar_count = 0

    for t_idx in range(start_idx, end_idx):
        ts = timeline[t_idx]
        bar_count += 1

        # ── Check exits for open positions ──
        surviving = []
        for pos in positions:
            sym = pos["ticker"]
            df_4h = all_4h.get(sym)
            df_1h = all_1h.get(sym)
            if df_4h is None or df_1h is None:
                surviving.append(pos); continue

            # Find where this 4h bar sits in the 4h data
            if ts not in df_4h.index:
                surviving.append(pos); continue
            
            idx_4h = df_4h.index.get_loc(ts)
            bars_held = idx_4h - pos["entry_bar"]
            
            # Check exit conditions on 1h bars within this 4h candle
            ts_next = ts + pd.Timedelta(hours=4)
            mask = (df_1h.index > ts) & (df_1h.index <= ts_next)
            df_exit = df_1h[mask]
            
            exit_reason = None
            exit_price = None
            exit_r = 0.0

            # Check bar-level SL/TP (not intra-bar for simplicity)
            bar_lo = float(df_4h["low"].iloc[idx_4h])
            bar_hi = float(df_4h["high"].iloc[idx_4h])
            bar_cl = float(df_4h["close"].iloc[idx_4h])

            if bar_lo <= pos["sl"]:
                exit_reason = "SL"
                exit_price = pos["sl"]
                exit_r = -1.0
            elif bar_hi >= pos["tp"]:
                exit_reason = "TP"
                exit_price = pos["tp"]
                exit_r = TP_R
            elif bars_held >= MAX_HOLD_BARS:
                exit_reason = "EXPIRED"
                exit_price = bar_cl
                risk_per_share = pos["entry_price"] - pos["sl"]
                exit_r = round((bar_cl - pos["entry_price"]) / max(risk_per_share, 0.01), 2)

            if exit_reason:
                pnl = pos["risked"] * exit_r
                capital += pos["risked"] + pnl
                closed_trades.append({
                    "ticker": sym,
                    "entry_date": str(df_4h.index[pos["entry_bar"]]),
                    "exit_date": str(ts),
                    "entry_price": pos["entry_price"],
                    "exit_price": round(exit_price, 2),
                    "exit_reason": exit_reason,
                    "r_multiple": round(exit_r, 2),
                    "pnl": round(pnl, 2),
                    "bars_held": bars_held,
                    "score": pos["score"],
                })
                if exit_r > 0:
                    signal_count += 1  # Only count winners/trades for reporting clarity
            else:
                surviving.append(pos)

        positions = surviving

        # ── Scan for new entries ──
        if len(positions) >= MAX_POSITIONS: continue

        open_syms = {p["ticker"] for p in positions}
        candidates = []

        for sym, df_4h in all_4h.items():
            if sym in open_syms: continue
            if ts not in df_4h.index: continue
            
            idx = df_4h.index.get_loc(ts)
            if idx < 200: continue

            # Volume filter
            vol_20avg = df_4h["volume"].iloc[idx-20:idx].mean()
            if df_4h["volume"].iloc[idx] < VOLUME_FILTER * vol_20avg:
                continue

            sc = score_signal(df_4h, idx)
            if sc["composite"] < MIN_CONFLUENCE: continue

            close = float(df_4h["close"].iloc[idx])
            atr = float(df_4h["ATR"].iloc[idx])
            if pd.isna(atr) or atr <= 0: continue

            candidates.append((sym, idx, sc, close, atr))

        # Sort by score descending, take best
        candidates.sort(key=lambda x: x[2]["composite"], reverse=True)
        slots = MAX_POSITIONS - len(positions)

        for sym, idx, sc, close, atr in candidates[:slots]:
            sl = close - STOP_ATR * atr
            risk_per_share = close - sl
            risked = capital * RISK_PER_TRADE
            shares = max(1, int(risked / risk_per_share))
            actual_risk = shares * risk_per_share
            tp = close + TP_R * risk_per_share

            capital -= actual_risk
            positions.append({
                "ticker": sym,
                "entry_bar": idx,
                "entry_price": round(close, 2),
                "shares": shares,
                "sl": round(sl, 2),
                "tp": round(tp, 2),
                "risked": round(actual_risk, 2),
                "score": sc["composite"],
            })
            signal_count += 1

    # ── Close any remaining at end ──
    for pos in positions:
        capital += pos["risked"]  # return risk capital

    # ── Results ──
    total_value = capital
    total_return = (total_value - STARTING_CAPITAL) / STARTING_CAPITAL * 100
    peak_return = (peak - STARTING_CAPITAL) / STARTING_CAPITAL * 100

    if not closed_trades:
        print("❌ No trades — tighten parameters")
        return

    df_t = pd.DataFrame(closed_trades)
    wins = (df_t["r_multiple"] > 0).sum()
    total_trades = len(df_t)
    total_r = df_t["r_multiple"].sum()
    avg_r = total_r / total_trades
    win_rate = wins / total_trades * 100
    losers = df_t[df_t["r_multiple"] < 0]
    avg_loss = losers["r_multiple"].mean() if len(losers) > 0 else 0
    winners = df_t[df_t["r_multiple"] > 0]
    avg_win = winners["r_multiple"].mean() if len(winners) > 0 else 0
    pf = abs(avg_win * wins / (avg_loss * (total_trades - wins))) if len(losers) > 0 else 99

    cumulative = (1 + df_t["r_multiple"] * 0.01).prod() - 1

    print("=" * 60)
    print("  PORTFOLIO BACKTEST RESULTS (Round 4)")
    print("=" * 60)
    print(f"  Universe: {len(all_4h)} stocks (first {UNIVERSE_SIZE} of S&P 500)")
    print(f"  Timeline: {bar_count} 4h bars ({timeline[start_idx]} → {timeline[end_idx-1]})")
    print(f"  Signals scanned: {signal_count}")
    print(f"  Total trades: {total_trades}")
    print(f"  Win rate: {wins}/{total_trades} ({win_rate:.1f}%)")
    print(f"  Avg R/trade: {avg_r:+.3f}")
    print(f"  Avg win R: {avg_win:+.3f} | Avg loss R: {avg_loss:+.3f}")
    print(f"  Profit factor: {pf:.2f}")
    print(f"  Cumulative return (1% risk): {cumulative*100:+.1f}%")
    print(f"  Ending capital: ${total_value:.2f} ({total_return:+.1f}%)")
    print(f"  Max positions held: {MAX_POSITIONS}")
    print()
    
    # Exit breakdown
    print("  Exit breakdown:")
    for reason in ["TP", "SL", "EXPIRED"]:
        cnt = (df_t["exit_reason"] == reason).sum()
        avg_r_reason = df_t[df_t["exit_reason"] == reason]["r_multiple"].mean() if cnt > 0 else 0
        print(f"    {reason}: {cnt} ({cnt/max(total_trades,1)*100:.1f}%) avg {avg_r_reason:+.2f}R")

    # Top/bottom trades
    print()
    print("  Top 5 trades:")
    for _, t in df_t.nlargest(5, "r_multiple").iterrows():
        print(f"    {t['ticker']}: {t['exit_reason']} +{t['r_multiple']:.2f}R ({t['bars_held']} bars)")
    print("  Worst 5 trades:")
    for _, t in df_t.nsmallest(5, "r_multiple").iterrows():
        print(f"    {t['ticker']}: {t['exit_reason']} {t['r_multiple']:.2f}R ({t['bars_held']} bars)")


if __name__ == "__main__":
    backtest()
