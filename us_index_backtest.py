#!/usr/bin/env python3
"""
US Stock Index 8-Factor Confluence Backtester
===============================================
Applies the 8-factor confluence V2 system to Nasdaq-100, S&P 500, and Russell 2000
using daily OHLCV data from Yahoo Finance.

8 Factors (adapted for indices):
  1. Trend (linear regression slope + strength)
  2. VWAP (price vs volume-weighted average)
  3. OBV (On-Balance Volume trend)
  4. CMF (Chaikin Money Flow)
  5. MFI (Money Flow Index)
  6. Volatility Regime (ATR-based — replaces perp funding rate)
  7. Volume Profile Quality (VP concentration)
  8. Candle Pattern (engulfing, pin bars)

Usage:
  python3 us_index_backtest.py [--period 2y] [--interval 1d]
  python3 us_index_backtest.py --output ~/backtest_results.md
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import yfinance as yf


# ═══════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════

BACKTEST_CONFIG = {
    # Indices to test
    "tickers": {
        "^GSPC": "S&P 500",
    },
    # ETFs
    "etf_map": {
        "^GSPC": "SPY",
    },
    # Timeframe
    "period": "2y",        # yfinance period
    "interval": "1d",      # Daily candles
    # Capital & Risk
    "starting_capital": 100_000.0,
    "risk_per_trade": 0.01,         # 1% risk per trade
    "min_rr": 1.5,                  # Min reward:risk
    # Entry
    "min_confluence_score": 3.0,
    "require_trend_alignment": True,
    "max_open_positions": 2,
    "long_only_tickers": ["^GSPC"],  # Disable shorts
    # Exit — tuned for 1h index swing trading
    "tp1_rr": 2.5,                  # Take profit 1 (2.5R, partial close 50%)
    "tp2_rr": 5.0,                  # Take profit 2 (5.0R, full close)
    "tp1_allocation": 0.5,
    "max_hold_bars": 999,           # Effectively unlimited — let winners run
    "stop_atr_multiplier": 2.5,     # Stop = entry ± ATR × 2.5
    # VIX Filter (disabled — too restrictive)
    "vix_filter": False,
    "vix_min": 20,
    # Signal scoring weights
    "weight_trend": 2.0,
    "weight_vwap": 1.5,
    "weight_obv": 1.0,
    "weight_cmf": 1.0,
    "weight_mfi": 1.0,
    "weight_momentum": 1.0,
    "weight_volatility": 1.0,       # Replaces funding rate
    "weight_vp_quality": 2.0,
    "weight_candle": 1.5,
}


# ═══════════════════════════════════════════════
# Data Types
# ═══════════════════════════════════════════════

@dataclass
class IndicatorSnapshot:
    close: float = 0.0
    high: float = 0.0
    low: float = 0.0
    volume: float = 0.0
    
    # Volume Profile
    poc: float = 0.0
    vah: float = 0.0
    val: float = 0.0
    vp_quality: float = 0.0
    
    # VWAP
    vwap: float = 0.0
    price_vs_vwap: float = 0.0
    
    # OBV
    obv_trend: str = "neutral"
    
    # CMF
    cmf: float = 0.0
    
    # MFI
    mfi: float = 50.0
    
    # Trend
    trend: str = "neutral"
    trend_strength: float = 0.0
    
    # Volatility Regime (replaces funding)
    vol_regime: str = "normal"       # low, normal, high
    atr_pct: float = 0.0
    
    # Momentum
    momentum: float = 0.0             # ROC(10) as percentage
    
    # Volume
    volume_ratio: float = 1.0


@dataclass
class ConfluenceScore:
    total: float = 0.0
    direction: str = "none"
    
    trend_score: float = 0.0
    vwap_score: float = 0.0
    obv_score: float = 0.0
    cmf_score: float = 0.0
    mfi_score: float = 0.0
    vol_score: float = 0.0
    vp_quality_score: float = 0.0
    candle_score: float = 0.0
    momentum_score: float = 0.0
    
    long_signals: int = 0
    short_signals: int = 0
    neutral_signals: int = 0


@dataclass
class BacktestTrade:
    trade_id: int
    ticker: str
    direction: str
    entry_date: str
    entry_price: float
    stop_loss: float
    tp1: float
    tp2: float
    position_size: float
    risk_amount: float
    confluence_score: float
    signal_breakdown: str
    
    status: str = "open"
    exit_price: Optional[float] = None
    exit_date: Optional[str] = None
    exit_reason: str = ""
    pnl: float = 0.0
    pnl_pct: float = 0.0
    partial_closed: bool = False
    tp1_hit: bool = False
    bars_held: int = 0


@dataclass
class PerfMetrics:
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    avg_bars_held: float = 0.0
    best_trade_pct: float = 0.0
    worst_trade_pct: float = 0.0
    avg_confluence: float = 0.0
    sharpe: float = 0.0
    buy_hold_return: float = 0.0
    num_long: int = 0
    num_short: int = 0
    long_win_rate: float = 0.0
    short_win_rate: float = 0.0


@dataclass
class VolumeProfile:
    poc: float = 0.0
    vah: float = 0.0
    val: float = 0.0
    concentration: float = 0.0
    total_volume: float = 0.0


# ═══════════════════════════════════════════════
# Technical Indicators (ported from Hyperliquid V2)
# ═══════════════════════════════════════════════

def calculate_vwap(closes: List[float], highs: List[float], lows: List[float], volumes: List[float], lookback: int = 20) -> Optional[Tuple[float, float, float]]:
    """Calculate VWAP with std dev bands from price arrays."""
    if len(closes) < 2:
        return None
    recent_n = min(lookback, len(closes))
    recent = slice(-recent_n, None) if recent_n > 0 else slice(0, len(closes))
    
    cum_vol = 0.0
    cum_tp_vol = 0.0
    cum_tp_sq_vol = 0.0
    
    for i in range(max(0, len(closes) - recent_n), len(closes)):
        h, l, c, v = highs[i], lows[i], closes[i], volumes[i]
        if v == 0:
            continue
        tp = (h + l + c) / 3.0
        cum_vol += v
        cum_tp_vol += tp * v
        cum_tp_sq_vol += (tp * tp) * v
    
    if cum_vol == 0:
        return None
    vwap = cum_tp_vol / cum_vol
    variance = (cum_tp_sq_vol / cum_vol) - (vwap * vwap)
    std_dev = math.sqrt(max(0, variance))
    return (vwap, vwap + std_dev, vwap - std_dev)


def calculate_obv(closes: List[float], volumes: List[float], sma_period: int = 20) -> Tuple[float, float, str]:
    """Calculate On-Balance Volume."""
    if len(closes) < sma_period + 1:
        return 0, 0, "neutral"
    
    obv_values = [0.0]
    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv_values.append(obv_values[-1] + volumes[i])
        elif closes[i] < closes[i-1]:
            obv_values.append(obv_values[-1] - volumes[i])
        else:
            obv_values.append(obv_values[-1])
    
    current_obv = obv_values[-1]
    if len(obv_values) >= sma_period:
        obv_sma = sum(obv_values[-sma_period:]) / sma_period
    else:
        obv_sma = current_obv
    
    if current_obv > obv_sma * 1.01:
        trend = "bullish"
    elif current_obv < obv_sma * 0.99:
        trend = "bearish"
    else:
        trend = "neutral"
    return (current_obv, obv_sma, trend)


def calculate_cmf(closes: List[float], highs: List[float], lows: List[float], volumes: List[float], period: int = 20) -> float:
    """Chaikin Money Flow."""
    if len(closes) < period:
        return 0.0
    recent = slice(-period, None) if period > 0 else slice(0, len(closes))
    
    mfv_sum = 0.0
    vol_sum = 0.0
    for i in range(max(0, len(closes) - period), len(closes)):
        h, l, c, v = highs[i], lows[i], closes[i], volumes[i]
        if (h - l) == 0:
            continue
        mfm = ((c - l) - (h - c)) / (h - l)
        mfv_sum += mfm * v
        vol_sum += v
    return mfv_sum / vol_sum if vol_sum > 0 else 0.0


def calculate_mfi(closes: List[float], highs: List[float], lows: List[float], volumes: List[float], period: int = 14) -> float:
    """Money Flow Index."""
    if len(closes) < period + 1:
        return 50.0
    
    typical_prices = [(highs[i] + lows[i] + closes[i]) / 3.0 for i in range(len(closes))]
    
    pos_mf = 0.0
    neg_mf = 0.0
    for i in range(len(typical_prices) - period, len(typical_prices)):
        if i == 0:
            continue
        tp_change = typical_prices[i] - typical_prices[i-1]
        mf = typical_prices[i] * volumes[i]
        if tp_change > 0:
            pos_mf += mf
        elif tp_change < 0:
            neg_mf += mf
    
    if neg_mf == 0:
        return 100.0 if pos_mf > 0 else 50.0
    mf_ratio = pos_mf / neg_mf
    return 100.0 - (100.0 / (1.0 + mf_ratio))


def detect_trend(closes: List[float], lookback: int = 20) -> Tuple[str, float]:
    """Detect trend via linear regression slope + R² strength."""
    if len(closes) < lookback:
        return ("neutral", 0.0)
    recent = closes[-lookback:]
    
    n = len(recent)
    x_mean = (n - 1) / 2
    y_mean = sum(recent) / n
    
    numerator = sum((i - x_mean) * (recent[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return ("neutral", 0.0)
    
    slope = numerator / denominator
    slope_pct = (slope / y_mean) * 100 if y_mean != 0 else 0
    
    y_pred = [recent[0] + slope * i for i in range(n)]
    ss_res = sum((recent[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((recent[i] - y_mean) ** 2 for i in range(n))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    strength = min(1.0, max(0.0, r_squared))
    
    if slope_pct > 0.02:
        return ("bullish", strength)
    elif slope_pct < -0.02:
        return ("bearish", strength)
    return ("neutral", strength)


def calculate_volume_profile(closes: List[float], highs: List[float], lows: List[float], volumes: List[float], num_bins: int = 100, value_area_pct: float = 0.70) -> Optional[VolumeProfile]:
    """Volume Profile from price arrays."""
    if len(closes) < 5:
        return None
    
    price_max = max(highs)
    price_min = min(lows)
    if price_max == price_min:
        return None
    
    bin_size = (price_max - price_min) / num_bins
    volume_at_price = defaultdict(float)
    
    for i in range(len(closes)):
        o, h, l, c, v = closes[i], highs[i], lows[i], closes[i], volumes[i]
        h_actual = max(o, h, l, c)
        l_actual = min(o, h, l, c)
        
        if h_actual == l_actual:
            bin_idx = int((c - price_min) / bin_size)
            bin_idx = max(0, min(bin_idx, num_bins - 1))
            bin_price = price_min + (bin_idx + 0.5) * bin_size
            volume_at_price[bin_price] += v
        else:
            low_bin = int((l_actual - price_min) / bin_size)
            high_bin = int((h_actual - price_min) / bin_size)
            low_bin = max(0, min(low_bin, num_bins - 1))
            high_bin = max(0, min(high_bin, num_bins - 1))
            
            num_affected = high_bin - low_bin + 1
            vol_per_bin = v / num_affected
            for b in range(low_bin, high_bin + 1):
                bp = price_min + (b + 0.5) * bin_size
                volume_at_price[bp] += vol_per_bin
    
    levels = sorted(volume_at_price.items())
    total_vol = sum(v for _, v in levels)
    if total_vol == 0:
        return None
    
    # Find POC
    poc_price, poc_vol = max(levels, key=lambda x: x[1])
    
    # Value Area (top-down)
    sorted_desc = sorted(levels, key=lambda x: x[1], reverse=True)
    cum_vol = 0.0
    va_prices = []
    for p, v in sorted_desc:
        cum_vol += v
        va_prices.append(p)
        if cum_vol >= total_vol * value_area_pct:
            break
    
    vah = max(va_prices)
    val = min(va_prices)
    
    # Concentration: volume at POC vs total
    poc_idx = next(i for i, (p, _) in enumerate(levels) if p == poc_price)
    nearby_vol = poc_vol
    if poc_idx > 0:
        nearby_vol += levels[poc_idx-1][1]
    if poc_idx < len(levels) - 1:
        nearby_vol += levels[poc_idx+1][1]
    concentration = nearby_vol / total_vol
    
    return VolumeProfile(poc=poc_price, vah=vah, val=val, concentration=concentration, total_volume=total_vol)


def detect_candle_signal(close_curr: float, open_curr: float, high_curr: float, low_curr: float,
                          close_prev: float, open_prev: float) -> Optional[str]:
    """Detect bullish/bearish candle patterns."""
    body = abs(close_curr - open_curr)
    total_range = high_curr - low_curr
    if total_range == 0:
        return None
    
    lower_wick = min(open_curr, close_curr) - low_curr
    upper_wick = high_curr - max(open_curr, close_curr)
    
    # Bullish rejection (hammer)
    if (body > 0 and lower_wick > 2 * body and upper_wick < body * 0.5 and
        (close_curr - low_curr) / total_range > 0.65):
        return "bullish_rejection"
    
    # Bearish rejection (shooting star)
    if (body > 0 and upper_wick > 2 * body and lower_wick < body * 0.5 and
        (high_curr - close_curr) / total_range > 0.65):
        return "bearish_rejection"
    
    # Bullish engulfing
    if close_prev < open_prev and close_curr > open_curr and open_curr <= close_prev and close_curr >= open_prev:
        return "bullish_engulfing"
    
    # Bearish engulfing
    if close_prev > open_prev and close_curr < open_curr and open_curr >= close_prev and close_curr <= open_prev:
        return "bearish_engulfing"
    
    return None


def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    """Average True Range."""
    if len(closes) < period + 1:
        return 0.0
    
    tr_values = []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        tr_values.append(tr)
    
    if not tr_values:
        return 0.0
    return sum(tr_values[-period:]) / min(period, len(tr_values))


# ═══════════════════════════════════════════════
# Confluence Scoring (adapted for indices)
# ═══════════════════════════════════════════════

def calculate_confluence(snapshot: IndicatorSnapshot, candle_signal: Optional[str]) -> ConfluenceScore:
    """8-factor confluence score (-10 to +10). Adapted for indices (no funding rate)."""
    cfg = BACKTEST_CONFIG
    score = ConfluenceScore()
    
    # 1. Trend (weight: 2.0)
    if snapshot.trend == "bullish":
        score.trend_score = snapshot.trend_strength
    elif snapshot.trend == "bearish":
        score.trend_score = -snapshot.trend_strength
    
    # 2. VWAP (weight: 1.5) — ADAPTED FOR INDICES
    # In uptrend: above VWAP = normal trending (+0.3), below VWAP = discount (+0.5 to +1.0)
    # In downtrend: below VWAP = normal trending (-0.3), above VWAP = bounce (-0.5 to -1.0)
    if snapshot.trend == "bullish":
        if snapshot.price_vs_vwap < -0.002:
            score.vwap_score = min(1.0, abs(snapshot.price_vs_vwap) * 100)
        else:
            score.vwap_score = 0.3
    elif snapshot.trend == "bearish":
        if snapshot.price_vs_vwap > 0.002:
            score.vwap_score = -min(1.0, abs(snapshot.price_vs_vwap) * 100)
        else:
            score.vwap_score = -0.3
    else:
        if snapshot.price_vs_vwap < -0.002:
            score.vwap_score = min(0.5, abs(snapshot.price_vs_vwap) * 50)
        elif snapshot.price_vs_vwap > 0.002:
            score.vwap_score = -min(0.5, abs(snapshot.price_vs_vwap) * 50)
    
    # 3. OBV (weight: 1.0)
    if snapshot.obv_trend == "bullish":
        score.obv_score = 0.7
    elif snapshot.obv_trend == "bearish":
        score.obv_score = -0.7
    
    # 4. CMF (weight: 1.0)
    score.cmf_score = max(-1.0, min(1.0, snapshot.cmf * 2))
    
    # 5. MFI (weight: 1.0)
    if snapshot.mfi > 80:
        score.mfi_score = -0.5  # Overbought → bearish
    elif snapshot.mfi < 20:
        score.mfi_score = 0.5   # Oversold → bullish
    elif snapshot.mfi > 60:
        score.mfi_score = 0.3
    elif snapshot.mfi < 40:
        score.mfi_score = -0.3
    
    # 6. Volatility Regime (weight: 1.0) — replaces funding rate
    # Low vol = trending, high vol = choppy/risk-off
    if snapshot.vol_regime == "low":
        score.vol_score = 0.3   # Trending conditions
    elif snapshot.vol_regime == "high":
        score.vol_score = -0.3  # Choppy / risk-off
    
    # 7. Volume Profile Quality (weight: 2.0)
    if snapshot.vp_quality > 0.15:
        score.vp_quality_score = min(1.0, snapshot.vp_quality * 5)
    elif snapshot.vp_quality > 0.10:
        score.vp_quality_score = 0.5
    
    # 8. Candle Pattern (weight: 1.5)
    if candle_signal:
        if "bullish" in candle_signal:
            score.candle_score = 0.8
        elif "bearish" in candle_signal:
            score.candle_score = -0.8
    
    # 9. Momentum — ROC(10) (weight: 1.0)
    # Scale ROC to [-1, 1]: 2% ROC = +1.0, -2% = -1.0
    if snapshot.momentum != 0:
        score.momentum_score = round(max(-1.0, min(1.0, snapshot.momentum / 2)), 2)
    
    # Calculate weighted total
    weights = [
        (score.trend_score, cfg["weight_trend"]),
        (score.vwap_score, cfg["weight_vwap"]),
        (score.obv_score, cfg["weight_obv"]),
        (score.cmf_score, cfg["weight_cmf"]),
        (score.mfi_score, cfg["weight_mfi"]),
        (score.momentum_score, cfg["weight_momentum"]),
        (score.vol_score, cfg["weight_volatility"]),
        (score.vp_quality_score, cfg["weight_vp_quality"]),
        (score.candle_score, cfg["weight_candle"]),
    ]
    
    total_weight = sum(w for _, w in weights)
    weighted_sum = sum(s * w for s, w in weights)
    score.total = (weighted_sum / total_weight) * 10 if total_weight > 0 else 0
    
    # Count signal directions
    individual = [score.trend_score, score.vwap_score, score.obv_score,
                  score.cmf_score, score.mfi_score, score.momentum_score, score.vol_score,
                  score.vp_quality_score, score.candle_score]
    for s in individual:
        if s > 0.1:
            score.long_signals += 1
        elif s < -0.1:
            score.short_signals += 1
        else:
            score.neutral_signals += 1
    
    if score.total > 0.5:
        score.direction = "long"
    elif score.total < -0.5:
        score.direction = "short"
    else:
        score.direction = "none"
    
    return score


# ═══════════════════════════════════════════════
# Backtest Engine
# ═══════════════════════════════════════════════

class IndexBacktester:
    """Backtest 8-factor confluence on a US stock index."""
    
    def __init__(self, ticker: str, name: str, etf_ticker: str):
        self.ticker = ticker
        self.name = name
        self.etf_ticker = etf_ticker
        self.cfg = BACKTEST_CONFIG
        
        self.capital = self.cfg["starting_capital"]
        self.peak_capital = self.cfg["starting_capital"]
        self.equity_curve: List[float] = [self.capital]
        self.trades: List[BacktestTrade] = []
        self.open_positions: List[BacktestTrade] = []
        self.trade_counter = 0
        
        self.dates: List[str] = []
        self.opens: List[float] = []
        self.highs: List[float] = []
        self.lows: List[float] = []
        self.closes: List[float] = []
        self.volumes: List[float] = []
        self.vix_map: Dict[str, float] = {}  # date -> VIX close
    
    def fetch_data(self) -> bool:
        """Download historical OHLCV data from Yahoo Finance."""
        try:
            print(f"  Fetching {self.ticker} ({self.name})...")
            etf = yf.Ticker(self.etf_ticker)
            df = etf.history(period=self.cfg["period"], interval=self.cfg["interval"])
            
            if df.empty:
                # Try index directly
                index = yf.Ticker(self.ticker)
                df = index.history(period=self.cfg["period"], interval=self.cfg["interval"])
            
            if df.empty:
                print(f"  ⚠ No data for {self.ticker}")
                return False
            
            # Strip timezone for clean date strings
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            
            self.dates = [d.strftime("%Y-%m-%d") for d in df.index]
            self.opens = df["Open"].tolist()
            self.highs = df["High"].tolist()
            self.lows = df["Low"].tolist()
            self.closes = df["Close"].tolist()
            self.volumes = df["Volume"].tolist()
            
            # Fetch VIX data for fear/greed filter
            try:
                vix = yf.Ticker("^VIX")
                vix_df = vix.history(period=self.cfg["period"], interval=self.cfg["interval"])
                if vix_df.index.tz is not None:
                    vix_df.index = vix_df.index.tz_localize(None)
                for d in vix_df.index:
                    ds = d.strftime("%Y-%m-%d")
                    self.vix_map[ds] = float(vix_df.loc[d, "Close"])
                print(f"  VIX: {len(self.vix_map)} data points")
            except Exception as e:
                print(f"  ⚠ VIX unavailable: {e}")
            
            print(f"  Loaded {len(self.dates)} candles ({self.dates[0]} to {self.dates[-1]})")
            return True
        except Exception as e:
            print(f"  ❌ Error fetching {self.ticker}: {e}")
            return False
    
    def build_snapshot(self, idx: int) -> Optional[IndicatorSnapshot]:
        """Build indicator snapshot at candle index."""
        if idx < 30:  # Need warmup
            return None
        
        closes = self.closes[:idx+1]
        highs = self.highs[:idx+1]
        lows = self.lows[:idx+1]
        volumes = self.volumes[:idx+1]
        
        sn = IndicatorSnapshot(
            close=closes[-1],
            high=highs[-1],
            low=lows[-1],
            volume=volumes[-1],
        )
        
        # Trend
        trend, strength = detect_trend(closes, lookback=20)
        sn.trend = trend
        sn.trend_strength = strength
        
        # VWAP
        vwap_res = calculate_vwap(closes, highs, lows, volumes, lookback=20)
        if vwap_res:
            vwap, _, _ = vwap_res
            sn.vwap = vwap
            sn.price_vs_vwap = (closes[-1] - vwap) / vwap if vwap > 0 else 0
        
        # OBV
        _, _, obv_trend = calculate_obv(closes, volumes, sma_period=20)
        sn.obv_trend = obv_trend
        
        # CMF
        sn.cmf = calculate_cmf(closes, highs, lows, volumes, period=20)
        
        # MFI
        sn.mfi = calculate_mfi(closes, highs, lows, volumes, period=14)
        
        # Volume Profile
        vp = calculate_volume_profile(closes, highs, lows, volumes)
        if vp:
            sn.poc = vp.poc
            sn.vah = vp.vah
            sn.val = vp.val
            sn.vp_quality = vp.concentration
        
        # Volatility Regime (ATR-based)
        atr = calculate_atr(highs, lows, closes, period=14)
        sn.atr_pct = (atr / closes[-1]) * 100 if closes[-1] > 0 else 0
        if sn.atr_pct < 0.8:
            sn.vol_regime = "low"
        elif sn.atr_pct > 2.0:
            sn.vol_regime = "high"
        else:
            sn.vol_regime = "normal"
        
        # Volume ratio
        lookback = min(20, idx)
        if lookback > 0:
            avg_vol = sum(volumes[-lookback-1:-1]) / lookback
            sn.volume_ratio = volumes[-1] / avg_vol if avg_vol > 0 else 1.0
        
        # Momentum: ROC(10) — rate of change over 10 bars
        if len(closes) >= 11:
            sn.momentum = (closes[-1] - closes[-11]) / closes[-11] * 100
        
        return sn
    
    def run_backtest(self) -> PerfMetrics:
        """Walk through all candles and trade the 8-factor system."""
        metrics = PerfMetrics()
        idx = 0
        
        while idx < len(self.dates):
            sn = self.build_snapshot(idx)
            if sn is None:
                idx += 1
                continue
            
            # Candle signal
            candle_signal = None
            if idx > 0:
                candle_signal = detect_candle_signal(
                    self.closes[idx], self.opens[idx], self.highs[idx], self.lows[idx],
                    self.closes[idx-1], self.opens[idx-1]
                )
            
            # Confluence score
            cs = calculate_confluence(sn, candle_signal)
            
            date = self.dates[idx]
            price = self.closes[idx]
            
            # ── CHECK OPEN POSITIONS ──
            self._check_exits(idx, date, price, cs)
            
            # ── ENTRY LOGIC ──
            can_enter = len(self.open_positions) < self.cfg["max_open_positions"]
            if can_enter:
                self._try_entry(idx, date, price, sn, cs, candle_signal)
            
            # Update equity curve
            open_pnl = sum(t.pnl for t in self.open_positions)
            self.equity_curve.append(self.capital + open_pnl)
            peak = max(self.peak_capital, self.equity_curve[-1])
            self.peak_capital = peak
            
            idx += 1
        
        # Force-close remaining positions at last price
        final_price = self.closes[-1]
        final_date = self.dates[-1]
        for t in list(self.open_positions):
            t.exit_price = final_price
            t.exit_date = final_date
            t.exit_reason = "end_of_backtest"
            t.status = "closed"
            t.bars_held = len(self.dates) - idx
            # Calculate final P&L
            if t.direction == "long":
                t.pnl = (final_price - t.entry_price) / t.entry_price * 100
            else:
                t.pnl = (t.entry_price - final_price) / t.entry_price * 100
            t.pnl_pct = t.pnl
            self.open_positions.remove(t)
        
        # ── COMPUTE METRICS ──
        return self._compute_metrics()
    
    def _try_entry(self, idx: int, date: str, price: float, sn: IndicatorSnapshot, cs: ConfluenceScore, candle_signal: Optional[str] = None):
        """Evaluate and execute entry."""
        cfg = self.cfg
        
        # Check minimum score
        if abs(cs.total) < cfg["min_confluence_score"]:
            return
        
        # Require trend alignment for strong conviction
        if cfg["require_trend_alignment"]:
            if cs.total > 0 and sn.trend == "bearish":
                return
            if cs.total < 0 and sn.trend == "bullish":
                return
        
        direction = cs.direction
        if direction == "none":
            return
        
        # Long-only filter for selected tickers (disable shorts on strong trenders)
        if direction == "short" and self.ticker in cfg.get("long_only_tickers", []):
            return
        
        # VIX filter: only enter when VIX > min_vix (buy when fearful)
        if cfg.get("vix_filter", False):
            vix_val = self.vix_map.get(date[:10], 0)
            if vix_val < cfg.get("vix_min", 20):
                return
        
        # Calculate ATR for stop placement
        atr = calculate_atr(self.highs[:idx+1], self.lows[:idx+1], self.closes[:idx+1], period=14)
        atr_distance = atr * cfg["stop_atr_multiplier"]
        
        if direction == "long":
            entry = price
            stop = entry - atr_distance
            tp1 = entry + atr_distance * cfg["tp1_rr"]
            tp2 = entry + atr_distance * cfg["tp2_rr"]
        else:
            entry = price
            stop = entry + atr_distance
            tp1 = entry - atr_distance * cfg["tp1_rr"]
            tp2 = entry - atr_distance * cfg["tp2_rr"]
        
        # Risk amount
        risk_dollars = self.capital * cfg["risk_per_trade"]
        stop_distance = abs(entry - stop)
        if stop_distance == 0:
            return
        position_size = risk_dollars / stop_distance  # Units
        risk_amount = risk_dollars
        
        # Signal breakdown string
        breakdown = (f"T:{sn.trend}({sn.trend_strength:.2f}) "
                     f"V:{sn.price_vs_vwap*100:+.2f}% "
                     f"O:{sn.obv_trend} "
                     f"C:{sn.cmf:+.3f} "
                     f"M:{sn.mfi:.0f} "
                     f"Mo:{sn.momentum:+.1f}% "
                     f"VL:{sn.vol_regime} "
                     f"VP:{sn.vp_quality:.2f} "
                     f"P:{candle_signal or 'none'}")
        
        self.trade_counter += 1
        trade = BacktestTrade(
            trade_id=self.trade_counter,
            ticker=self.ticker,
            direction=direction,
            entry_date=date,
            entry_price=entry,
            stop_loss=stop,
            tp1=tp1,
            tp2=tp2,
            position_size=position_size,
            risk_amount=risk_amount,
            confluence_score=cs.total,
            signal_breakdown=breakdown,
            bars_held=0,
        )
        self.trades.append(trade)
        self.open_positions.append(trade)
        
        dir_str = "🟢 LONG" if direction == "long" else "🔴 SHORT"
        print(f"    {date} {dir_str} @ ${entry:.2f} | Score: {cs.total:+.1f} | "
              f"Stop: ${stop:.2f} | TP1: ${tp1:.2f} TP2: ${tp2:.2f}")
    
    def _check_exits(self, idx: int, date: str, price: float, cs: ConfluenceScore):
        """Check stop loss, take profit, and signal-reversal exits."""
        for t in list(self.open_positions):
            t.bars_held += 1
            exited = False
            
            if t.direction == "long":
                # Stop loss
                if price <= t.stop_loss:
                    t.exit_price = t.stop_loss
                    t.exit_reason = "stop_loss"
                    t.status = "closed"
                    exited = True
                
                # TP1 (partial)
                elif not t.partial_closed and price >= t.tp1:
                    pnl_partial = (t.tp1 - t.entry_price) / t.entry_price * 100
                    t.pnl += pnl_partial * 0.5  # TP1 allocation ~50%
                    t.partial_closed = True
                    t.tp1_hit = True
                
                # TP2 (full)
                elif t.partial_closed and price >= t.tp2:
                    t.exit_price = t.tp2
                    t.exit_reason = "tp2"
                    t.status = "closed"
                    exited = True
                
                # Max hold
                elif t.bars_held >= self.cfg["max_hold_bars"]:
                    t.exit_price = price
                    t.exit_reason = "max_hold"
                    t.status = "closed"
                    exited = True
                
                # Signal reversal (strong opposite signal)
                elif cs.total < -self.cfg["min_confluence_score"] * 1.5:
                    t.exit_price = price
                    t.exit_reason = "signal_reversal"
                    t.status = "closed"
                    exited = True
            
            else:  # Short
                if price >= t.stop_loss:
                    t.exit_price = t.stop_loss
                    t.exit_reason = "stop_loss"
                    t.status = "closed"
                    exited = True
                
                elif not t.partial_closed and price <= t.tp1:
                    t.partial_closed = True
                    t.tp1_hit = True
                
                elif t.partial_closed and price <= t.tp2:
                    t.exit_price = t.tp2
                    t.exit_reason = "tp2"
                    t.status = "closed"
                    exited = True
                
                elif t.bars_held >= self.cfg["max_hold_bars"]:
                    t.exit_price = price
                    t.exit_reason = "max_hold"
                    t.status = "closed"
                    exited = True
                
                elif cs.total > self.cfg["min_confluence_score"] * 1.5:
                    t.exit_price = price
                    t.exit_reason = "signal_reversal"
                    t.status = "closed"
                    exited = True
            
            if exited:
                t.exit_date = date
                if t.direction == "long":
                    t.pnl = (t.exit_price - t.entry_price) / t.entry_price * 100
                else:
                    t.pnl = (t.entry_price - t.exit_price) / t.entry_price * 100
                t.pnl_pct = t.pnl
                
                # Adjust capital
                self.capital *= (1 + t.pnl / 100)
                
                dir_str = "🟢" if t.direction == "long" else "🔴"
                result = "✅ WIN" if t.pnl > 0 else "❌ LOSS"
                print(f"    {date} {dir_str} EXIT {t.ticker} {result} ({t.exit_reason}) "
                      f"P&L: {t.pnl:+.2f}% | Held: {t.bars_held}d")
                
                self.open_positions.remove(t)
    
    def _compute_metrics(self) -> PerfMetrics:
        """Calculate performance metrics from completed trades."""
        m = PerfMetrics()
        
        closed = [t for t in self.trades if t.status == "closed"]
        if not closed:
            return m
        
        m.total_trades = len(closed)
        wins = [t for t in closed if t.pnl > 0]
        losses = [t for t in closed if t.pnl <= 0]
        m.wins = len(wins)
        m.losses = len(losses)
        m.win_rate = (len(wins) / len(closed) * 100) if closed else 0
        
        m.total_pnl = sum(t.pnl for t in closed)
        m.total_pnl_pct = (self.capital - self.cfg["starting_capital"]) / self.cfg["starting_capital"] * 100
        
        m.avg_win = sum(t.pnl for t in wins) / len(wins) if wins else 0
        m.avg_loss = sum(t.pnl for t in losses) / len(losses) if losses else 0
        
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        m.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        best = max(closed, key=lambda t: t.pnl)
        worst = min(closed, key=lambda t: t.pnl)
        m.best_trade_pct = best.pnl
        m.worst_trade_pct = worst.pnl
        
        m.avg_bars_held = sum(t.bars_held for t in closed) / len(closed)
        m.avg_confluence = sum(abs(t.confluence_score) for t in closed) / len(closed)
        
        # Max drawdown from equity curve
        peak = self.equity_curve[0]
        dd = 0
        dd_pct = 0
        for eq in self.equity_curve:
            if eq > peak:
                peak = eq
            drawdown = peak - eq
            if drawdown > dd:
                dd = drawdown
                dd_pct = (peak - eq) / peak * 100
        m.max_drawdown = dd
        m.max_drawdown_pct = dd_pct
        
        # Sharpe ratio (daily returns)
        if len(self.equity_curve) > 1:
            returns = [(self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
                       for i in range(1, len(self.equity_curve))]
            if returns:
                avg_ret = sum(returns) / len(returns)
                variance = sum((r - avg_ret) ** 2 for r in returns) / len(returns)
                std = math.sqrt(variance)
                m.sharpe = (avg_ret / std * math.sqrt(252)) if std > 0 else 0
        
        # Buy & hold return
        if len(self.closes) > 1:
            m.buy_hold_return = (self.closes[-1] - self.closes[0]) / self.closes[0] * 100
        
        # Long vs short breakdown
        longs = [t for t in closed if t.direction == "long"]
        shorts = [t for t in closed if t.direction == "short"]
        m.num_long = len(longs)
        m.num_short = len(shorts)
        m.long_win_rate = len([t for t in longs if t.pnl > 0]) / len(longs) * 100 if longs else 0
        m.short_win_rate = len([t for t in shorts if t.pnl > 0]) / len(shorts) * 100 if shorts else 0
        
        return m


# ═══════════════════════════════════════════════
# Report Generator
# ═══════════════════════════════════════════════

def format_report(all_results: Dict[str, PerfMetrics], all_trades: Dict[str, List[BacktestTrade]]) -> str:
    """Generate a markdown report of backtest results."""
    lines = []
    
    lines.append(f"# 📊 US Index 8-Factor Confluence Backtest Report")
    lines.append(f"")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Period:** Last {BACKTEST_CONFIG['period']} (daily candles)")
    lines.append(f"**Strategy:** V2 8-Factor Confluence (adapted for indices)")
    lines.append(f"**Capital:** ${BACKTEST_CONFIG['starting_capital']:,.0f}")
    lines.append(f"**Risk:** {BACKTEST_CONFIG['risk_per_trade']*100:.1f}% per trade")
    lines.append(f"**Min Score:** {BACKTEST_CONFIG['min_confluence_score']}")
    lines.append(f"")
    lines.append(f"## 8 Factors Used")
    lines.append(f"")
    lines.append(f"| # | Factor | Weight | What It Measures |")
    lines.append(f"|---|--------|--------|-----------------|")
    lines.append(f"| 1 | **Trend** | {BACKTEST_CONFIG['weight_trend']} | Linear regression slope + R² strength |")
    lines.append(f"| 2 | **VWAP** | {BACKTEST_CONFIG['weight_vwap']} | Price vs volume-weighted average (discount/premium) |")
    lines.append(f"| 3 | **OBV** | {BACKTEST_CONFIG['weight_obv']} | On-Balance Volume trend confirmation |")
    lines.append(f"| 4 | **CMF** | {BACKTEST_CONFIG['weight_cmf']} | Chaikin Money Flow (accumulation/distribution) |")
    lines.append(f"| 5 | **MFI** | {BACKTEST_CONFIG['weight_mfi']} | Money Flow Index (overbought/oversold) |")
    lines.append(f"| 6 | **Vol Regime** | {BACKTEST_CONFIG['weight_volatility']} | ATR-based volatility regime (replaces perp funding) |")
    lines.append(f"| 7 | **VP Quality** | {BACKTEST_CONFIG['weight_vp_quality']} | Volume Profile concentration score |")
    lines.append(f"| 8 | **Candle** | {BACKTEST_CONFIG['weight_candle']} | Engulfing / pin bar patterns |")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    
    for ticker, metrics in all_results.items():
        name = BACKTEST_CONFIG["tickers"].get(ticker, ticker)
        trades = all_trades.get(ticker, [])
        closed = [t for t in trades if t.status == "closed"]
        
        lines.append(f"## {name} ({ticker})")
        lines.append(f"")
        lines.append(f"### Summary")
        lines.append(f"")
        lines.append(f"- **Total Trades:** {metrics.total_trades}")
        lines.append(f"- **Win Rate:** {metrics.win_rate:.1f}% ({metrics.wins}W / {metrics.losses}L)")
        lines.append(f"- **Total P&L:** {metrics.total_pnl_pct:+.2f}%")
        lines.append(f"- **Profit Factor:** {metrics.profit_factor:.2f}")
        lines.append(f"- **Avg Win:** {metrics.avg_win:+.2f}% | **Avg Loss:** {metrics.avg_loss:+.2f}%")
        lines.append(f"- **Best Trade:** {metrics.best_trade_pct:+.2f}% | **Worst:** {metrics.worst_trade_pct:+.2f}%")
        lines.append(f"- **Avg Bars Held:** {metrics.avg_bars_held:.1f} days")
        lines.append(f"- **Avg Confluence Score:** {metrics.avg_confluence:.1f}")
        lines.append(f"- **Max Drawdown:** {metrics.max_drawdown_pct:.1f}%")
        lines.append(f"- **Sharpe Ratio (252d):** {metrics.sharpe:.2f}")
        lines.append(f"- **Buy & Hold Return:** {metrics.buy_hold_return:+.2f}%")
        lines.append(f"")
        lines.append(f"### Long vs Short Breakdown")
        lines.append(f"")
        lines.append(f"- **Long:** {metrics.num_long} trades ({metrics.long_win_rate:.1f}% WR)")
        lines.append(f"- **Short:** {metrics.num_short} trades ({metrics.short_win_rate:.1f}% WR)")
        lines.append(f"")
        
        if closed:
            lines.append(f"### Trade Log (last 10)")
            lines.append(f"")
            lines.append(f"| # | Date | Dir | Entry | Exit | P&L | Reason | Score |")
            lines.append(f"|---|------|-----|-------|------|-----|--------|-------|")
            for t in closed[-10:]:
                dir_sym = "L" if t.direction == "long" else "S"
                lines.append(f"| T{t.trade_id} | {t.entry_date} | {dir_sym} | ${t.entry_price:.1f} | "
                           f"${t.exit_price:.1f} | {t.pnl:+.2f}% | {t.exit_reason} | {t.confluence_score:+.1f} |")
            lines.append(f"")
        
        lines.append(f"---")
        lines.append(f"")
    
    # Combined portfolio
    lines.append(f"## 📈 Combined Portfolio View")
    lines.append(f"")
    total_trades = sum(m.total_trades for m in all_results.values())
    total_wins = sum(m.wins for m in all_results.values())
    total_losses = sum(m.losses for m in all_results.values())
    combined_wr = (total_wins / total_trades * 100) if total_trades > 0 else 0
    
    lines.append(f"- **Total Trades Across All Indices:** {total_trades}")
    lines.append(f"- **Combined Win Rate:** {combined_wr:.1f}% ({total_wins}W / {total_losses}L)")
    lines.append(f"")
    lines.append(f"| Index | Trades | Win Rate | Total P&L% | PF | Sharpe | DD% | BuyHold% |")
    lines.append(f"|-------|--------|----------|------------|----|--------|-----|----------|")
    for ticker, m in all_results.items():
        name = BACKTEST_CONFIG["tickers"].get(ticker, ticker)[:15]
        lines.append(f"| {name} | {m.total_trades} | {m.win_rate:.0f}% | {m.total_pnl_pct:+.1f}% | "
                   f"{m.profit_factor:.1f} | {m.sharpe:.1f} | {m.max_drawdown_pct:.0f}% | {m.buy_hold_return:+.1f}% |")
    
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*Automated backtest by Hermes Agent — 8-factor confluence V2 adapted for US indices*")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="US Index 8-Factor Confluence Backtester")
    parser.add_argument("--period", default="2y", help="Yahoo Finance period (default: 2y)")
    parser.add_argument("--interval", default="1d", help="Candle interval (default: 1d)")
    parser.add_argument("--output", default=None, help="Output markdown file path")
    args = parser.parse_args()
    
    if args.period:
        BACKTEST_CONFIG["period"] = args.period
    if args.interval:
        BACKTEST_CONFIG["interval"] = args.interval
    
    print(f"╔══════════════════════════════════════════════╗")
    print(f"║  US Index 8-Factor Confluence Backtester    ║")
    print(f"╚══════════════════════════════════════════════╝")
    print(f"")
    print(f"Period: {BACKTEST_CONFIG['period']} | Interval: {BACKTEST_CONFIG['interval']}")
    print(f"Capital: ${BACKTEST_CONFIG['starting_capital']:,.0f} | Risk: {BACKTEST_CONFIG['risk_per_trade']*100:.0f}%")
    print(f"Min Score: {BACKTEST_CONFIG['min_confluence_score']}")
    print(f"")
    
    all_results: Dict[str, PerfMetrics] = {}
    all_trades: Dict[str, List[BacktestTrade]] = {}
    
    for ticker, name in BACKTEST_CONFIG["tickers"].items():
        etf = BACKTEST_CONFIG["etf_map"].get(ticker, ticker)
        
        print(f"\n{'='*60}")
        print(f"📊 {name}")
        print(f"{'='*60}")
        
        bt = IndexBacktester(ticker, name, etf)
        if not bt.fetch_data():
            print(f"  ❌ Skipping {name} — data unavailable")
            continue
        
        print(f"  Running backtest...")
        metrics = bt.run_backtest()
        
        # Store final capital
        if bt.trades:
            bt_final_capital = bt.capital  # Keep reference
        
        all_results[ticker] = metrics
        all_trades[ticker] = bt.trades
        
        print(f"")
        print(f"  ── Results ──")
        print(f"  Trades: {metrics.total_trades} | WR: {metrics.win_rate:.1f}%")
        print(f"  Total P&L: {metrics.total_pnl_pct:+.2f}%")
        print(f"  Profit Factor: {metrics.profit_factor:.2f}")
        print(f"  Max DD: {metrics.max_drawdown_pct:.1f}%")
        print(f"  Sharpe: {metrics.sharpe:.2f}")
        print(f"  BuyHold: {metrics.buy_hold_return:+.2f}%")
        print(f"  Long: {metrics.num_long} ({metrics.long_win_rate:.0f}%) | Short: {metrics.num_short} ({metrics.short_win_rate:.0f}%)")
    
    # Generate report
    report = format_report(all_results, all_trades)
    
    # Output
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            f.write(report)
        print(f"\n✅ Report saved to {args.output}")
    else:
        print(f"\n{report}")
    
    print(f"\n✅ Backtest complete!")


if __name__ == "__main__":
    main()
