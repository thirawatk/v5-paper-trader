#!/usr/bin/env python3
"""
POC Paper Trader V2 — Multi-Factor Confluence Edition
======================================================
Enhanced POC paper trading with:
  - VWAP (Volume-Weighted Average Price) confluence
  - OBV (On-Balance Volume) trend confirmation
  - CMF (Chaikin Money Flow) money flow direction
  - MFI (Money Flow Index) overbought/oversold
  - Funding Rate sentiment from Hyperliquid
  - Volume Profile quality scoring
  - Composite confluence score (-10 to +10)

Usage:
  python3 poc_paper_trader_v2.py BTC --interval 1h --hours 168
  python3 poc_paper_trader_v2.py ETH --interval 15m --hours 72 --min-score 5
  python3 poc_paper_trader_v2.py BTC --interval 4h --hours 336 --json

Requires: Hyperliquid API (stdlib only, no external deps)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

# Reuse Hyperliquid client for data fetching
import os as _os
_hl_script_dir = "/root/.hermes/profiles/trader/skills/hyperliquid/scripts"
if _hl_script_dir not in sys.path:
    sys.path.insert(0, _hl_script_dir)
from hyperliquid_client import (
    _post_info, _normalize_candles, _normalize_funding_history,
    _hours_ago_ms, _safe_float, _compact_number,
    _format_price, _format_percent, _format_fraction_percent, _format_timestamp_ms
)


# ═══════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════

@dataclass
class POCConfig:
    """V2 Configuration with multi-factor confluence"""
    # Volume Profile
    vp_lookback: int = 100
    price_bins: int = 100
    value_area_pct: float = 0.70
    
    # Entry Logic
    poc_tolerance_pct: float = 0.003
    min_candles_between_retests: int = 5
    
    # Confluence Scoring
    min_confluence_score: int = 5      # Minimum score to enter (scale -10 to +10)
    require_trend_alignment: bool = True
    
    # Signal Weights (used in composite score)
    weight_trend: float = 2.0
    weight_vwap: float = 1.5
    weight_obv: float = 1.0
    weight_cmf: float = 1.0
    weight_mfi: float = 1.0
    weight_momentum: float = 1.0
    weight_funding: float = 1.5
    weight_vp_quality: float = 2.0
    weight_candle_pattern: float = 1.5
    weight_wyckoff_structure: float = 2.5   # Wyckoff context + events (new)
    weight_vpoc_migration: float = 1.5      # VPOC migration trend health (new)
    
    # Risk Management
    risk_per_trade: float = 0.01
    min_rr_ratio: float = 1.5
    max_open_trades: int = 3
    stop_buffer_pct: float = 0.002
    
    # Take Profit
    tp1_rr: float = 1.5
    tp2_rr: float = 3.0
    
    # Performance
    starting_capital: float = 10000.0
    
    # Debug
    verbose: bool = False


# ═══════════════════════════════════════════════
# Technical Indicators
# ═══════════════════════════════════════════════

@dataclass
class IndicatorSnapshot:
    """All indicator values at a single candle"""
    # Price
    close: float = 0.0
    high: float = 0.0
    low: float = 0.0
    volume: float = 0.0
    
    # Volume Profile
    poc: float = 0.0
    vah: float = 0.0
    val: float = 0.0
    vp_quality: float = 0.0       # 0-1, how concentrated is POC
    poc_distance_pct: float = 0.0  # Distance from price to POC
    
    # VWAP
    vwap: float = 0.0
    vwap_upper: float = 0.0
    vwap_lower: float = 0.0
    price_vs_vwap: float = 0.0    # % difference
    
    # OBV
    obv: float = 0.0
    obv_sma: float = 0.0
    obv_trend: str = "neutral"     # bullish, bearish, neutral
    
    # CMF
    cmf: float = 0.0
    cmf_trend: str = "neutral"
    
    # MFI
    mfi: float = 50.0
    mfi_zone: str = "neutral"      # overbought, oversold, neutral
    
    # Trend
    trend: str = "neutral"
    trend_strength: float = 0.0    # 0-1
    
    # Funding
    funding_rate: float = 0.0
    funding_sentiment: str = "neutral"
    
    # Momentum (ROC-10)
    momentum: float = 0.0
    
    # Volume
    volume_ratio: float = 1.0      # Current vol / avg vol


# ─────────────────────────────────────────────
# Volume Profile
# ─────────────────────────────────────────────

@dataclass
class VolumeLevel:
    price: float
    volume: float
    pct_of_total: float = 0.0


@dataclass
class VolumeProfile:
    poc: float
    vah: float
    val: float
    levels: List[VolumeLevel] = field(default_factory=list)
    total_volume: float = 0.0
    poc_volume: float = 0.0
    concentration: float = 0.0    # How concentrated is volume at POC (0-1)


def calculate_volume_profile(
    candles: List[Dict[str, Any]],
    num_bins: int = 100,
    value_area_pct: float = 0.70
) -> Optional[VolumeProfile]:
    """Calculate Volume Profile from OHLCV candles"""
    if len(candles) < 5:
        return None
    
    all_highs = [_safe_float(c.get("high")) for c in candles]
    all_lows = [_safe_float(c.get("low")) for c in candles]
    clean_highs = [h for h in all_highs if h is not None]
    clean_lows = [l for l in all_lows if l is not None]
    
    if not clean_highs or not clean_lows:
        return None
    
    price_max = max(clean_highs)
    price_min = min(clean_lows)
    
    if price_max == price_min:
        return None
    
    bin_size = (price_max - price_min) / num_bins
    volume_at_price = defaultdict(float)
    
    for candle in candles:
        o = _safe_float(candle.get("open"))
        h = _safe_float(candle.get("high"))
        l = _safe_float(candle.get("low"))
        c = _safe_float(candle.get("close"))
        v = _safe_float(candle.get("volume"))
        
        if any(x is None for x in [o, h, l, c, v]) or v == 0:
            continue
        
        candle_low = min(o, h, l, c)
        candle_high = max(o, h, l, c)
        
        if candle_high == candle_low:
            bin_idx = int((c - price_min) / bin_size)
            bin_idx = max(0, min(bin_idx, num_bins - 1))
            bin_price = price_min + (bin_idx + 0.5) * bin_size
            volume_at_price[bin_price] += v
        else:
            low_bin = int((candle_low - price_min) / bin_size)
            high_bin = int((candle_high - price_min) / bin_size)
            low_bin = max(0, min(low_bin, num_bins - 1))
            high_bin = max(0, min(high_bin, num_bins - 1))
            
            num_affected_bins = high_bin - low_bin + 1
            volume_per_bin = v / num_affected_bins
            
            for b in range(low_bin, high_bin + 1):
                bin_price = price_min + (b + 0.5) * bin_size
                volume_at_price[bin_price] += volume_per_bin
    
    levels = []
    total_volume = 0.0
    for price, vol in sorted(volume_at_price.items()):
        total_volume += vol
        levels.append(VolumeLevel(price=price, volume=vol))
    
    if total_volume == 0:
        return None
    
    for level in levels:
        level.pct_of_total = level.volume / total_volume
    
    poc_level = max(levels, key=lambda x: x.volume)
    poc = poc_level.price
    poc_volume = poc_level.volume
    
    # Value Area
    sorted_by_volume = sorted(levels, key=lambda x: x.volume, reverse=True)
    cumulative_volume = 0.0
    value_area_levels = []
    
    for level in sorted_by_volume:
        cumulative_volume += level.volume
        value_area_levels.append(level)
        if cumulative_volume >= total_volume * value_area_pct:
            break
    
    value_area_prices = [l.price for l in value_area_levels]
    vah = max(value_area_prices)
    val = min(value_area_prices)
    
    # Concentration: what % of total volume is at POC level ± 1 bin
    poc_idx = levels.index(poc_level) if poc_level in levels else -1
    if poc_idx >= 0:
        nearby_volume = poc_level.volume
        if poc_idx > 0:
            nearby_volume += levels[poc_idx - 1].volume
        if poc_idx < len(levels) - 1:
            nearby_volume += levels[poc_idx + 1].volume
        concentration = nearby_volume / total_volume
    else:
        concentration = 0.0
    
    return VolumeProfile(
        poc=poc,
        vah=vah,
        val=val,
        levels=levels,
        total_volume=total_volume,
        poc_volume=poc_volume,
        concentration=concentration,
    )


# ─────────────────────────────────────────────
# VWAP Calculator
# ─────────────────────────────────────────────

def calculate_vwap(
    candles: List[Dict[str, Any]],
    lookback: int = 20
) -> Optional[Tuple[float, float, float]]:
    """
    Calculate VWAP with standard deviation bands.
    Returns: (vwap, upper_band, lower_band)
    """
    if len(candles) < 2:
        return None
    
    recent = candles[-lookback:] if lookback > 0 else candles
    
    cum_vol = 0.0
    cum_tp_vol = 0.0
    cum_tp_sq_vol = 0.0
    
    for candle in recent:
        h = _safe_float(candle.get("high"))
        l = _safe_float(candle.get("low"))
        c = _safe_float(candle.get("close"))
        v = _safe_float(candle.get("volume"))
        
        if any(x is None for x in [h, l, c, v]) or v == 0:
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


# ─────────────────────────────────────────────
# OBV Calculator
# ─────────────────────────────────────────────

def calculate_obv(
    candles: List[Dict[str, Any]],
    sma_period: int = 20
) -> Optional[Tuple[float, float, str]]:
    """
    Calculate On-Balance Volume with SMA.
    Returns: (obv, obv_sma, trend)
    """
    if len(candles) < sma_period + 1:
        return None
    
    obv_values = [0.0]
    
    for i in range(1, len(candles)):
        c_prev = _safe_float(candles[i-1].get("close"))
        c_curr = _safe_float(candles[i].get("close"))
        v_curr = _safe_float(candles[i].get("volume"))
        
        if any(x is None for x in [c_prev, c_curr, v_curr]):
            obv_values.append(obv_values[-1])
            continue
        
        if c_curr > c_prev:
            obv_values.append(obv_values[-1] + v_curr)
        elif c_curr < c_prev:
            obv_values.append(obv_values[-1] - v_curr)
        else:
            obv_values.append(obv_values[-1])
    
    current_obv = obv_values[-1]
    
    # SMA of OBV
    if len(obv_values) >= sma_period:
        obv_sma = sum(obv_values[-sma_period:]) / sma_period
    else:
        obv_sma = current_obv
    
    # Trend
    if current_obv > obv_sma * 1.02:
        trend = "bullish"
    elif current_obv < obv_sma * 0.98:
        trend = "bearish"
    else:
        trend = "neutral"
    
    return (current_obv, obv_sma, trend)


# ─────────────────────────────────────────────
# CMF Calculator
# ─────────────────────────────────────────────

def calculate_cmf(
    candles: List[Dict[str, Any]],
    period: int = 20
) -> Optional[float]:
    """
    Calculate Chaikin Money Flow.
    Returns: CMF value (-1 to +1)
    """
    if len(candles) < period:
        return None
    
    recent = candles[-period:]
    
    mfv_sum = 0.0
    vol_sum = 0.0
    
    for candle in recent:
        h = _safe_float(candle.get("high"))
        l = _safe_float(candle.get("low"))
        c = _safe_float(candle.get("close"))
        v = _safe_float(candle.get("volume"))
        
        if any(x is None for x in [h, l, c, v]) or (h - l) == 0:
            continue
        
        # Money Flow Multiplier
        mfm = ((c - l) - (h - c)) / (h - l)
        mfv = mfm * v
        
        mfv_sum += mfv
        vol_sum += v
    
    if vol_sum == 0:
        return 0.0
    
    return mfv_sum / vol_sum


# ─────────────────────────────────────────────
# MFI Calculator
# ─────────────────────────────────────────────

def calculate_mfi(
    candles: List[Dict[str, Any]],
    period: int = 14
) -> Optional[float]:
    """
    Calculate Money Flow Index.
    Returns: MFI value (0-100)
    """
    if len(candles) < period + 1:
        return None
    
    typical_prices = []
    volumes = []
    
    for candle in candles[-(period + 1):]:
        h = _safe_float(candle.get("high"))
        l = _safe_float(candle.get("low"))
        c = _safe_float(candle.get("close"))
        v = _safe_float(candle.get("volume"))
        
        if any(x is None for x in [h, l, c, v]):
            continue
        
        typical_prices.append((h + l + c) / 3.0)
        volumes.append(v)
    
    if len(typical_prices) < period + 1:
        return 50.0  # Default neutral
    
    pos_mf = 0.0
    neg_mf = 0.0
    
    for i in range(1, len(typical_prices)):
        tp_change = typical_prices[i] - typical_prices[i-1]
        mf = typical_prices[i] * volumes[i]
        
        if tp_change > 0:
            pos_mf += mf
        elif tp_change < 0:
            neg_mf += mf
    
    if neg_mf == 0:
        return 100.0
    
    mf_ratio = pos_mf / neg_mf
    mfi = 100.0 - (100.0 / (1.0 + mf_ratio))
    
    return mfi


# ─────────────────────────────────────────────
# Trend Detection
# ─────────────────────────────────────────────

def detect_trend(
    candles: List[Dict[str, Any]],
    lookback: int = 20
) -> Tuple[str, float]:
    """
    Detect trend using linear regression.
    Returns: (trend, strength) where strength is 0-1
    """
    if len(candles) < lookback:
        return ("neutral", 0.0)
    
    recent = candles[-lookback:]
    closes = [_safe_float(c.get("close")) for c in recent]
    closes = [c for c in closes if c is not None]
    
    if len(closes) < 10:
        return ("neutral", 0.0)
    
    n = len(closes)
    x_mean = (n - 1) / 2
    y_mean = sum(closes) / n
    
    numerator = sum((i - x_mean) * (closes[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return ("neutral", 0.0)
    
    slope = numerator / denominator
    slope_pct = (slope / y_mean) * 100 if y_mean != 0 else 0
    
    # Strength based on R-squared
    y_pred = [closes[0] + slope * i for i in range(n)]
    ss_res = sum((closes[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((closes[i] - y_mean) ** 2 for i in range(n))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    strength = min(1.0, max(0.0, r_squared))
    
    if slope_pct > 0.03:
        return ("bullish", strength)
    elif slope_pct < -0.03:
        return ("bearish", strength)
    else:
        return ("neutral", strength)


# ─────────────────────────────────────────────
# Funding Rate Sentiment
# ─────────────────────────────────────────────

def fetch_funding_sentiment(
    coin: str,
    hours: float = 72
) -> Tuple[float, str]:
    """
    Fetch funding rate from Hyperliquid and determine sentiment.
    Returns: (funding_rate, sentiment)
    """
    try:
        end_ms = int(time.time() * 1000)
        start_ms = _hours_ago_ms(hours, end_ms)
        
        payload = {
            "type": "fundingHistory",
            "coin": coin,
            "startTime": start_ms,
            "endTime": end_ms,
        }
        
        raw = _post_info(payload)
        funding_history = _normalize_funding_history(raw)
        
        if not funding_history:
            return (0.0, "neutral")
        
        # Get recent funding rates
        rates = []
        for item in funding_history[-10:]:  # Last 10 funding intervals
            rate = _safe_float(item.get("funding_rate"))
            if rate is not None:
                rates.append(rate)
        
        if not rates:
            return (0.0, "neutral")
        
        avg_rate = sum(rates) / len(rates)
        latest_rate = rates[-1]
        
        # Sentiment based on absolute level and direction
        if latest_rate > 0.0005:  # > 0.05% per hour = extremely positive
            sentiment = "extremely_bullish"
        elif latest_rate > 0.0001:
            sentiment = "bullish"
        elif latest_rate < -0.0005:
            sentiment = "extremely_bearish"
        elif latest_rate < -0.0001:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        return (avg_rate, sentiment)
    
    except Exception:
        return (0.0, "neutral")


# ─────────────────────────────────────────────
# Candle Patterns
# ─────────────────────────────────────────────

def is_bullish_rejection(candle: Dict[str, Any]) -> bool:
    """Hammer / pin bar at support"""
    o = _safe_float(candle.get("open"))
    h = _safe_float(candle.get("high"))
    l = _safe_float(candle.get("low"))
    c = _safe_float(candle.get("close"))
    
    if any(x is None for x in [o, h, l, c]):
        return False
    
    body = abs(c - o)
    total_range = h - l
    if total_range == 0:
        return False
    
    lower_wick = min(o, c) - l
    upper_wick = h - max(o, c)
    
    return (
        body > 0 and
        lower_wick > 2 * body and
        upper_wick < body * 0.5 and
        (c - l) / total_range > 0.65
    )


def is_bearish_rejection(candle: Dict[str, Any]) -> bool:
    """Shooting star at resistance"""
    o = _safe_float(candle.get("open"))
    h = _safe_float(candle.get("high"))
    l = _safe_float(candle.get("low"))
    c = _safe_float(candle.get("close"))
    
    if any(x is None for x in [o, h, l, c]):
        return False
    
    body = abs(c - o)
    total_range = h - l
    if total_range == 0:
        return False
    
    lower_wick = min(o, c) - l
    upper_wick = h - max(o, c)
    
    return (
        body > 0 and
        upper_wick > 2 * body and
        lower_wick < body * 0.5 and
        (h - c) / total_range > 0.65
    )


def is_bullish_engulfing(candle: Dict[str, Any], prev: Dict[str, Any]) -> bool:
    o = _safe_float(candle.get("open"))
    c = _safe_float(candle.get("close"))
    po = _safe_float(prev.get("open"))
    pc = _safe_float(prev.get("close"))
    
    if any(x is None for x in [o, c, po, pc]):
        return False
    
    return (pc < po and c > o and o <= pc and c >= po)


def is_bearish_engulfing(candle: Dict[str, Any], prev: Dict[str, Any]) -> bool:
    o = _safe_float(candle.get("open"))
    c = _safe_float(candle.get("close"))
    po = _safe_float(prev.get("open"))
    pc = _safe_float(prev.get("close"))
    
    if any(x is None for x in [o, c, po, pc]):
        return False
    
    return (pc > po and c < o and o >= pc and c <= po)


def get_candle_signal(candle: Dict[str, Any], prev: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Detect candle pattern, return signal type"""
    if is_bullish_rejection(candle):
        return "bullish_rejection"
    elif is_bearish_rejection(candle):
        return "bearish_rejection"
    elif prev is not None:
        if is_bullish_engulfing(candle, prev):
            return "bullish_engulfing"
        elif is_bearish_engulfing(candle, prev):
            return "bearish_engulfing"
    return None


# ═══════════════════════════════════════════════
# Confluence Scoring System
# ═══════════════════════════════════════════════

@dataclass
class ConfluenceScore:
    """Multi-factor confluence score breakdown"""
    total: float = 0.0
    direction: str = "none"        # long, short, none
    
    # Individual scores (-1 to +1 each)
    trend_score: float = 0.0
    vwap_score: float = 0.0
    obv_score: float = 0.0
    cmf_score: float = 0.0
    mfi_score: float = 0.0
    funding_score: float = 0.0
    vp_quality_score: float = 0.0
    candle_score: float = 0.0
    
    # Wyckoff 2.0 scores (-1 to +1 each)
    wyckoff_structure_score: float = 0.0  # Context + events (Spring/Upthrust/SOS/SOW)
    wyckoff_vpoc_score: float = 0.0       # VPOC migration & trend health
    
    # Momentum
    momentum_score: float = 0.0
    
    # Breakdown
    long_signals: int = 0
    short_signals: int = 0
    neutral_signals: int = 0


def calculate_confluence(
    snapshot: IndicatorSnapshot,
    candle_signal: Optional[str],
    config: POCConfig,
    wyckoff_structure_score: float = 0.0,
    wyckoff_vpoc_score: float = 0.0,
) -> ConfluenceScore:
    """
    Calculate composite confluence score from all indicators.
    Wyckoff 2.0 scores are folded in as structural context + VPOC migration.
    Scale: -10 to +10 (positive = long, negative = short)
    """
    score = ConfluenceScore()
    
    # ── 1. Trend Score (weight: 2.0) ──
    if snapshot.trend == "bullish":
        score.trend_score = snapshot.trend_strength
    elif snapshot.trend == "bearish":
        score.trend_score = -snapshot.trend_strength
    else:
        score.trend_score = 0.0
    
    # ── 2. VWAP Score (weight: 1.5) ──
    # Price below VWAP in uptrend = bullish (discount)
    # Price above VWAP in downtrend = bearish (premium)
    if snapshot.price_vs_vwap < -0.002:  # > 0.2% below VWAP
        score.vwap_score = min(1.0, abs(snapshot.price_vs_vwap) * 100)
    elif snapshot.price_vs_vwap > 0.002:
        score.vwap_score = -min(1.0, abs(snapshot.price_vs_vwap) * 100)
    else:
        score.vwap_score = 0.0
    
    # ── 3. OBV Score (weight: 1.0) ──
    if snapshot.obv_trend == "bullish":
        score.obv_score = 0.7
    elif snapshot.obv_trend == "bearish":
        score.obv_score = -0.7
    else:
        score.obv_score = 0.0
    
    # ── 4. CMF Score (weight: 1.0) ──
    # CMF directly represents money flow direction
    score.cmf_score = max(-1.0, min(1.0, snapshot.cmf * 2))
    
    # ── 5. MFI Score (weight: 1.0) ──
    # Contrarian at extremes, trend-following in middle
    if snapshot.mfi > 80:
        score.mfi_score = -0.5  # Overbought → bearish
    elif snapshot.mfi < 20:
        score.mfi_score = 0.5   # Oversold → bullish
    elif snapshot.mfi > 60:
        score.mfi_score = 0.3   # Bullish momentum
    elif snapshot.mfi < 40:
        score.mfi_score = -0.3  # Bearish momentum
    else:
        score.mfi_score = 0.0
    
    # ── 6. Funding Rate Score (weight: 1.5) ──
    # Contrarian: extreme positive funding = overleveraged longs
    if snapshot.funding_sentiment == "extremely_bullish":
        score.funding_score = -0.5  # Contrarian short
    elif snapshot.funding_sentiment == "bullish":
        score.funding_score = 0.2   # Mild bullish
    elif snapshot.funding_sentiment == "extremely_bearish":
        score.funding_score = 0.5   # Contrarian long
    elif snapshot.funding_sentiment == "bearish":
        score.funding_score = -0.2  # Mild bearish
    else:
        score.funding_score = 0.0
    
    # ── 7. Volume Profile Quality Score (weight: 2.0) ──
    # High concentration = strong POC = high probability zone
    if snapshot.vp_quality > 0.15:
        score.vp_quality_score = min(1.0, snapshot.vp_quality * 5)
    elif snapshot.vp_quality > 0.10:
        score.vp_quality_score = 0.5
    else:
        score.vp_quality_score = 0.0
    
    # ── 8. Candle Pattern Score (weight: 1.5) ──
    if candle_signal:
        if "bullish" in candle_signal:
            score.candle_score = 0.8
        elif "bearish" in candle_signal:
            score.candle_score = -0.8
    
    # ── 9. Momentum Score (weight: 1.0) ──
    # ROC-10 scaled to [-1, 1]: 2% ROC = +1.0
    if snapshot.momentum != 0:
        score.momentum_score = max(-1.0, min(1.0, snapshot.momentum / 2))
    
    # ── 10. Wyckoff Structure Score (weight: 2.5) ──
    score.wyckoff_structure_score = wyckoff_structure_score

    # ── 10. Wyckoff VPOC Migration Score (weight: 1.5) ──
    score.wyckoff_vpoc_score = wyckoff_vpoc_score

    # ── Calculate Composite Score ──
    total_weight = (
        config.weight_trend +
        config.weight_vwap +
        config.weight_obv +
        config.weight_cmf +
        config.weight_mfi +
        config.weight_momentum +
        config.weight_funding +
        config.weight_vp_quality +
        config.weight_candle_pattern +
        config.weight_wyckoff_structure +
        config.weight_vpoc_migration
    )

    weighted_sum = (
        score.trend_score * config.weight_trend +
        score.vwap_score * config.weight_vwap +
        score.obv_score * config.weight_obv +
        score.cmf_score * config.weight_cmf +
        score.mfi_score * config.weight_mfi +
        score.momentum_score * config.weight_momentum +
        score.funding_score * config.weight_funding +
        score.vp_quality_score * config.weight_vp_quality +
        score.candle_score * config.weight_candle_pattern +
        score.wyckoff_structure_score * config.weight_wyckoff_structure +
        score.wyckoff_vpoc_score * config.weight_vpoc_migration
    )
    
    # Normalize to -10 to +10
    score.total = (weighted_sum / total_weight) * 10
    
    # Count signal directions
    individual_scores = [
        score.trend_score,
        score.vwap_score,
        score.obv_score,
        score.cmf_score,
        score.mfi_score,
        score.momentum_score,
        score.funding_score,
        score.vp_quality_score,
        score.candle_score,
        score.wyckoff_structure_score,
        score.wyckoff_vpoc_score,
    ]
    
    for s in individual_scores:
        if s > 0.1:
            score.long_signals += 1
        elif s < -0.1:
            score.short_signals += 1
        else:
            score.neutral_signals += 1
    
    # Determine direction
    if score.total > 0.5:
        score.direction = "long"
    elif score.total < -0.5:
        score.direction = "short"
    else:
        score.direction = "none"
    
    return score


# ═══════════════════════════════════════════════
# Wyckoff 2.0 — Structure Detection & Event Scoring
# ═══════════════════════════════════════════════

@dataclass
class WyckoffStructure:
    """Detected Wyckoff structure context"""
    context: str = "unknown"           # range, trend_up, trend_down
    structure_type: str = "unknown"    # accumulation, distribution, markup, markdown
    phase: str = "unknown"             # A, B, C, D, E, or trend
    top: float = 0.0                   # Range top / resistance
    bottom: float = 0.0                # Range bottom / support
    creek: float = 0.0                 # Key support level (Creek)
    ice: float = 0.0                   # Key resistance level (Ice)
    width_pct: float = 0.0             # Range width as % of price
    slope: float = 0.0                 # Structure slope direction


@dataclass
class WyckoffEvents:
    """Detected Wyckoff events at current candle"""
    # Shakeout events
    spring_detected: bool = False
    upthrust_detected: bool = False
    spring_price: float = 0.0
    upthrust_price: float = 0.0

    # Breakout confirmation
    sos_detected: bool = False        # Sign of Strength bar
    sow_detected: bool = False        # Sign of Weakness bar
    sos_idx: int = -1
    sow_idx: int = -1

    # Pullback / Back Up
    back_up_detected: bool = False    # Test after breakout
    back_up_zone: float = 0.0

    # Continuation
    lps_detected: bool = False        # Last Point of Support (within range)
    lpsy_detected: bool = False       # Last Point of Supply (within range)

    # VP
    price_vs_vah: str = "inside"      # above, below, inside
    price_vs_val: str = "inside"      # above, below, inside
    price_vs_poc: str = "near"        # above, below, near


@dataclass
class VpocMigration:
    """VPOC migration tracking for trend health"""
    current_poc: float = 0.0
    previous_poc: float = 0.0
    migration_pct: float = 0.0        # % movement of VPOC
    direction: str = "none"           # up, down, none
    phase: str = "initial"            # initial, migrating, strong_trend, exhausted


def detect_structure_context(
    candles: List[Dict[str, Any]],
    vp: Optional[VolumeProfile],
    lookback: int = 50,
) -> WyckoffStructure:
    """
    Detect Wyckoff structure context from OHLCV candles + Volume Profile.
    Determines if price is in a range (building cause) or trend (effect).
    Uses Volume Profile zones to identify structure boundaries.
    """
    s = WyckoffStructure()
    if len(candles) < lookback or vp is None:
        return s

    recent = candles[-lookback:]
    closes = [_safe_float(c.get("close")) for c in recent]
    highs = [_safe_float(c.get("high")) for c in recent]
    lows = [_safe_float(c.get("low")) for c in recent]
    closes = [c for c in closes if c is not None]
    highs = [h for h in highs if h is not None]
    lows = [l for l in lows if l is not None]

    if len(closes) < 10:
        return s

    # ── Price oscillation — range vs trend ──
    price_range_pct = (max(highs) - min(lows)) / min(lows) * 100 if min(lows) > 0 else 0
    recent_volatility = (max(highs[-20:]) - min(lows[-20:])) / min(lows[-20:]) * 100 if min(lows[-20:]) > 0 else 0

    # Simple linear regression for slope detection
    n = len(closes)
    indices = list(range(n))
    mean_i = n / 2
    mean_c = sum(closes) / n
    numerator = sum((i - mean_i) * (c - mean_c) for i, c in zip(indices, closes))
    denominator = sum((i - mean_i) ** 2 for i in indices)
    slope = numerator / denominator if denominator != 0 else 0
    slope_pct = (slope / mean_c) * 100 if mean_c != 0 else 0

    # R-squared for trend strength
    y_pred = [closes[0] + slope * i for i in range(n)]
    ss_res = sum((closes[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((closes[i] - mean_c) ** 2 for i in range(n))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    # ── Classify Context ──
    # Range: slope near 0 and repeated turns between VAH/VAL
    price_at_vah = (closes[-1] - vp.vah) / vp.vah if vp.vah > 0 else 0
    price_at_val = (closes[-1] - vp.val) / vp.val if vp.val > 0 else 0
    price_at_poc = (closes[-1] - vp.poc) / vp.poc if vp.poc > 0 else 0

    # Count touches at VAH and VAL (within 1%)
    vah_touches = sum(1 for h in highs[-20:] if vp.vah > 0 and abs(h - vp.vah) / vp.vah < 0.01)
    val_touches = sum(1 for l in lows[-20:] if vp.val > 0 and abs(l - vp.val) / vp.val < 0.01)
    total_touches = vah_touches + val_touches

    # Trend scoring
    trend_bias_score = 0.0

    if abs(slope_pct) < 0.05 and total_touches >= 3:
        # Range
        s.context = "range"
        s.top = vp.vah
        s.bottom = vp.val
        s.creek = vp.val    # Creek = support bottom
        s.ice = vp.vah      # Ice = resistance top
        s.width_pct = price_range_pct
        s.slope = slope_pct

        # Determine structure type within range using VP shape
        # Accumulation: VP concentrated at bottom (b-shape)
        # Distribution: VP concentrated at top (P-shape)
        poc_vs_vah = (vp.poc - vp.val) / (vp.vah - vp.val) if (vp.vah - vp.val) > 0 else 0.5

        # Check volume characteristics
        recent_volume = [_safe_float(c.get("volume")) for c in recent[-15:]]
        recent_volume = [v for v in recent_volume if v is not None]
        early_volume = [_safe_float(c.get("volume")) for c in recent[:15]]
        early_volume = [v for v in early_volume if v is not None]
        vol_trend = (sum(recent_volume) / len(recent_volume)) / (sum(early_volume) / len(early_volume)) if early_volume else 1.0

        if poc_vs_vah < 0.35 and vol_trend < 1.0:
            # POC near bottom, volume contracting = accumulation
            s.structure_type = "accumulation"
            s.phase = "B" if vol_trend < 0.85 else "C"
        elif poc_vs_vah > 0.65 and vol_trend < 1.0:
            # POC near top, volume contracting = distribution
            s.structure_type = "distribution"
            s.phase = "B" if vol_trend < 0.85 else "C"
        elif poc_vs_vah < 0.35 and vol_trend > 1.1:
            # Volume spike at bottom = possible Spring (Phase C)
            s.structure_type = "accumulation"
            s.phase = "C"
        elif poc_vs_vah > 0.65 and vol_trend > 1.1:
            s.structure_type = "distribution"
            s.phase = "C"
        else:
            # Balanced / no clear type yet
            s.structure_type = "unknown"
            s.phase = "A"

    elif abs(slope_pct) >= 0.05 and r_squared > 0.5:
        # Trend
        if slope_pct > 0:
            s.context = "trend_up"
            s.structure_type = "markup"  # Phase E
            s.phase = "E"
            s.creek = vp.val  # Support = value area low
            s.slope = slope_pct
            s.bottom = min(lows[-10:]) if lows[-10:] else 0
        else:
            s.context = "trend_down"
            s.structure_type = "markdown"
            s.phase = "E"
            s.ice = vp.vah   # Resistance = value area high
            s.slope = slope_pct
            s.top = max(highs[-10:]) if highs[-10:] else 0
    else:
        s.context = "transition"
        s.structure_type = "unknown"
        s.phase = "unknown"

    return s


def detect_wyckoff_events(
    candles: List[Dict[str, Any]],
    vp: Optional[VolumeProfile],
    structure: WyckoffStructure,
    lookback: int = 15,
) -> WyckoffEvents:
    """
    Detect Wyckoff events at the current candle:
    - Spring / Upthrust (shakeouts at range extremes)
    - SOS / SOW bar (breakout confirmation)
    - Back Up / BUEC (test after breakout)
    - LPS / LPSY (pullbacks within range)
    """
    events = WyckoffEvents()
    if len(candles) < 3 or vp is None:
        return events

    current = candles[-1]
    prev = candles[-2]
    curr_close = _safe_float(current.get("close")) or 0
    curr_high = _safe_float(current.get("high")) or 0
    curr_low = _safe_float(current.get("low")) or 0
    curr_vol = _safe_float(current.get("volume")) or 0
    curr_open = _safe_float(current.get("open")) or 0
    prev_close = _safe_float(prev.get("close")) or 0
    prev_low = _safe_float(prev.get("low")) or 0
    prev_high = _safe_float(prev.get("high")) or 0
    prev_vol = _safe_float(prev.get("volume")) or 0

    # Calculate average volume
    vols = [_safe_float(c.get("volume")) for c in candles[-lookback:]]
    vols = [v for v in vols if v is not None and v > 0]
    avg_vol = sum(vols) / len(vols) if vols else 0

    body = abs(curr_close - curr_open)
    total_range = curr_high - curr_low
    range_pct = total_range / curr_open if curr_open > 0 else 0

    # ── Price position vs Volume Profile zones ──
    if vp.vah > 0:
        if curr_close > vp.vah * 1.005:
            events.price_vs_vah = "above"
        elif curr_close < vp.vah * 0.995:
            events.price_vs_vah = "inside"
        else:
            events.price_vs_vah = "near"

    if vp.val > 0:
        if curr_close < vp.val * 0.995:
            events.price_vs_val = "below"
        elif curr_close > vp.val * 1.005:
            events.price_vs_val = "inside"
        else:
            events.price_vs_val = "near"

    if vp.poc > 0:
        poc_dist = abs(curr_close - vp.poc) / vp.poc if vp.poc > 0 else 1
        if curr_close > vp.poc:
            events.price_vs_poc = "above" if poc_dist > 0.01 else "near"
        else:
            events.price_vs_poc = "below" if poc_dist > 0.01 else "near"

    # ── SOS (Sign of Strength) Detection ──
    # Wide range bullish candle with high volume, close upper third
    if (range_pct > 0.01 and curr_close > curr_open and
        body / total_range > 0.5 if total_range > 0 else False and
        curr_vol > avg_vol * 1.5):
        events.sos_detected = True
        events.sos_idx = len(candles) - 1

    # ── SOW (Sign of Weakness) Detection ──
    if (range_pct > 0.01 and curr_close < curr_open and
        body / total_range > 0.5 if total_range > 0 else False and
        curr_vol > avg_vol * 1.5):
        events.sow_detected = True
        events.sow_idx = len(candles) - 1

    # ── Spring Detection ──
    # Price dips below VAL / structure bottom then closes back above
    if structure.bottom > 0:
        # Price touched below support
        touched_below = curr_low < structure.bottom * 0.995
        closed_above = curr_close > structure.bottom * 0.995
        if touched_below and closed_above:
            events.spring_detected = True
            events.spring_price = structure.bottom

    # ── Upthrust Detection ──
    if structure.top > 0:
        touched_above = curr_high > structure.top * 1.005
        closed_below = curr_close < structure.top * 1.005
        if touched_above and closed_below:
            events.upthrust_detected = True
            events.upthrust_price = structure.top

    # ── Back Up / BUEC Detection (test after breakout) ──
    if structure.context in ("trend_up", "trend_down") and len(candles) > 5:
        # Check if price pulled back to broken structure level
        recent_highs = [_safe_float(c.get("high")) for c in candles[-5:-1]]
        recent_highs = [h for h in recent_highs if h is not None]
        recent_lows = [_safe_float(c.get("low")) for c in candles[-5:-1]]
        recent_lows = [l for l in recent_lows if l is not None]

        if structure.context == "trend_up" and recent_lows:
            # Pullback to Creek / VAL for Back Up
            pullback_depth = min(recent_lows)
            if vp.val > 0 and abs(pullback_depth - vp.val) / vp.val < 0.01:
                events.back_up_detected = True
                events.back_up_zone = vp.val
                events.lps_detected = True
        elif structure.context == "trend_down" and recent_highs:
            pullback_height = max(recent_highs)
            if vp.vah > 0 and abs(pullback_height - vp.vah) / vp.vah < 0.01:
                events.back_up_detected = True
                events.back_up_zone = vp.vah
                events.lpsy_detected = True

    return events


def track_vpoc_migration(
    candles: List[Dict[str, Any]],
    structure: WyckoffStructure,
    half_lookback: int = 50,
) -> VpocMigration:
    """
    Track VPOC migration to assess trend health.
    Splits candles into two halves: early and recent.
    If VPOC migrates with price = healthy trend.
    If VPOC stays inside range after breakout = false break warning.
    """
    mig = VpocMigration()
    if len(candles) < half_lookback * 2:
        return mig

    early_candles = candles[:half_lookback]
    recent_candles = candles[-half_lookback:]

    def _calc_poc(candles_slice):
        prices = defaultdict(float)
        for c in candles_slice:
            h = _safe_float(c.get("high"))
            l = _safe_float(c.get("low"))
            v = _safe_float(c.get("volume"))
            if any(x is None for x in [h, l, v]) or v == 0:
                continue
            mid = (h + l) / 2
            # Distribute volume across price range
            for mult in [0.25, 0.5, 0.75]:
                price_level = l + (h - l) * mult
                prices[price_level] += v / 4
        if not prices:
            return 0.0
        return max(prices, key=prices.get)

    early_poc = _calc_poc(early_candles)
    recent_poc = _calc_poc(recent_candles)

    mig.current_poc = recent_poc
    mig.previous_poc = early_poc

    if early_poc > 0 and recent_poc > 0:
        mig.migration_pct = (recent_poc - early_poc) / early_poc * 100

        if abs(mig.migration_pct) < 0.5:
            mig.direction = "none"
            # VPOC stuck = no acceptance = range may continue
            if structure.context == "range":
                mig.phase = "range_steady"
            else:
                mig.phase = "trend_unconfirmed"
        elif mig.migration_pct > 0:
            mig.direction = "up"
            if mig.migration_pct > 3.0:
                mig.phase = "strong_trend"
            elif mig.migration_pct > 1.0:
                mig.phase = "migrating"
            else:
                mig.phase = "initial"
        else:
            mig.direction = "down"
            if abs(mig.migration_pct) > 3.0:
                mig.phase = "strong_trend"
            elif abs(mig.migration_pct) > 1.0:
                mig.phase = "migrating"
            else:
                mig.phase = "initial"

    return mig


def score_wyckoff(
    structure: WyckoffStructure,
    events: WyckoffEvents,
    migration: VpocMigration,
) -> Tuple[float, float]:
    """
    Score Wyckoff direction and certainty.
    Returns (wyckoff_structure_score, wyckoff_vpoc_score)
    Both on scale -1 to +1 (positive = long, negative = short)

    Structure score: context + events
    VPOC score: trend health via migration
    """
    struct_score = 0.0
    vpoc_score = 0.0

    # ── Structure Context Score (range -1 to +1) ──
    if structure.structure_type == "accumulation":
        # Accumulation = eventual bullish breakout
        if structure.phase in ("C", "D"):
            struct_score += 0.7  # Near breakout
        elif structure.phase == "B":
            struct_score += 0.3  # Building cause
        else:
            struct_score += 0.1
    elif structure.structure_type == "distribution":
        if structure.phase in ("C", "D"):
            struct_score -= 0.7
        elif structure.phase == "B":
            struct_score -= 0.3
        else:
            struct_score -= 0.1
    elif structure.context == "trend_up":
        struct_score += 0.5  # Markup
    elif structure.context == "trend_down":
        struct_score -= 0.5  # Markdown

    # ── Wyckoff Events Score (cumulative, capped ±0.5) ──
    event_bias = 0.0
    if events.spring_detected:
        event_bias += 0.5    # Strong bullish shakeout
    if events.sos_detected:
        event_bias += 0.4    # Sign of Strength
    if events.lps_detected:
        event_bias += 0.3    # Last Point of Support
    if events.back_up_detected and structure.context == "trend_up":
        event_bias += 0.3    # Valid back up in uptrend

    if events.upthrust_detected:
        event_bias -= 0.5
    if events.sow_detected:
        event_bias -= 0.4
    if events.lpsy_detected:
        event_bias -= 0.3
    if events.back_up_detected and structure.context == "trend_down":
        event_bias -= 0.3

    # Clamp event bias
    event_bias = max(-0.5, min(0.5, event_bias))

    # Combine: structure provides baseline, events provide amplification
    # In a range, events matter more. In a trend, structure matters more.
    if structure.context == "range":
        struct_score = struct_score * 0.4 + event_bias * 0.6
    else:
        struct_score = struct_score * 0.6 + event_bias * 0.4

    struct_score = max(-1.0, min(1.0, struct_score))

    # ── VPOC Migration Score ──
    if migration.direction == "up":
        if migration.phase == "strong_trend":
            vpoc_score = 0.8
        elif migration.phase == "migrating":
            vpoc_score = 0.5
        elif migration.phase == "initial":
            vpoc_score = 0.3
    elif migration.direction == "down":
        if migration.phase == "strong_trend":
            vpoc_score = -0.8
        elif migration.phase == "migrating":
            vpoc_score = -0.5
        elif migration.phase == "initial":
            vpoc_score = -0.3
    else:
        # VPOC stuck — no acceptance yet
        if structure.context == "range":
            vpoc_score = 0.0  # Neutral, range expected
        elif structure.structure_type == "accumulation":
            vpoc_score = -0.2  # Pending breakout
        elif structure.structure_type == "distribution":
            vpoc_score = 0.2   # Pending breakdown
        else:
            vpoc_score = 0.0

    return (struct_score, vpoc_score)


# ═══════════════════════════════════════════════
# Paper Trading Engine
# ═══════════════════════════════════════════════

@dataclass
class PaperTrade:
    trade_id: int
    coin: str
    direction: str
    entry_price: float
    stop_loss: float
    tp1: float
    tp2: float
    position_size: float
    risk_amount: float
    entry_time: str
    entry_candle_idx: int
    confluence_score: float
    signal_breakdown: str
    
    status: str = "open"
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    exit_candle_idx: Optional[int] = None
    pnl: float = 0.0
    pnl_r: float = 0.0
    partial_closed: bool = False
    notes: str = ""


@dataclass
class PerformanceMetrics:
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    expectancy_r: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    avg_win_r: float = 0.0
    avg_loss_r: float = 0.0
    sharpe_ratio: float = 0.0
    total_r: float = 0.0
    avg_confluence_score: float = 0.0


class POCPaperTraderV2:
    """V2 Paper trading engine with multi-factor confluence"""
    
    def __init__(self, coin: str, config: POCConfig):
        self.coin = coin
        self.config = config
        self.equity = config.starting_capital
        self.peak_equity = config.starting_capital
        self.trades: List[PaperTrade] = []
        self.open_trades: List[PaperTrade] = []
        self.trade_counter = 0
        self.equity_curve: List[float] = [config.starting_capital]
        self.funding_rate = 0.0
        self.funding_sentiment = "neutral"
    
    def _fetch_candles(self, interval: str, hours: float) -> List[Dict[str, Any]]:
        end_ms = int(time.time() * 1000)
        start_ms = _hours_ago_ms(hours, end_ms)
        
        payload = {
            "type": "candleSnapshot",
            "req": {
                "coin": self.coin,
                "interval": interval,
                "startTime": start_ms,
                "endTime": end_ms,
            },
        }
        
        raw = _post_info(payload)
        candles = _normalize_candles(raw)
        
        if not candles:
            raise ValueError(f"No candles returned for {self.coin}")
        
        return candles
    
    def _calculate_position_size(self, entry: float, stop: float) -> Tuple[float, float]:
        risk_dollars = self.equity * self.config.risk_per_trade
        stop_distance = abs(entry - stop)
        if stop_distance == 0:
            return 0.0, 0.0
        return risk_dollars / stop_distance, risk_dollars
    
    def _build_snapshot(
        self,
        candles: List[Dict[str, Any]],
        idx: int,
        vp: VolumeProfile,
        trend: str,
        trend_strength: float,
    ) -> IndicatorSnapshot:
        """Build complete indicator snapshot at candle index"""
        candle = candles[idx]
        close = _safe_float(candle.get("close")) or 0.0
        high = _safe_float(candle.get("high")) or 0.0
        low = _safe_float(candle.get("low")) or 0.0
        volume = _safe_float(candle.get("volume")) or 0.0
        
        # VWAP
        vwap_result = calculate_vwap(candles[:idx+1], lookback=20)
        if vwap_result:
            vwap, vwap_upper, vwap_lower = vwap_result
            price_vs_vwap = (close - vwap) / vwap if vwap > 0 else 0
        else:
            vwap = close
            vwap_upper = close
            vwap_lower = close
            price_vs_vwap = 0
        
        # OBV
        obv_result = calculate_obv(candles[:idx+1], sma_period=20)
        if obv_result:
            obv, obv_sma, obv_trend = obv_result
        else:
            obv = 0
            obv_sma = 0
            obv_trend = "neutral"
        
        # CMF
        cmf = calculate_cmf(candles[:idx+1], period=20) or 0.0
        
        # MFI
        mfi = calculate_mfi(candles[:idx+1], period=14) or 50.0
        
        # Volume ratio
        lookback = min(20, idx)
        if lookback > 0:
            avg_vol = sum(
                _safe_float(candles[i].get("volume")) or 0
                for i in range(idx - lookback, idx)
            ) / lookback
            volume_ratio = volume / avg_vol if avg_vol > 0 else 1.0
        else:
            volume_ratio = 1.0
        
        # POC distance
        poc_distance_pct = abs(close - vp.poc) / vp.poc if vp.poc > 0 else 0
        
        return IndicatorSnapshot(
            close=close,
            high=high,
            low=low,
            volume=volume,
            poc=vp.poc,
            vah=vp.vah,
            val=vp.val,
            vp_quality=vp.concentration,
            poc_distance_pct=poc_distance_pct,
            vwap=vwap,
            vwap_upper=vwap_upper,
            vwap_lower=vwap_lower,
            price_vs_vwap=price_vs_vwap,
            obv=obv,
            obv_sma=obv_sma,
            obv_trend=obv_trend,
            cmf=cmf,
            cmf_trend="bullish" if cmf > 0.05 else "bearish" if cmf < -0.05 else "neutral",
            mfi=mfi,
            mfi_zone="overbought" if mfi > 80 else "oversold" if mfi < 20 else "neutral",
            trend=trend,
            trend_strength=trend_strength,
            funding_rate=self.funding_rate,
            funding_sentiment=self.funding_sentiment,
            volume_ratio=volume_ratio,
            momentum=(candles[idx].get("close", 0) - candles[max(0,idx-10)].get("close", 0)) / max(candles[max(0,idx-10)].get("close", 0.01), 0.01) * 100 if idx >= 10 else 0.0,
        )
    
    def _check_entry_signal(
        self,
        candles: List[Dict[str, Any]],
        idx: int,
        snapshot: IndicatorSnapshot,
        confluence: ConfluenceScore,
    ) -> Optional[Dict[str, Any]]:
        """Check for POC retest entry with confluence"""
        if idx < 1:
            return None
        
        candle = candles[idx]
        prev_candle = candles[idx - 1]
        
        close = snapshot.close
        high = snapshot.high
        low = snapshot.low
        
        # Must be near POC
        poc_touched = (
            (low <= snapshot.poc * (1 + self.config.poc_tolerance_pct)) and
            (high >= snapshot.poc * (1 - self.config.poc_tolerance_pct))
        )
        
        if not poc_touched:
            return None
        
        # Check minimum distance between retests
        if self.open_trades:
            last_trade = max(self.open_trades, key=lambda t: t.entry_candle_idx)
            if idx - last_trade.entry_candle_idx < self.config.min_candles_between_retests:
                return None
        
        # Direction from confluence
        direction = confluence.direction
        if direction == "none":
            return None
        
        # Trend alignment filter
        if self.config.require_trend_alignment:
            if snapshot.trend == "bullish" and direction == "short":
                return None
            elif snapshot.trend == "bearish" and direction == "long":
                return None
        
        # Volume filter
        if snapshot.volume_ratio < self.config.risk_per_trade * 80:  # Relaxed
            pass  # Don't block on volume alone in V2
        
        # Candle pattern
        candle_signal = get_candle_signal(candle, prev_candle)
        
        # Calculate stop and target
        if direction == "long":
            stop = min(low, snapshot.val) * (1 - self.config.stop_buffer_pct)
            risk = close - stop
            target1 = close + risk * self.config.tp1_rr
            target2 = close + risk * self.config.tp2_rr
            target1 = max(target1, snapshot.vah)
        else:
            stop = max(high, snapshot.vah) * (1 + self.config.stop_buffer_pct)
            risk = stop - close
            target1 = close - risk * self.config.tp1_rr
            target2 = close - risk * self.config.tp2_rr
            target1 = min(target1, snapshot.val)
        
        # Check R:R
        reward = abs(target1 - close)
        if risk == 0:
            return None
        
        rr_ratio = reward / risk
        if rr_ratio < self.config.min_rr_ratio:
            return None
        
        return {
            "direction": direction,
            "entry": close,
            "stop": stop,
            "tp1": target1,
            "tp2": target2,
            "risk_per_unit": risk,
            "rr_ratio": rr_ratio,
            "candle_signal": candle_signal or "none",
            "confluence_score": confluence.total,
            "signal_breakdown": (
                f"T:{confluence.trend_score:+.1f} "
                f"V:{confluence.vwap_score:+.1f} "
                f"O:{confluence.obv_score:+.1f} "
                f"C:{confluence.cmf_score:+.1f} "
                f"M:{confluence.mfi_score:+.1f} "
                f"F:{confluence.funding_score:+.1f} "
                f"P:{confluence.vp_quality_score:+.1f} "
                f"K:{confluence.candle_score:+.1f}"
            ),
        }
    
    def _open_trade(self, signal: Dict[str, Any], candle: Dict[str, Any], candle_idx: int) -> PaperTrade:
        self.trade_counter += 1
        
        position_size, risk_amount = self._calculate_position_size(
            signal["entry"], signal["stop"]
        )
        
        trade = PaperTrade(
            trade_id=self.trade_counter,
            coin=self.coin,
            direction=signal["direction"],
            entry_price=signal["entry"],
            stop_loss=signal["stop"],
            tp1=signal["tp1"],
            tp2=signal["tp2"],
            position_size=position_size,
            risk_amount=risk_amount,
            entry_time=_format_timestamp_ms(candle.get("time")),
            entry_candle_idx=candle_idx,
            confluence_score=signal["confluence_score"],
            signal_breakdown=signal["signal_breakdown"],
            notes=f"R:R={signal['rr_ratio']:.2f} | Score={signal['confluence_score']:+.1f}",
        )
        
        self.open_trades.append(trade)
        self.trades.append(trade)
        return trade
    
    def _check_exits(self, candles: List[Dict[str, Any]], idx: int) -> List[str]:
        candle = candles[idx]
        high = _safe_float(candle.get("high"))
        low = _safe_float(candle.get("low"))
        
        if high is None or low is None:
            return []
        
        events = []
        closed_trades = []
        
        for trade in self.open_trades:
            if trade.status == "tp1_hit":
                if trade.direction == "long" and high >= trade.tp2:
                    remaining = trade.position_size * 0.5
                    pnl = (trade.tp2 - trade.entry_price) * remaining
                    trade.pnl += pnl
                    trade.pnl_r = trade.pnl / trade.risk_amount
                    trade.status = "closed"
                    trade.exit_price = trade.tp2
                    trade.exit_time = _format_timestamp_ms(candle.get("time"))
                    trade.exit_candle_idx = idx
                    self.equity += pnl
                    events.append(f"TP2: {trade.direction.upper()} @ {trade.tp2:.2f} | {trade.pnl_r:+.2f}R | ${pnl:+.2f}")
                    closed_trades.append(trade)
                
                elif trade.direction == "short" and low <= trade.tp2:
                    remaining = trade.position_size * 0.5
                    pnl = (trade.entry_price - trade.tp2) * remaining
                    trade.pnl += pnl
                    trade.pnl_r = trade.pnl / trade.risk_amount
                    trade.status = "closed"
                    trade.exit_price = trade.tp2
                    trade.exit_time = _format_timestamp_ms(candle.get("time"))
                    trade.exit_candle_idx = idx
                    self.equity += pnl
                    events.append(f"TP2: {trade.direction.upper()} @ {trade.tp2:.2f} | {trade.pnl_r:+.2f}R | ${pnl:+.2f}")
                    closed_trades.append(trade)
                continue
            
            if trade.direction == "long":
                if low <= trade.stop_loss:
                    pnl = (trade.stop_loss - trade.entry_price) * trade.position_size
                    trade.pnl = pnl
                    trade.pnl_r = -1.0
                    trade.status = "stopped"
                    trade.exit_price = trade.stop_loss
                    trade.exit_time = _format_timestamp_ms(candle.get("time"))
                    trade.exit_candle_idx = idx
                    self.equity += pnl
                    events.append(f"STOP: {trade.direction.upper()} @ {trade.stop_loss:.2f} | -1.0R | ${pnl:.2f}")
                    closed_trades.append(trade)
                elif high >= trade.tp1 and not trade.partial_closed:
                    pnl = (trade.tp1 - trade.entry_price) * (trade.position_size * 0.5)
                    trade.pnl += pnl
                    trade.partial_closed = True
                    trade.status = "tp1_hit"
                    events.append(f"TP1: {trade.direction.upper()} @ {trade.tp1:.2f} | +${pnl:.2f}")
            else:
                if high >= trade.stop_loss:
                    pnl = (trade.entry_price - trade.stop_loss) * trade.position_size
                    trade.pnl = pnl
                    trade.pnl_r = -1.0
                    trade.status = "stopped"
                    trade.exit_price = trade.stop_loss
                    trade.exit_time = _format_timestamp_ms(candle.get("time"))
                    trade.exit_candle_idx = idx
                    self.equity += pnl
                    events.append(f"STOP: {trade.direction.upper()} @ {trade.stop_loss:.2f} | -1.0R | ${pnl:.2f}")
                    closed_trades.append(trade)
                elif low <= trade.tp1 and not trade.partial_closed:
                    pnl = (trade.entry_price - trade.tp1) * (trade.position_size * 0.5)
                    trade.pnl += pnl
                    trade.partial_closed = True
                    trade.status = "tp1_hit"
                    events.append(f"TP1: {trade.direction.upper()} @ {trade.tp1:.2f} | +${pnl:.2f}")
        
        for trade in closed_trades:
            if trade in self.open_trades:
                self.open_trades.remove(trade)
        
        return events
    
    def run(self, interval: str = "1h", hours: float = 168) -> Dict[str, Any]:
        print(f"\n{'='*70}")
        print(f"  POC Paper Trader V2 — Multi-Factor Confluence")
        print(f"  Coin: {self.coin} | Interval: {interval} | Lookback: {hours}h")
        print(f"  Capital: ${self.config.starting_capital:,.2f} | Risk: {self.config.risk_per_trade*100:.1f}%")
        print(f"  Min Confluence Score: {self.config.min_confluence_score}")
        print(f"{'='*70}\n")
        
        # Fetch data
        print("Fetching candle data...")
        candles = self._fetch_candles(interval, hours)
        print(f"Loaded {len(candles)} candles")
        
        # Fetch funding rate
        print("Fetching funding rate...")
        self.funding_rate, self.funding_sentiment = fetch_funding_sentiment(self.coin, hours)
        print(f"Avg funding: {self.funding_rate*100:.4f}% | Sentiment: {self.funding_sentiment}")
        
        print(f"\nRunning simulation...\n")
        
        all_events = []
        vp_lookback = self.config.vp_lookback
        
        for idx in range(vp_lookback, len(candles)):
            # Volume Profile
            vp_slice = candles[max(0, idx - vp_lookback):idx + 1]
            vp = calculate_volume_profile(vp_slice, self.config.price_bins, self.config.value_area_pct)
            if vp is None:
                continue
            
            # Trend
            trend, trend_strength = detect_trend(candles[:idx + 1])
            
            # Build snapshot
            snapshot = self._build_snapshot(candles, idx, vp, trend, trend_strength)
            
            # Exit checks
            exit_events = self._check_exits(candles, idx)
            all_events.extend(exit_events)
            
            # Entry checks
            if len(self.open_trades) < self.config.max_open_trades:
                # Candle pattern
                prev_candle = candles[idx - 1] if idx > 0 else None
                candle_signal = get_candle_signal(candles[idx], prev_candle)
                
                # Confluence score
                confluence = calculate_confluence(snapshot, candle_signal, self.config)
                
                # Check minimum score
                if abs(confluence.total) >= self.config.min_confluence_score:
                    signal = self._check_entry_signal(candles, idx, snapshot, confluence)
                    
                    if signal:
                        trade = self._open_trade(signal, candles[idx], idx)
                        entry_event = (
                            f"ENTRY: {trade.direction.upper()} @ {trade.entry_price:.2f} | "
                            f"Stop: {trade.stop_loss:.2f} | TP1: {trade.tp1:.2f} | "
                            f"Score: {signal['confluence_score']:+.1f} | {signal['signal_breakdown']}"
                        )
                        all_events.append(entry_event)
                        
                        if self.config.verbose:
                            print(f"  #{trade.trade_id} {trade.direction.upper()} @ {trade.entry_price:.2f} "
                                  f"| Score: {signal['confluence_score']:+.1f}")
            
            self.equity_curve.append(self.equity)
            self.peak_equity = max(self.peak_equity, self.equity)
        
        # Force close remaining
        for trade in list(self.open_trades):
            last_close = _safe_float(candles[-1].get("close"))
            if last_close:
                if trade.direction == "long":
                    pnl = (last_close - trade.entry_price) * trade.position_size
                else:
                    pnl = (trade.entry_price - last_close) * trade.position_size
                
                trade.pnl += pnl
                trade.pnl_r = trade.pnl / trade.risk_amount
                trade.status = "closed"
                trade.exit_price = last_close
                trade.exit_time = _format_timestamp_ms(candles[-1].get("time"))
                trade.exit_candle_idx = len(candles) - 1
                trade.notes += " | Force-closed"
                self.equity += pnl
        
        self.open_trades.clear()
        
        metrics = self._calculate_metrics()
        
        return {
            "coin": self.coin,
            "interval": interval,
            "hours": hours,
            "candles": len(candles),
            "funding_rate": self.funding_rate,
            "funding_sentiment": self.funding_sentiment,
            "config": asdict(self.config),
            "metrics": asdict(metrics),
            "trades": [asdict(t) for t in self.trades],
            "equity_curve": self.equity_curve,
            "events": all_events,
        }
    
    def _calculate_metrics(self) -> PerformanceMetrics:
        if not self.trades:
            return PerformanceMetrics()
        
        m = PerformanceMetrics()
        m.total_trades = len(self.trades)
        
        wins = [t for t in self.trades if t.pnl > 0]
        losses = [t for t in self.trades if t.pnl < 0]
        
        m.wins = len(wins)
        m.losses = len(losses)
        m.win_rate = (m.wins / m.total_trades * 100) if m.total_trades > 0 else 0
        
        m.total_pnl = sum(t.pnl for t in self.trades)
        m.avg_win = sum(t.pnl for t in wins) / len(wins) if wins else 0
        m.avg_loss = sum(t.pnl for t in losses) / len(losses) if losses else 0
        
        r_values = [t.pnl_r for t in self.trades if t.pnl_r != 0]
        m.total_r = sum(r_values)
        m.expectancy_r = sum(r_values) / len(r_values) if r_values else 0
        m.avg_win_r = sum(t.pnl_r for t in wins) / len(wins) if wins else 0
        m.avg_loss_r = sum(t.pnl_r for t in losses) / len(losses) if losses else 0
        
        gross_profits = sum(t.pnl for t in wins)
        gross_losses = abs(sum(t.pnl for t in losses))
        m.profit_factor = gross_profits / gross_losses if gross_losses > 0 else float('inf')
        
        m.best_trade = max(t.pnl_r for t in self.trades)
        m.worst_trade = min(t.pnl_r for t in self.trades)
        
        if self.equity_curve:
            peak = self.equity_curve[0]
            max_dd = 0
            max_dd_pct = 0
            for eq in self.equity_curve:
                peak = max(peak, eq)
                dd = peak - eq
                dd_pct = dd / peak if peak > 0 else 0
                max_dd = max(max_dd, dd)
                max_dd_pct = max(max_dd_pct, dd_pct)
            m.max_drawdown = max_dd
            m.max_drawdown_pct = max_dd_pct * 100
        
        if len(r_values) > 1:
            mean_r = sum(r_values) / len(r_values)
            std_r = math.sqrt(sum((r - mean_r) ** 2 for r in r_values) / (len(r_values) - 1))
            trades_per_year = min(len(r_values), 365)
            m.sharpe_ratio = (mean_r / std_r) * math.sqrt(trades_per_year) if std_r > 0 else 0
        
        # Average confluence score
        scores = [t.confluence_score for t in self.trades]
        m.avg_confluence_score = sum(scores) / len(scores) if scores else 0
        
        return m


# ═══════════════════════════════════════════════
# Rendering
# ═══════════════════════════════════════════════

def render_results(data: Dict[str, Any]) -> str:
    m = data["metrics"]
    cfg = data["config"]
    
    lines = [
        f"\n{'='*70}",
        f"  PAPER TRADING RESULTS V2 — {data['coin']}",
        f"{'='*70}",
        f"",
        f"  Period: {data['candles']} candles ({data['interval']}, {data['hours']}h)",
        f"  Funding Rate: {data['funding_rate']*100:.4f}% ({data['funding_sentiment']})",
        f"  Starting Capital: ${cfg['starting_capital']:,.2f}",
        f"  Final Equity: ${cfg['starting_capital'] + m['total_pnl']:,.2f}",
        f"",
        f"  {'─'*66}",
        f"  PERFORMANCE SUMMARY",
        f"  {'─'*66}",
        f"  Total Trades:        {m['total_trades']}",
        f"  Wins / Losses:       {m['wins']} / {m['losses']}",
        f"  Win Rate:            {m['win_rate']:.1f}%",
        f"",
        f"  Total PnL:           ${m['total_pnl']:+,.2f}",
        f"  Total R:             {m['total_r']:+.2f}R",
        f"  Expectancy:          {m['expectancy_r']:+.3f}R per trade",
        f"  Avg Confluence:      {m['avg_confluence_score']:+.1f}",
        f"",
        f"  Avg Win:             ${m['avg_win']:+,.2f} ({m['avg_win_r']:+.2f}R)",
        f"  Avg Loss:            ${m['avg_loss']:+,.2f} ({m['avg_loss_r']:+.2f}R)",
        f"  Profit Factor:       {m['profit_factor']:.2f}",
        f"",
        f"  Best Trade:          {m['best_trade']:+.2f}R",
        f"  Worst Trade:         {m['worst_trade']:+.2f}R",
        f"",
        f"  Max Drawdown:        ${m['max_drawdown']:,.2f} ({m['max_drawdown_pct']:.1f}%)",
        f"  Sharpe Ratio:        {m['sharpe_ratio']:.2f}",
    ]
    
    if data["trades"]:
        lines.extend([
            f"",
            f"  {'─'*66}",
            f"  TRADE LOG",
            f"  {'─'*66}",
        ])
        
        for t in data["trades"][:25]:
            icon = "✓" if t["pnl"] > 0 else "✗" if t["pnl"] < 0 else "="
            score_str = f"{t['confluence_score']:+.1f}"
            lines.append(
                f"  {icon} #{t['trade_id']:3d} {t['direction']:5s} @ {t['entry_price']:>10,.2f} → "
                f"{t['exit_price']:>10,.2f} | {t['pnl_r']:+.2f}R | Score:{score_str}"
            )
    
    if data["events"]:
        lines.extend([
            f"",
            f"  {'─'*66}",
            f"  KEY EVENTS (last 25)",
            f"  {'─'*66}",
        ])
        for e in data["events"][-25:]:
            lines.append(f"  • {e}")
    
    lines.append(f"\n{'='*70}\n")
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="POC Paper Trader V2 — Multi-Factor Confluence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("coin", help="Coin to trade (e.g., BTC, ETH, SOL)")
    parser.add_argument("--interval", default="1h", help="Candle interval (default: 1h)")
    parser.add_argument("--hours", type=float, default=168, help="Lookback in hours (default: 168)")
    parser.add_argument("--risk", type=float, default=0.01, help="Risk per trade (default: 0.01)")
    parser.add_argument("--capital", type=float, default=10000, help="Starting capital (default: 10000)")
    parser.add_argument("--vp-lookback", type=int, default=100, help="Volume Profile lookback (default: 100)")
    parser.add_argument("--min-score", type=int, default=5, help="Min confluence score to enter (default: 5)")
    parser.add_argument("--min-rr", type=float, default=1.5, help="Minimum R:R ratio (default: 1.5)")
    parser.add_argument("--verbose", action="store_true", help="Print signals as they occur")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    config = POCConfig(
        risk_per_trade=args.risk,
        starting_capital=args.capital,
        vp_lookback=args.vp_lookback,
        min_confluence_score=args.min_score,
        min_rr_ratio=args.min_rr,
        verbose=args.verbose,
    )
    
    trader = POCPaperTraderV2(args.coin.upper(), config)
    results = trader.run(args.interval, args.hours)
    
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(render_results(results))


if __name__ == "__main__":
    main()
