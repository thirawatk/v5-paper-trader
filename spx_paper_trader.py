#!/usr/bin/env python3
"""
VOO 8-Factor Confluence Paper Trader — Live Mode
==================================================
Runs the proven V5 configuration in real-time on VOO (S&P 500).
State is persisted to a JSON file so cron ticks are idempotent.

Capital:     $1,000
Risk:        1% per trade
Min Score:   3.0
Stop:        ATR × 2.5
TP2:         5.0R
Max Hold:    Unlimited (let winners run)

Silent output = no action taken (for cron).
Only prints when: entry triggered, exit triggered, or daily status.
"""

import json
import math
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yfinance as yf

# ── Config ──
CONFIG = {
    "ticker": "VOO",
    "etf": "VOO",
    "period": "1y",
    "interval": "1d",
    "capital": 1000.0,
    "risk_per_trade": 0.01,
    "min_confluence": 3.0,
    "stop_atr": 2.5,
    "tp2_rr": 5.0,
    "max_positions": 2,
}

STATE_DIR = "/root/.hermes/profiles/trader/paper_trader_data"
STATE_FILE = os.path.join(STATE_DIR, "spx_voo_paper_trader_state.json")
os.makedirs(STATE_DIR, exist_ok=True)


# ── Indicator Functions (ported from backtest) ──

def compute_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def compute_vwap(df, lookback=20):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    tv = tp * df['Volume']
    vwap = tv.rolling(lookback).sum() / df['Volume'].rolling(lookback).sum()
    return vwap

def compute_atr(df, period=14):
    h, l, c = df['High'], df['Low'], df['Close']
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def compute_obv(df):
    obv = [0.0]
    c = df['Close'].values
    v = df['Volume'].values
    for i in range(1, len(df)):
        if c[i] > c[i-1]:
            obv.append(obv[-1] + v[i])
        elif c[i] < c[i-1]:
            obv.append(obv[-1] - v[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)

def compute_cmf(df, period=20):
    mfm = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low']).replace(0, None)
    return (mfm * df['Volume']).rolling(period).sum() / df['Volume'].rolling(period).sum()

def compute_mfi(df, period=14):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    mf = tp * df['Volume']
    pf = pd.Series(0.0, index=df.index)
    nf = pd.Series(0.0, index=df.index)
    for i in range(1, len(df)):
        if tp.iloc[i] > tp.iloc[i-1]:
            pf.iloc[i] = mf.iloc[i]
        else:
            nf.iloc[i] = mf.iloc[i]
    ps = pf.rolling(period).sum()
    ns = nf.rolling(period).sum()
    ratio = ps / ns.replace(0, None)
    return 100 - (100 / (1 + ratio))

def detect_trend_slope(closes):
    n = len(closes)
    if n < 10:
        return "neutral", 0.0
    indices = list(range(n))
    mean_i = (n - 1) / 2
    mean_c = sum(closes) / n
    num = sum((i - mean_i) * (c - mean_c) for i, c in zip(indices, closes))
    den = sum((i - mean_i) ** 2 for i in indices)
    if den == 0:
        return "neutral", 0.0
    slope = num / den
    slope_pct = (slope / mean_c) * 100 if mean_c != 0 else 0
    y_pred = [closes[0] + slope * i for i in range(n)]
    ss_res = sum((closes[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((closes[i] - mean_c) ** 2 for i in range(n))
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    strength = min(1.0, max(0.0, r2))
    if slope_pct > 0.02:
        return "bullish", strength
    elif slope_pct < -0.02:
        return "bearish", strength
    return "neutral", strength

def compute_vp_quality(df, lookback=100, bins=100):
    if len(df) < lookback:
        return 0.0
    recent = df.iloc[-lookback:]
    lo = recent['Low'].min()
    hi = recent['High'].max()
    if hi == lo:
        return 0.0
    bs = (hi - lo) / bins
    vap = defaultdict(float)
    for _, r in recent.iterrows():
        cl = min(r['Open'], r['High'], r['Low'], r['Close'])
        ch = max(r['Open'], r['High'], r['Low'], r['Close'])
        lo_b = max(0, min(int((cl - lo) / bs), bins - 1))
        hi_b = max(0, min(int((ch - lo) / bs), bins - 1))
        nb = hi_b - lo_b + 1
        vb = r['Volume'] / nb if nb > 0 else r['Volume']
        for b in range(lo_b, hi_b + 1):
            bp = lo + (b + 0.5) * bs
            vap[bp] += vb
    if not vap:
        return 0.0
    tv = sum(vap.values())
    if tv == 0:
        return 0.0
    max_vol = max(vap.values())
    return max_vol / tv

def detect_candle_signal(row, prev):
    o, h, l, c = row['Open'], row['High'], row['Low'], row['Close']
    po, pc = prev['Open'], prev['Close']
    body = abs(c - o)
    tr = h - l
    if tr == 0:
        return None
    lw = min(o, c) - l
    uw = h - max(o, c)
    if body > 0 and lw > 2 * body and uw < 0.5 * body and (c - l) / tr > 0.65:
        return "bullish_rejection"
    if body > 0 and uw > 2 * body and lw < 0.5 * body and (h - c) / tr > 0.65:
        return "bearish_rejection"
    if pc < po and c > o and o <= pc and c >= po:
        return "bullish_engulfing"
    if pc > po and c < o and o >= pc and c <= po:
        return "bearish_engulfing"
    return None


# ── Scoring Engine ──

WEIGHTS = {
    "trend": 2.0, "vwap": 1.5, "obv": 1.0, "cmf": 1.0,
    "mfi": 1.0, "momentum": 1.0, "volatility": 1.0, "vp_quality": 2.0, "candle": 1.5,
}
TOTAL_W = sum(WEIGHTS.values())

def compute_confluence(df, idx) -> Tuple[float, str, dict]:
    """Returns (composite_score, direction, factor_breakdown)"""
    if idx < 30:
        return 0.0, "none", {}
    
    row = df.iloc[idx]
    c = row['Close']
    s = {}
    
    # 1. Trend
    closes = df['Close'].iloc[:idx+1].tolist()
    trend, strength = detect_trend_slope(closes[-20:])
    if trend == "bullish":
        s['trend'] = round(strength, 2)
    elif trend == "bearish":
        s['trend'] = round(-strength, 2)
    else:
        s['trend'] = 0.0
    
    # 2. VWAP (adapted for indices)
    vwap = row.get('VWAP')
    if pd.notna(vwap) and vwap > 0:
        pv = (c - vwap) / vwap
        if trend == "bullish":
            if pv < -0.002:
                s['vwap'] = round(min(1.0, abs(pv) * 100), 2)
            else:
                s['vwap'] = 0.3
        elif trend == "bearish":
            if pv > 0.002:
                s['vwap'] = round(-min(1.0, abs(pv) * 100), 2)
            else:
                s['vwap'] = -0.3
        else:
            if pv < -0.002:
                s['vwap'] = round(min(0.5, abs(pv) * 50), 2)
            elif pv > 0.002:
                s['vwap'] = round(-min(0.5, abs(pv) * 50), 2)
            else:
                s['vwap'] = 0.0
    else:
        s['vwap'] = 0.0
    
    # 3. OBV
    obv = row.get('OBV')
    obv_sma = row.get('OBV_SMA')
    if pd.notna(obv) and pd.notna(obv_sma) and obv_sma > 0:
        if obv > obv_sma * 1.01:
            s['obv'] = 0.7
        elif obv < obv_sma * 0.99:
            s['obv'] = -0.7
        else:
            s['obv'] = 0.0
    else:
        s['obv'] = 0.0
    
    # 4. CMF
    cmf = row.get('CMF')
    if pd.notna(cmf):
        s['cmf'] = round(max(-1.0, min(1.0, cmf * 2)), 2)
    else:
        s['cmf'] = 0.0
    
    # 5. MFI
    mfi = row.get('MFI')
    if pd.notna(mfi):
        if mfi > 80:
            s['mfi'] = -0.5
        elif mfi < 20:
            s['mfi'] = 0.5
        elif mfi > 60:
            s['mfi'] = 0.3
        elif mfi < 40:
            s['mfi'] = -0.3
        else:
            s['mfi'] = 0.0
    else:
        s['mfi'] = 0.0
    
    # 6. Vol regime
    atr_pct = row.get('ATR_PCT')
    if pd.notna(atr_pct):
        if atr_pct < 0.8:
            s['vol'] = 0.3
        elif atr_pct > 2.0:
            s['vol'] = -0.3
        else:
            s['vol'] = 0.0
    else:
        s['vol'] = 0.0
    
    # 7. VP Quality
    vpq = row.get('VP_Quality')
    if pd.notna(vpq):
        if vpq > 0.15:
            s['vpq'] = round(min(1.0, vpq * 5), 2)
        elif vpq > 0.10:
            s['vpq'] = 0.5
        else:
            s['vpq'] = 0.0
    else:
        s['vpq'] = 0.0
    
    # 8. Candle
    pat = row.get('CANDLE_SIG')
    if pd.notna(pat) and pat and pat != "none":
        if "bullish" in str(pat):
            s['candle'] = 0.8
        elif "bearish" in str(pat):
            s['candle'] = -0.8
        else:
            s['candle'] = 0.0
    else:
        s['candle'] = 0.0
    
    # 9. Momentum — ROC(10)
    mom = row.get('MOM')
    if pd.notna(mom):
        s['mom'] = round(max(-1.0, min(1.0, mom / 2)), 2)
    else:
        s['mom'] = 0.0
    
    # Weighted composite
    KEY_MAP = {"trend":"trend","vwap":"vwap","obv":"obv","cmf":"cmf",
               "mfi":"mfi","momentum":"mom","volatility":"vol","vp_quality":"vpq","candle":"candle"}
    wsum = sum(s.get(KEY_MAP[f], 0) * WEIGHTS[f] for f in WEIGHTS)
    total = (wsum / TOTAL_W) * 10
    
    # Direction
    if total > 0.5:
        direction = "long"
    elif total < -0.5:
        direction = "short"
    else:
        direction = "none"
    
    return round(total, 2), direction, s


# ── Data Fetching ──

def fetch_data() -> Optional[pd.DataFrame]:
    """Fetch SPY data and compute all indicators."""
    try:
        etf = yf.Ticker(CONFIG["etf"])
        df = etf.history(period=CONFIG["period"], interval=CONFIG["interval"])
        if df.empty or len(df) < 50:
            return None
        
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        
        # Compute indicators
        df['VWAP'] = compute_vwap(df)
        df['ATR'] = compute_atr(df)
        df['ATR_PCT'] = (df['ATR'] / df['Close']) * 100
        df['OBV'] = compute_obv(df)
        df['OBV_SMA'] = df['OBV'].rolling(20).mean()
        df['CMF'] = compute_cmf(df)
        df['MFI'] = compute_mfi(df)
        
        # Candle signals
        df['CANDLE_SIG'] = None
        for i in range(1, len(df)):
            df.at[df.index[i], 'CANDLE_SIG'] = detect_candle_signal(df.iloc[i], df.iloc[i-1])
        
        # VP Quality (slow — compute on last 100 bars)
        df['VP_Quality'] = 0.0
        for i in range(100, len(df)):
            vpq = compute_vp_quality(df.iloc[:i+1], lookback=100)
            df.at[df.index[i], 'VP_Quality'] = vpq
        
        # Momentum: ROC(10)
        df['MOM'] = (df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10) * 100
        
        return df
    
    except Exception as e:
        print(f"⚠ Fetch error: {e}")
        return None


# ── State Management ──

def load_state() -> Dict[str, Any]:
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "capital": CONFIG["capital"],
            "peak_capital": CONFIG["capital"],
            "positions": [],
            "trades": [],
            "last_date": "",
        }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ── Core Logic ──

def check_and_trade():
    state = load_state()
    df = fetch_data()
    if df is None or len(df) < 50:
        print("⚠ No data available")
        return
    
    latest_idx = len(df) - 1
    latest_date = df.index[latest_idx].strftime("%Y-%m-%d")
    
    # Skip if already processed this date
    if latest_date <= state.get("last_date", ""):
        return  # Silent — no new data
    
    state["last_date"] = latest_date
    capital = state["capital"]
    close = float(df['Close'].iloc[latest_idx])
    atr = float(df['ATR'].iloc[latest_idx]) if pd.notna(df['ATR'].iloc[latest_idx]) else 0
    
    # ── Check open positions ──
    positions = state.get("positions", [])
    exited = []
    
    for pos in positions:
        entry = pos["entry_price"]
        highest = max(pos.get("highest", entry), close)
        pos["highest"] = highest
        
        # Stop loss
        if close <= pos["stop"]:
            pos["exit_price"] = close
            pos["exit_date"] = latest_date
            pos["exit_reason"] = "stop_loss"
            pos["pnl_pct"] = round(((close - entry) / entry) * 100, 2)
            capital *= (1 + pos["pnl_pct"] / 100)
            exited.append(pos)
            continue
        
        # TP2 (5R)
        if close >= pos["tp2"]:
            pos["exit_price"] = close
            pos["exit_date"] = latest_date
            pos["exit_reason"] = "tp2"
            pos["pnl_pct"] = round(((close - entry) / entry) * 100, 2)
            capital *= (1 + pos["pnl_pct"] / 100)
            exited.append(pos)
            continue
        
        # TP1 partial (2.5R)
        if not pos.get("partial_closed", False) and close >= pos["tp1"]:
            pos["partial_closed"] = True
            pos["tp1_hit_date"] = latest_date
            pos["tp1_pnl"] = round(((pos["tp1"] - entry) / entry) * 100, 2)
    
    # Remove exited positions
    for p in exited:
        positions.remove(p)
        state.setdefault("trades", []).append(p)
    
    state["capital"] = round(capital, 2)
    state["positions"] = positions
    state["peak_capital"] = max(state.get("peak_capital", capital), capital)
    
    current_dd = round((state["peak_capital"] - capital) / state["peak_capital"] * 100, 1) if state["peak_capital"] > 0 else 0
    
    # Print any exits
    for p in exited:
        result = "✅ WIN" if p["pnl_pct"] > 0 else "❌ LOSS"
        print(f"{latest_date} 🏁 EXIT VOO {result} ({p['exit_reason']}) | "
              f"P&L: {p['pnl_pct']:+.2f}% | Entry: ${entry:.2f} → Exit: ${close:.2f} | "
              f"Capital: ${capital:.2f}")
    
    # ── Check entry ──
    score, direction, factors = compute_confluence(df, latest_idx)
    
    can_enter = len(positions) < CONFIG["max_positions"]
    
    if can_enter and direction == "long" and abs(score) >= CONFIG["min_confluence"] and atr > 0:
        stop = close - atr * CONFIG["stop_atr"]
        stop_dist = abs(close - stop)
        risk_amount = capital * CONFIG["risk_per_trade"]
        pos_size = risk_amount / stop_dist if stop_dist > 0 else 0
        
        tp1 = entry + stop_dist * (CONFIG["tp2_rr"] * 0.5)  # 2.5R
        tp2 = entry + stop_dist * CONFIG["tp2_rr"]           # 5.0R
        
        # Use entry
        entry = close
        
        # Factor reasons string
        bullish = [k.upper() for k, v in factors.items() if v > 0]
        bearish = [k.upper() for k, v in factors.items() if v < 0]
        reasons = f"🟢{'/'.join(bullish)}" if bullish else ""
        if bearish:
            reasons += f" 🔴{'/'.join(bearish)}"
        
        pos = {
            "entry_date": latest_date,
            "entry_price": round(entry, 2),
            "stop": round(stop, 2),
            "tp1": round(tp1, 2),
            "tp2": round(tp2, 2),
            "position_size": round(pos_size, 4),
            "risk_amount": round(risk_amount, 2),
            "confluence_score": score,
            "highest": entry,
            "partial_closed": False,
        }
        positions.append(pos)
        state["positions"] = positions
        
        print(f"{latest_date} 🟢 LONG VOO @ ${entry:.2f} | Score: {score:+.2f} | {reasons}")
    
    # Daily status update
    pos_count = len(positions)
    print(f"{latest_date} 📊 VOO ${close:.2f} | Score: {score:+.2f} | "
          f"Pos: {pos_count}" + (f" {', '.join(p['entry_date'] for p in positions)}" if pos_count else ""))
    
    save_state(state)


# ── Main ──

def main():
    # Silent unless there's actual trade action or daily status
    check_and_trade()

if __name__ == "__main__":
    main()
