#!/usr/bin/env python3
"""
8-Factor Confluence Backtest — Nasdaq 100, S&P 500, Russell 2000
=================================================================
Adapts the POC Paper Trader V2 8-factor scoring system for stocks:
  1. Trend Direction + Strength     (weight 2.0)
  2. VWAP Position                  (weight 1.5)
  3. OBV Trend Confirmation         (weight 1.0)
  4. CMF Money Flow                 (weight 1.0)
  5. MFI Overbought/Oversold        (weight 1.0)
  6. VIX Fear Sentiment             (weight 1.5) — replaces Funding Rate
  7. Volume Profile Quality         (weight 2.0)
  8. Candle Pattern Recognition     (weight 1.5)

Signal: Composite score >= 5 (on -10 to +10 scale)
R:R:    Stop = -2×ATR(14), TP1 = +1.5R, TP2 = +3.0R, max hold 20 days
Period: 2023-01-01 to 2026-07-01
"""

import yfinance as yf
import pandas as pd
import numpy as np
import sys
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ── Constants ──
FAST, SLOW, SIG = 12, 26, 9
MIN_CONFLUENCE = 4.0          # Minimum composite score for entry
FORWARD_DAYS = [5, 10, 20]
MAX_HOLD_DAYS = 20            # Max bars to hold before "expired"

# ── R:R Parameters ──
STOP_ATR_MULT = 2.0           # Stop = entry - N×ATR
TP1_R = 1.5                   # TP1 at 1.5× risk
TP2_R = 3.0                   # TP2 at 3.0× risk
SWING_LOOKBACK = 10           # For swing-low based stop (fallback)

START_DATE = "2022-10-01"     # Extra 3mo for EMA warmup
BACKTEST_START = "2023-01-01"
END_DATE = "2026-07-01"
BATCH_SIZE = 50

# ── Weights (matching V2 paper trader) ──
WEIGHTS = {
    "trend": 2.0,
    "vwap": 1.5,
    "obv": 1.0,
    "cmf": 1.0,
    "mfi": 1.0,
    "vix": 1.5,        # replaces funding_rate
    "vp_quality": 2.0,
    "candle": 1.5,
}
TOTAL_WEIGHT = sum(WEIGHTS.values())


# ═══════════════════════════════════════════════
# Indicator Computation
# ═══════════════════════════════════════════════

def compute_macd(close: pd.Series):
    ema_f = close.ewm(span=FAST, adjust=False).mean()
    ema_s = close.ewm(span=SLOW, adjust=False).mean()
    macd = ema_f - ema_s
    signal = macd.rolling(window=SIG).mean()
    hist = macd - signal
    return macd, signal, hist


def compute_ema(close: pd.Series, span: int) -> pd.Series:
    return close.ewm(span=span, adjust=False).mean()


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range."""
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def compute_vwap(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Rolling VWAP over lookback candles."""
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    tp_vol = typical * df["Volume"]
    cum_tp_vol = tp_vol.rolling(window=lookback).sum()
    cum_vol = df["Volume"].rolling(window=lookback).sum()
    vwap = cum_tp_vol / cum_vol.replace(0, np.nan)
    return vwap


def compute_vwap_bands(df: pd.DataFrame, lookback: int = 20, num_std: float = 2.0):
    """
    Compute VWAP with standard deviation bands.
    Returns: vwap_series, upper_band, lower_band
    Upper = VWAP + N×std(price), Lower = VWAP - N×std(price)
    """
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    tp_vol = typical * df["Volume"]
    cum_tp_vol = tp_vol.rolling(window=lookback).sum()
    cum_vol = df["Volume"].rolling(window=lookback).sum()
    vwap = cum_tp_vol / cum_vol.replace(0, np.nan)

    # Rolling std of typical price around VWAP
    rolling_std = typical.rolling(window=lookback).std()
    upper = vwap + num_std * rolling_std
    lower = vwap - num_std * rolling_std

    return vwap, upper, lower


def compute_obv(df: pd.DataFrame) -> pd.Series:
    obv = [0]
    for i in range(1, len(df)):
        close_diff = df["Close"].iloc[i] - df["Close"].iloc[i - 1]
        if close_diff > 0:
            obv.append(obv[-1] + df["Volume"].iloc[i])
        elif close_diff < 0:
            obv.append(obv[-1] - df["Volume"].iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)


def compute_cmf(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Chaikin Money Flow."""
    mf_multiplier = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / \
                     (df["High"] - df["Low"]).replace(0, np.nan)
    mf_volume = mf_multiplier * df["Volume"]
    cmf = mf_volume.rolling(window=period).sum() / df["Volume"].rolling(window=period).sum()
    return cmf


def compute_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Money Flow Index."""
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    mf = typical * df["Volume"]
    pos_flow = pd.Series(0.0, index=df.index)
    neg_flow = pd.Series(0.0, index=df.index)
    for i in range(1, len(df)):
        if typical.iloc[i] > typical.iloc[i - 1]:
            pos_flow.iloc[i] = mf.iloc[i]
        elif typical.iloc[i] < typical.iloc[i - 1]:
            neg_flow.iloc[i] = mf.iloc[i]
    pos_sum = pos_flow.rolling(window=period).sum()
    neg_sum = neg_flow.rolling(window=period).sum()
    mfi = 100 - (100 / (1 + pos_sum / neg_sum.replace(0, np.nan)))
    return mfi


def compute_volume_profile_quality(df: pd.DataFrame, lookback: int = 100, bins: int = 100) -> pd.Series:
    """Rolling VP quality: how concentrated is volume at POC level."""
    qualities = pd.Series(np.nan, index=df.index)
    for i in range(lookback, len(df)):
        window = df.iloc[i - lookback:i]
        price_min = window["Low"].min()
        price_max = window["High"].max()
        if price_max == price_min:
            qualities.iloc[i] = 0.0
            continue
        bin_size = (price_max - price_min) / bins
        vol_at_bin = defaultdict(float)
        for j in range(len(window)):
            o, h, l, c = window.iloc[j][["Open", "High", "Low", "Close"]]
            v = window.iloc[j]["Volume"]
            candle_low, candle_high = min(o, h, l, c), max(o, h, l, c)
            if candle_high == candle_low:
                bi = int((c - price_min) / bin_size)
                bi = max(0, min(bi, bins - 1))
                vol_at_bin[bi] += v
            else:
                lo_bi = int((candle_low - price_min) / bin_size)
                hi_bi = int((candle_high - price_min) / bin_size)
                lo_bi = max(0, min(lo_bi, bins - 1))
                hi_bi = max(0, min(hi_bi, bins - 1))
                n_bins = hi_bi - lo_bi + 1
                v_per = v / n_bins
                for b in range(lo_bi, hi_bi + 1):
                    vol_at_bin[b] += v_per
        if not vol_at_bin:
            qualities.iloc[i] = 0.0
            continue
        total_vol = sum(vol_at_bin.values())
        max_vol = max(vol_at_bin.values())
        qualities.iloc[i] = max_vol / total_vol if total_vol > 0 else 0.0
    return qualities


def detect_candle_pattern(df: pd.DataFrame, idx: int) -> str:
    """Simple candle pattern detection at a given index."""
    if idx < 1:
        return "none"
    o, h, l, c = df.iloc[idx][["Open", "High", "Low", "Close"]]
    po, ph, pl, pc = df.iloc[idx - 1][["Open", "High", "Low", "Close"]]
    body = abs(c - o)
    total_range = h - l
    if total_range == 0:
        return "none"
    body_ratio = body / total_range

    # Bullish engulfing
    if c > o and po > pc and c > po and o < pc:
        return "bullish_engulfing"
    # Bearish engulfing
    if c < o and po < pc and c < po and o > pc:
        return "bearish_engulfing"
    # Hammer (small body at top, long lower wick)
    if body_ratio < 0.3 and (c - l) > 2 * body and (h - max(o, c)) < 0.3 * body:
        return "bullish_hammer"
    # Shooting star
    if body_ratio < 0.3 and (h - max(o, c)) > 2 * body and (min(o, c) - l) < 0.3 * body:
        return "bearish_star"
    # Bullish marubozu
    if body_ratio > 0.8 and c > o and (h - c) < 0.1 * total_range:
        return "bullish_marubozu"
    # Bearish marubozu
    if body_ratio > 0.8 and c < o and (o - h) < 0.1 * total_range:
        return "bearish_marubozu"

    return "none"


# ═══════════════════════════════════════════════
# Signal Scoring (8-Factor Confluence)
# ═══════════════════════════════════════════════

@dataclass
class SignalScores:
    trend: float = 0.0
    vwap: float = 0.0
    obv: float = 0.0
    cmf: float = 0.0
    mfi: float = 0.0
    vix: float = 0.0
    vp_quality: float = 0.0
    candle: float = 0.0
    composite: float = 0.0
    long_signals: int = 0
    short_signals: int = 0
    neutral_signals: int = 0
    direction: str = "none"


def score_signal(df: pd.DataFrame, vix_val: float, idx: int) -> SignalScores:
    """Compute 8-factor confluence score at a specific candle index."""
    s = SignalScores()
    row = df.iloc[idx]
    close = row["Close"]

    # ── 1. Trend (EMA 50 vs EMA 200) ──
    ema50 = df["EMA50"].iloc[idx]
    ema200 = df["EMA200"].iloc[idx]
    if pd.notna(ema50) and pd.notna(ema200):
        if close > ema50 > ema200:
            s.trend = 1.0    # Strong uptrend
        elif close > ema50 and ema50 <= ema200:
            s.trend = 0.5    # Recovery
        elif close < ema50 > ema200:
            s.trend = 0.3    # Pullback in uptrend
        elif close < ema50 < ema200:
            s.trend = -1.0   # Strong downtrend
        elif close < ema50 and ema50 >= ema200:
            s.trend = -0.5   # Weakening
        else:
            s.trend = 0.0
    else:
        s.trend = 0.0

    # ── 2. VWAP (band-aware scoring) ──
    # Uses 2-std bands: below lower = oversold/bullish, above upper = overextended
    vwap = df["VWAP"].iloc[idx]
    vwap_upper = df["VWAP_Upper"].iloc[idx]
    vwap_lower = df["VWAP_Lower"].iloc[idx]

    if pd.notna(vwap) and pd.notna(vwap_upper) and pd.notna(vwap_lower) and vwap > 0:
        band_width = vwap_upper - vwap_lower
        if band_width > 0:
            # Normalize distance from VWAP to band width
            pct_of_band = (close - vwap) / band_width  # 0=at VWAP, +1=at upper, -1=at lower

            if pct_of_band < -1.0:
                # Deep below lower band — strong oversold, bullish reversal potential
                s.vwap = min(1.0, abs(pct_of_band) * 0.5)
            elif pct_of_band < -0.5:
                # Below lower band edge — oversold
                s.vwap = 0.5 + abs(pct_of_band + 0.5) * 0.8
            elif pct_of_band < 0:
                # Between VWAP and lower band — mild discount
                s.vwap = 0.2 + abs(pct_of_band) * 0.6
            elif pct_of_band > 1.0:
                # Way above upper band — overextended, bearish
                s.vwap = -min(1.0, (pct_of_band - 1.0) * 0.5)
            elif pct_of_band > 0.5:
                # Above upper band edge — premium, cautious
                s.vwap = -0.2 - (pct_of_band - 0.5) * 0.8
            elif pct_of_band > 0:
                # Between VWAP and upper band — slight premium
                s.vwap = -pct_of_band * 0.4
            else:
                s.vwap = 0.1  # At VWAP — neutral/slight bullish
        else:
            s.vwap = 0.0
    else:
        s.vwap = 0.0

    # ── 3. OBV Trend ──
    if idx >= 20:
        obv_now = df["OBV"].iloc[idx]
        obv_sma = df["OBV"].iloc[idx - 19:idx + 1].mean()
        if pd.notna(obv_now) and pd.notna(obv_sma) and obv_sma != 0:
            if obv_now > obv_sma * 1.02:
                s.obv = 0.7
            elif obv_now > obv_sma:
                s.obv = 0.3
            elif obv_now < obv_sma * 0.98:
                s.obv = -0.7
            elif obv_now < obv_sma:
                s.obv = -0.3
    else:
        s.obv = 0.0

    # ── 4. CMF ──
    cmf = df["CMF"].iloc[idx]
    if pd.notna(cmf):
        s.cmf = max(-1.0, min(1.0, cmf * 2.5))
    else:
        s.cmf = 0.0

    # ── 5. MFI ──
    mfi = df["MFI"].iloc[idx]
    if pd.notna(mfi):
        if mfi > 80:
            s.mfi = -0.5   # Overbought
        elif mfi < 20:
            s.mfi = 0.5    # Oversold
        elif mfi > 60:
            s.mfi = 0.3
        elif mfi < 40:
            s.mfi = -0.3
    else:
        s.mfi = 0.0

    # ── 6. VIX Fear Sentiment (replaces Funding Rate) ──
    if vix_val >= 35:
        s.vix = 0.8    # Extreme fear → contrarian bullish
    elif vix_val >= 25:
        s.vix = 0.5    # High fear
    elif vix_val >= 20:
        s.vix = 0.3    # Elevated fear
    elif vix_val < 12:
        s.vix = -0.5   # Complacency → bearish
    elif vix_val < 15:
        s.vix = -0.2   # Low fear
    else:
        s.vix = 0.0

    # ── 7. VP Quality ──
    vpq = df["VP_Quality"].iloc[idx]
    if pd.notna(vpq):
        if vpq > 0.15:
            s.vp_quality = min(1.0, vpq * 5)
        elif vpq > 0.10:
            s.vp_quality = 0.5
    else:
        s.vp_quality = 0.0

    # ── 8. Candle Pattern ──
    pattern = detect_candle_pattern(df, idx)
    if "bullish" in pattern:
        if "engulfing" in pattern:
            s.candle = 0.9
        elif "hammer" in pattern:
            s.candle = 0.7
        elif "marubozu" in pattern:
            s.candle = 0.6
        else:
            s.candle = 0.4
    elif "bearish" in pattern:
        if "engulfing" in pattern:
            s.candle = -0.9
        elif "star" in pattern:
            s.candle = -0.7
        elif "marubozu" in pattern:
            s.candle = -0.6
        else:
            s.candle = -0.4

    # ── Composite ──
    weighted = (
        s.trend * WEIGHTS["trend"] +
        s.vwap * WEIGHTS["vwap"] +
        s.obv * WEIGHTS["obv"] +
        s.cmf * WEIGHTS["cmf"] +
        s.mfi * WEIGHTS["mfi"] +
        s.vix * WEIGHTS["vix"] +
        s.vp_quality * WEIGHTS["vp_quality"] +
        s.candle * WEIGHTS["candle"]
    )
    s.composite = (weighted / TOTAL_WEIGHT) * 10

    # Count directions
    scores_list = [s.trend, s.vwap, s.obv, s.cmf, s.mfi, s.vix, s.vp_quality, s.candle]
    for val in scores_list:
        if val > 0.1:
            s.long_signals += 1
        elif val < -0.1:
            s.short_signals += 1
        else:
            s.neutral_signals += 1

    if s.composite > 0.5:
        s.direction = "long"
    elif s.composite < -0.5:
        s.direction = "short"

    return s


# ═══════════════════════════════════════════════
# R:R Outcome Determination
# ═══════════════════════════════════════════════

def determine_rr_outcome(df: pd.DataFrame, entry_idx: int, entry_price: float,
                         atr: float) -> Dict[str, Any]:
    """
    Scan forward from entry to determine R:R outcome.
    Returns: outcome, bars, exit_price, r_multiple
    """
    # Calculate levels
    stop_loss = entry_price - STOP_ATR_MULT * atr

    # Also use swing low as a tighter stop if it's above ATR stop
    swing_start = max(0, entry_idx - SWING_LOOKBACK)
    swing_low = df["Low"].iloc[swing_start:entry_idx + 1].min()
    # Use the tighter of the two stops
    sl = max(stop_loss, swing_low) if swing_low > stop_loss else stop_loss

    risk = entry_price - sl
    if risk <= 0:
        return {"outcome": "invalid", "bars": 0, "exit_price": entry_price, "r_multiple": 0}

    tp1 = entry_price + TP1_R * risk
    tp2 = entry_price + TP2_R * risk

    # Scan forward
    end_idx = min(len(df) - 1, entry_idx + MAX_HOLD_DAYS)
    for i in range(entry_idx + 1, end_idx + 1):
        low = df["Low"].iloc[i]
        high = df["High"].iloc[i]
        close = df["Close"].iloc[i]
        bars = i - entry_idx

        # Check stop loss hit first
        if low <= sl:
            exit_px = sl
            r = -1.0  # Full stop hit
            # Check if it was a gap-down through stop
            if close < sl:
                r = round((close - entry_price) / risk, 2)
            return {"outcome": "sl_hit", "bars": bars, "exit_price": round(exit_px, 2),
                    "r_multiple": r}

        # Check TP2 hit
        if high >= tp2:
            return {"outcome": "tp2_hit", "bars": bars, "exit_price": round(tp2, 2),
                    "r_multiple": TP2_R}

        # Check TP1 hit
        if high >= tp1:
            return {"outcome": "tp1_hit", "bars": bars, "exit_price": round(tp1, 2),
                    "r_multiple": TP1_R}

    # Expired — close at last available price
    final_close = df["Close"].iloc[end_idx]
    r = round((final_close - entry_price) / risk, 2)
    return {"outcome": "expired", "bars": MAX_HOLD_DAYS, "exit_price": round(final_close, 2),
            "r_multiple": r}


# ═══════════════════════════════════════════════
# Signal Dataclass
# ═══════════════════════════════════════════════

@dataclass
class Signal:
    date: str
    close: float
    atr: float
    composite: float
    direction: str
    long_signals: int
    trend: float
    vwap: float
    obv: float
    cmf: float
    mfi: float
    vix: float
    vp_quality: float
    candle: float
    candle_pattern: str
    # R:R fields
    stop_loss: float = 0.0
    tp1: float = 0.0
    tp2: float = 0.0
    outcome: str = "pending"
    bars_to_outcome: int = 0
    r_multiple: float = 0.0
    # Legacy forward returns
    ret_5d: float = 0.0
    ret_10d: float = 0.0
    ret_20d: float = 0.0
    max_dd_5d: float = 0.0
    max_dd_10d: float = 0.0
    max_dd_20d: float = 0.0


# ═══════════════════════════════════════════════
# Universe Loaders
# ═══════════════════════════════════════════════

def load_universe(filepath: str) -> List[str]:
    """Load tickers from file, skip comments and blanks."""
    tickers = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                tickers.append(line.upper())
    return tickers


def get_sp500() -> List[str]:
    return load_universe("/root/.hermes/profiles/trader/scripts/sp500_universe.txt")


def get_nasdaq100() -> List[str]:
    return load_universe("/root/.hermes/profiles/trader/scripts/nasdaq100_universe.txt")


def get_russell2000() -> List[str]:
    return load_universe("/root/.hermes/profiles/trader/scripts/russell2000_universe.txt")


# ═══════════════════════════════════════════════
# Single Stock Backtest
# ═══════════════════════════════════════════════

def backtest_stock(ticker: str, vix_map: Dict[str, float]) -> Tuple[List[Signal], bool]:
    """Run 8-factor backtest with R:R on a single stock."""
    try:
        df = yf.Ticker(ticker).history(start=START_DATE, end=END_DATE)
        if df.empty or len(df) < 200:
            return [], True
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    except Exception:
        return [], False

    # ── Compute all indicators ──
    df["ATR"] = compute_atr(df)
    df["EMA50"] = compute_ema(df["Close"], 50)
    df["EMA200"] = compute_ema(df["Close"], 200)
    df["VWAP"], df["VWAP_Upper"], df["VWAP_Lower"] = compute_vwap_bands(df)
    df["OBV"] = compute_obv(df)
    df["CMF"] = compute_cmf(df)
    df["MFI"] = compute_mfi(df)
    df["VP_Quality"] = compute_volume_profile_quality(df)

    # ── Scan for signals ──
    signals = []
    for idx in range(max(200, 50), len(df)):
        date = df.index[idx]
        date_str = date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else str(date)[:10]
        if date_str < BACKTEST_START:
            continue

        # Get VIX for this date
        vix_val = 15.0
        for d_offset in range(6):
            check_date = (date - timedelta(days=d_offset)).strftime("%Y-%m-%d")
            if check_date in vix_map:
                vix_val = vix_map[check_date]
                break

        scores = score_signal(df, vix_val, idx)
        close = df["Close"].iloc[idx]
        atr = df["ATR"].iloc[idx]

        if scores.composite < MIN_CONFLUENCE or scores.direction != "long":
            continue
        if pd.isna(atr) or atr <= 0:
            continue

        # ── Determine R:R outcome ──
        rr = determine_rr_outcome(df, idx, close, atr)

        sig = Signal(
            date=date_str,
            close=round(close, 2),
            atr=round(atr, 2),
            composite=round(scores.composite, 2),
            direction=scores.direction,
            long_signals=scores.long_signals,
            trend=round(scores.trend, 2),
            vwap=round(scores.vwap, 2),
            obv=round(scores.obv, 2),
            cmf=round(scores.cmf, 2),
            mfi=round(scores.mfi, 2),
            vix=round(scores.vix, 2),
            vp_quality=round(scores.vp_quality, 2),
            candle=round(scores.candle, 2),
            candle_pattern=detect_candle_pattern(df, idx),
            stop_loss=round(rr.get("exit_price", 0) if rr["outcome"] == "sl_hit" else
                            close - STOP_ATR_MULT * atr, 2),
            tp1=round(close + TP1_R * STOP_ATR_MULT * atr, 2),
            tp2=round(close + TP2_R * STOP_ATR_MULT * atr, 2),
            outcome=rr["outcome"],
            bars_to_outcome=rr["bars"],
            r_multiple=rr["r_multiple"],
        )

        # Legacy forward returns
        for d in FORWARD_DAYS:
            if idx + d < len(df):
                fut_close = df["Close"].iloc[idx + d]
                ret = ((fut_close - close) / close) * 100
                window_low = df["Low"].iloc[idx:idx + d + 1].min()
                dd = ((window_low - close) / close) * 100
                setattr(sig, f"ret_{d}d", round(ret, 2))
                setattr(sig, f"max_dd_{d}d", round(dd, 2))

        signals.append(sig)

    return signals, True


# ═══════════════════════════════════════════════
# Batch Backtest Runner
# ═══════════════════════════════════════════════

def run_backtest(name: str, tickers: List[str], vix_map: Dict[str, float]) -> Dict[str, Any]:
    """Run backtest on a universe of tickers."""
    print(f"\n{'='*80}")
    print(f"  {name} — {len(tickers)} tickers")
    print(f"{'='*80}")

    all_signals = []
    failed = []
    success = 0

    for i, ticker in enumerate(tickers):
        if (i + 1) % 50 == 0 or i == 0:
            print(f"  [{i+1}/{len(tickers)}] Processing... ({ticker})")

        signals_list, ok = backtest_stock(ticker, vix_map)
        if ok:
            success += 1
            if signals_list:
                all_signals.extend([{"ticker": ticker, **s.__dict__} for s in signals_list])
        else:
            failed.append(ticker)

        if (i + 1) % 20 == 0:
            time.sleep(0.5)

    print(f"\n  Done: {success}/{len(tickers)} fetched, {len(failed)} failed, {len(all_signals)} signals")
    if failed:
        print(f"  Failed: {', '.join(failed[:8])}{'...' if len(failed) > 8 else ''}")

    return {
        "name": name,
        "total_tickers": len(tickers),
        "fetched": success,
        "failed": len(failed),
        "failed_tickers": failed,
        "total_signals": len(all_signals),
        "signals": all_signals,
    }


def compute_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """Compute aggregate statistics including R:R metrics."""
    signals = results["signals"]
    n = len(signals)

    if n == 0:
        return {**results, "win_rate_20d": 0, "avg_ret_20d": 0, "avg_r": 0, "win_rate_r": 0,
                "profit_factor": 0, "expectancy_r": 0, "tp1_pct": 0, "tp2_pct": 0, "sl_pct": 0,
                "expired_pct": 0, "avg_bars": 0, "avg_composite": 0}

    # ── R:R Statistics ──
    outcomes = [s["outcome"] for s in signals]
    r_values = [s["r_multiple"] for s in signals]
    bars = [s["bars_to_outcome"] for s in signals if s["bars_to_outcome"] > 0]

    tp1_count = outcomes.count("tp1_hit")
    tp2_count = outcomes.count("tp2_hit")
    sl_count = outcomes.count("sl_hit")
    expired_count = outcomes.count("expired")

    winners = tp1_count + tp2_count
    total_closed = winners + sl_count + expired_count

    # Win rate on R:R (tp1 + tp2 = win, sl = loss, expired = neutral/partial)
    win_rate_r = round(winners / max(total_closed, 1) * 100, 1)

    # Profit factor: sum of winning R / sum of losing R
    winning_r = sum(r for s, r in zip(signals, r_values) if s["outcome"] in ("tp1_hit", "tp2_hit"))
    losing_r = abs(sum(r for s, r in zip(signals, r_values) if s["outcome"] == "sl_hit"))
    profit_factor = round(winning_r / max(losing_r, 0.001), 2)

    # Expectancy: avg R per trade
    avg_r = round(np.mean(r_values), 2) if r_values else 0

    # ── Legacy forward return stats ──
    rets_20d = [s["ret_20d"] for s in signals if s["ret_20d"] != 0]
    composites = [s["composite"] for s in signals]

    top_20d = sorted([s for s in signals if s["ret_20d"] != 0], key=lambda x: x["ret_20d"], reverse=True)
    bot_20d = sorted([s for s in signals if s["ret_20d"] != 0], key=lambda x: x["ret_20d"])

    # ── Score band analysis ──
    bands = {"5-6": [], "6-7": [], "7-8": [], "8-10": []}
    for s in signals:
        sc = s["composite"]
        if sc < 6:
            bands["5-6"].append(s)
        elif sc < 7:
            bands["6-7"].append(s)
        elif sc < 8:
            bands["7-8"].append(s)
        else:
            bands["8-10"].append(s)

    band_stats = {}
    for band_name, band_signals in bands.items():
        if band_signals:
            b_rvals = [s["r_multiple"] for s in band_signals]
            b_wins = sum(1 for s in band_signals if s["outcome"] in ("tp1_hit", "tp2_hit"))
            b_total = b_wins + sum(1 for s in band_signals if s["outcome"] in ("sl_hit", "expired"))
            band_stats[band_name] = {
                "count": len(band_signals),
                "avg_r": round(np.mean(b_rvals), 2),
                "win_rate": round(b_wins / max(b_total, 1) * 100, 1),
            }

    return {
        **results,
        # R:R metrics
        "avg_r": avg_r,
        "win_rate_r": win_rate_r,
        "profit_factor": profit_factor,
        "tp1_pct": round(tp1_count / max(n, 1) * 100, 1),
        "tp2_pct": round(tp2_count / max(n, 1) * 100, 1),
        "sl_pct": round(sl_count / max(n, 1) * 100, 1),
        "expired_pct": round(expired_count / max(n, 1) * 100, 1),
        "avg_bars": round(np.mean(bars), 1) if bars else 0,
        "outcome_counts": {"tp1": tp1_count, "tp2": tp2_count, "sl": sl_count, "expired": expired_count},
        # Legacy
        "win_rate_20d": round(sum(1 for r in rets_20d if r > 0) / max(len(rets_20d), 1) * 100, 1),
        "avg_ret_20d": round(np.mean(rets_20d), 2) if rets_20d else 0,
        "avg_composite": round(np.mean(composites), 1) if composites else 0,
        "best_20d": f"{top_20d[0]['ticker']} {top_20d[0]['date']} +{top_20d[0]['ret_20d']}%" if top_20d else None,
        "worst_20d": f"{bot_20d[0]['ticker']} {bot_20d[0]['date']} {bot_20d[0]['ret_20d']}%" if bot_20d else None,
        "top5_20d": [{"ticker": s["ticker"], "date": s["date"], "ret": s["ret_20d"],
                       "score": s["composite"], "r": s["r_multiple"]} for s in top_20d[:5]],
        "worst5_20d": [{"ticker": s["ticker"], "date": s["date"], "ret": s["ret_20d"],
                         "score": s["composite"], "r": s["r_multiple"]} for s in bot_20d[:5]],
        # Score band analysis
        "score_bands": band_stats,
    }


# ═══════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════

def main():
    print("=" * 80)
    print("  8-FACTOR CONFLUENCE BACKTEST — with R:R")
    print("  Universes: Nasdaq 100 + S&P 500 + Russell 2000")
    print(f"  Signal: Composite ≥ {MIN_CONFLUENCE}/10")
    print(f"  R:R: Stop={STOP_ATR_MULT}×ATR | TP1={TP1_R}R | TP2={TP2_R}R | Max={MAX_HOLD_DAYS}d")
    print(f"  Period: {BACKTEST_START} → {END_DATE}")
    print("=" * 80)

    t0 = time.time()

    # ── Fetch VIX ──
    print("\n[0] Fetching VIX data...")
    vix_df = yf.Ticker("^VIX").history(start=START_DATE, end=END_DATE)
    vix_map = {}
    for idx in vix_df.index:
        vix_map[idx.strftime("%Y-%m-%d")] = vix_df.loc[idx, "Close"]
    print(f"  VIX: {len(vix_map)} points | Range: {min(vix_map.values()):.1f} - {max(vix_map.values()):.1f}")

    # ── Load universes ──
    print("\n[1] Loading universes...")
    universes = {
        "NASDAQ 100": get_nasdaq100(),
        "S&P 500": get_sp500(),
    }
    for name, tickers in universes.items():
        print(f"  {name}: {len(tickers)} tickers")

    # ── Run backtests ──
    all_results = {}
    for name, tickers in universes.items():
        raw = run_backtest(name, tickers, vix_map)
        all_results[name] = compute_summary(raw)

    elapsed = time.time() - t0

    # ── Grand aggregate ──
    all_signals = []
    for r in all_results.values():
        all_signals.extend(r["signals"])

    total_tickers = sum(r["total_tickers"] for r in all_results.values())
    total_fetched = sum(r["fetched"] for r in all_results.values())
    total_signals = sum(r["total_signals"] for r in all_results.values())

    # ── PRINT RESULTS ──
    print(f"\n{'='*80}")
    print(f"  BACKTEST COMPLETE — {elapsed/60:.1f} min | {total_fetched} stocks | {total_signals} signals")
    print(f"{'='*80}")

    # ═══ R:R SUMMARY ═══
    print(f"\n{'▓'*80}")
    print(f"  R:R OUTCOMES  (Stop={STOP_ATR_MULT}×ATR | TP1={TP1_R}R | TP2={TP2_R}R | Max={MAX_HOLD_DAYS}d)")
    print(f"{'▓'*80}")
    print(f"{'Index':<18} {'Signals':>8} {'TP2':>6} {'TP1':>6} {'SL':>6} {'Exp':>6} "
          f"{'Win%':>6} {'Avg R':>7} {'PF':>6} {'Best R':>8} {'Avg Bars':>9}")
    print("-" * 105)

    for name, r in all_results.items():
        oc = r.get("outcome_counts", {})
        best_r = max([s["r_multiple"] for s in r["signals"]]) if r["signals"] else 0
        print(f"{name:<18} {r['total_signals']:>8} "
              f"{oc.get('tp2',0):>6} {oc.get('tp1',0):>6} {oc.get('sl',0):>6} {oc.get('expired',0):>6} "
              f"{r['win_rate_r']:>5.1f}% {r['avg_r']:>+6.2f} {r['profit_factor']:>5.2f} "
              f"{best_r:>+7.2f}R {r['avg_bars']:>8.1f}d")

    # Grand R:R total
    grand_r = [s["r_multiple"] for s in all_signals]
    grand_win_r = sum(1 for s in all_signals if s["outcome"] in ("tp1_hit", "tp2_hit"))
    grand_sl = sum(1 for s in all_signals if s["outcome"] == "sl_hit")
    grand_exp = sum(1 for s in all_signals if s["outcome"] == "expired")
    grand_total = grand_win_r + grand_sl + grand_exp
    grand_pf = sum(s["r_multiple"] for s in all_signals if s["outcome"] in ("tp1_hit", "tp2_hit")) / \
               max(abs(sum(s["r_multiple"] for s in all_signals if s["outcome"] == "sl_hit")), 0.001)

    print("-" * 105)
    print(f"{'GRAND TOTAL':<18} {total_signals:>8} "
          f"{sum(1 for s in all_signals if s['outcome']=='tp2_hit'):>6} "
          f"{sum(1 for s in all_signals if s['outcome']=='tp1_hit'):>6} "
          f"{grand_sl:>6} {grand_exp:>6} "
          f"{round(grand_win_r/max(grand_total,1)*100,1):>5.1f}% "
          f"{round(np.mean(grand_r),2):>+6.2f} {round(grand_pf,2):>5.2f}")

    # ═══ SCORE BAND BREAKDOWN ═══
    print(f"\n{'─'*80}")
    print(f"  SCORE BAND ANALYSIS — Does higher composite = better R:R?")
    print(f"{'─'*80}")
    print(f"{'Band':<10} {'Signals':>8} {'Avg R':>7} {'Win Rate':>9} {'TP2 %':>7} {'SL %':>6}")
    print("-" * 55)

    all_bands = {"5-6": [], "6-7": [], "7-8": [], "8-10": []}
    for s in all_signals:
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
            print(f"{band_name:<10} {len(bs):>8} {np.mean(br):>+6.2f} "
                  f"{round(bw/max(bt,1)*100,1):>8.1f}% {round(btp2/max(len(bs),1)*100,1):>6.1f}% "
                  f"{round(bsl/max(len(bs),1)*100,1):>5.1f}%")

    # ═══ LEGACY FORWARD RETURNS ═══
    print(f"\n{'─'*80}")
    print(f"  FORWARD RETURNS (reference only)")
    print(f"{'─'*80}")
    print(f"{'Index':<18} {'Win 5d':>7} {'Win 10d':>7} {'Win 20d':>7} {'Avg 20d':>8}")
    print("-" * 55)
    for name, r in all_results.items():
        print(f"{name:<18} {r['win_rate_5d']:>6.1f}% {r['win_rate_10d']:>6.1f}% "
              f"{r['win_rate_20d']:>6.1f}% {r['avg_ret_20d']:>+7.2f}%")

    # ═══ TOP 5 BY R:MULTIPLE ═══
    print(f"\n{'─'*80}")
    print(f"  TOP 10 SIGNALS BY R:MULTIPLE")
    print(f"{'─'*80}")
    print(f"{'Ticker':<8} {'Date':<12} {'Score':>6} {'Outcome':>8} {'R':>7} {'Bars':>6} {'Ret 20d':>8}")
    print("-" * 65)
    for s in sorted(all_signals, key=lambda x: x["r_multiple"], reverse=True)[:10]:
        print(f"{s['ticker']:<8} {s['date']:<12} {s['composite']:>5.1f} {s['outcome']:>8} "
              f"{s['r_multiple']:>+6.2f}R {s['bars_to_outcome']:>5}d {s['ret_20d']:>+7.2f}%")

    # ═══ WORST 5 BY R:MULTIPLE ═══
    print(f"\n{'─'*80}")
    print(f"  WORST 5 SIGNALS BY R:MULTIPLE")
    print(f"{'─'*80}")
    print(f"{'Ticker':<8} {'Date':<12} {'Score':>6} {'Outcome':>8} {'R':>7} {'Bars':>6}")
    print("-" * 50)
    for s in sorted(all_signals, key=lambda x: x["r_multiple"])[:5]:
        print(f"{s['ticker']:<8} {s['date']:<12} {s['composite']:>5.1f} {s['outcome']:>8} "
              f"{s['r_multiple']:>+6.2f}R {s['bars_to_outcome']:>5}d")

    # ═══ FACTOR CONTRIBUTION ═══
    print(f"\n{'─'*80}")
    print(f"  FACTOR CONTRIBUTION (avg score per factor)")
    print(f"{'─'*80}")
    factors = ["trend", "vwap", "obv", "cmf", "mfi", "vix", "vp_quality", "candle"]
    for f_name in factors:
        vals = [s[f_name] for s in all_signals]
        avg = np.mean(vals) if vals else 0
        pos_pct = sum(1 for v in vals if v > 0) / max(len(vals), 1) * 100
        bar = "█" * int(abs(avg) * 10)
        print(f"  {f_name:<12} avg={avg:>+6.2f}  pos={pos_pct:>5.1f}%  {bar}")

    # ── Save JSON ──
    output = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "period": f"{BACKTEST_START} → {END_DATE}",
            "min_confluence_score": MIN_CONFLUENCE,
            "rr_params": {
                "stop_atr_mult": STOP_ATR_MULT,
                "tp1_r": TP1_R,
                "tp2_r": TP2_R,
                "max_hold_days": MAX_HOLD_DAYS,
            },
            "weights": WEIGHTS,
            "factors": factors,
        },
        "grand_summary": {
            "total_tickers": total_tickers,
            "total_fetched": total_fetched,
            "total_signals": total_signals,
            "avg_r": round(np.mean(grand_r), 2),
            "win_rate_r": round(grand_win_r / max(grand_total, 1) * 100, 1),
            "profit_factor": round(grand_pf, 2),
            "elapsed_minutes": round(elapsed / 60, 1),
        },
        "by_index": {},
    }
    for name, r in all_results.items():
        output["by_index"][name] = {
            k: v for k, v in r.items()
            if k not in ("signals", "failed_tickers")
        }
        output["by_index"][name]["top10_by_r"] = sorted(
            [s for s in r["signals"] if s["r_multiple"] != 0],
            key=lambda x: x["r_multiple"], reverse=True
        )[:10]

    out_path = "/root/.hermes/profiles/trader/scripts/backtest_8factor_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  📁 Full results: {out_path}")


if __name__ == "__main__":
    main()
