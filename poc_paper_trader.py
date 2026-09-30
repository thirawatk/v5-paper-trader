#!/usr/bin/env python3
"""
POC (Point of Control) Paper Trading Bot for Hyperliquid
=========================================================
Calculates Volume Profile from OHLCV candles, identifies POC,
detects POC retest setups, and simulates paper trades.

Usage:
  python3 poc_paper_trader.py BTC --interval 1h --hours 168
  python3 poc_paper_trader.py ETH --interval 15m --hours 72 --risk 0.01
  python3 poc_paper_trader.py BTC --interval 1h --hours 168 --json

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
    _post_info, _normalize_candles, _hours_ago_ms, _safe_float, _compact_number,
    _format_price, _format_percent, _format_fraction_percent, _format_timestamp_ms
)


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

@dataclass
class POCConfig:
    """POC Paper Trader Configuration"""
    # Volume Profile
    vp_lookback: int = 100          # Number of candles for Volume Profile calculation
    price_bins: int = 100           # Number of price levels in Volume Profile
    value_area_pct: float = 0.70    # % of volume for Value Area (70% standard)
    
    # Entry Logic
    poc_tolerance_pct: float = 0.003  # Price must be within 0.3% of POC to count as retest
    min_candles_between_retests: int = 5  # Min candles between retests (avoid whipsaws)
    require_htf_trend: bool = True   # Require trend alignment for entries
    
    # Confirmation
    require_volume_spike: bool = True  # Volume on retest candle > avg
    volume_spike_mult: float = 0.8     # Volume must be > 0.8x avg (relaxed for paper trading)
    require_rejection_candle: bool = False  # Require rejection candle at POC (pin bar, engulfing)
    
    # Risk Management
    risk_per_trade: float = 0.01    # 1% of equity per trade
    min_rr_ratio: float = 1.5       # Minimum R:R ratio to enter
    max_open_trades: int = 3        # Maximum simultaneous positions
    stop_buffer_pct: float = 0.002  # Stop loss buffer beyond zone (0.2%)
    
    # Take Profit
    tp1_rr: float = 1.5             # Take 50% at 1.5R
    tp2_rr: float = 3.0             # Take remaining at 3R or trail
    
    # Performance
    starting_capital: float = 10000.0


# ─────────────────────────────────────────────
# Volume Profile Calculator
# ─────────────────────────────────────────────

@dataclass
class VolumeLevel:
    """Single price level in the Volume Profile"""
    price: float
    volume: float
    pct_of_total: float = 0.0


@dataclass
class VolumeProfile:
    """Complete Volume Profile analysis"""
    poc: float                      # Point of Control (highest volume price)
    vah: float                      # Value Area High
    val: float                      # Value Area Low
    hvn_threshold: float            # High Volume Node threshold
    lvn_threshold: float            # Low Volume Node threshold
    levels: List[VolumeLevel] = field(default_factory=list)
    total_volume: float = 0.0
    poc_volume: float = 0.0
    value_area_volume: float = 0.0


def calculate_volume_profile(
    candles: List[Dict[str, Any]],
    num_bins: int = 100,
    value_area_pct: float = 0.70
) -> VolumeProfile:
    """
    Calculate Volume Profile from OHLCV candles.
    
    Distributes each candle's volume across its price range,
    then finds the POC and Value Area.
    """
    if not candles:
        raise ValueError("No candles provided for Volume Profile calculation")
    
    # Find price range
    all_highs = [_safe_float(c.get("high")) for c in candles]
    all_lows = [_safe_float(c.get("low")) for c in candles]
    clean_highs = [h for h in all_highs if h is not None]
    clean_lows = [l for l in all_lows if l is not None]
    
    if not clean_highs or not clean_lows:
        raise ValueError("Invalid candle data — no valid high/low prices")
    
    price_max = max(clean_highs)
    price_min = min(clean_lows)
    
    if price_max == price_min:
        raise ValueError("Price range is zero — cannot build Volume Profile")
    
    # Create price bins
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
        
        # Distribute volume across the candle's price range
        candle_low = min(o, h, l, c)
        candle_high = max(o, h, l, c)
        
        if candle_high == candle_low:
            # Doji — all volume at close
            bin_idx = int((c - price_min) / bin_size)
            bin_idx = max(0, min(bin_idx, num_bins - 1))
            bin_price = price_min + (bin_idx + 0.5) * bin_size
            volume_at_price[bin_price] += v
        else:
            # Distribute volume proportionally across bins in range
            low_bin = int((candle_low - price_min) / bin_size)
            high_bin = int((candle_high - price_min) / bin_size)
            low_bin = max(0, min(low_bin, num_bins - 1))
            high_bin = max(0, min(high_bin, num_bins - 1))
            
            num_affected_bins = high_bin - low_bin + 1
            volume_per_bin = v / num_affected_bins
            
            for b in range(low_bin, high_bin + 1):
                bin_price = price_min + (b + 0.5) * bin_size
                volume_at_price[bin_price] += volume_per_bin
    
    # Build sorted levels
    levels = []
    total_volume = 0.0
    for price, vol in sorted(volume_at_price.items()):
        total_volume += vol
        levels.append(VolumeLevel(price=price, volume=vol))
    
    if total_volume == 0:
        raise ValueError("Total volume is zero — cannot build Volume Profile")
    
    # Calculate percentages
    for level in levels:
        level.pct_of_total = level.volume / total_volume
    
    # Find POC (highest volume level)
    poc_level = max(levels, key=lambda x: x.volume)
    poc = poc_level.price
    poc_volume = poc_level.volume
    
    # Calculate Value Area (70% of volume centered on POC)
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
    value_area_volume = cumulative_volume
    
    # Calculate HVN/LVN thresholds (1 std dev from mean)
    volumes = [l.volume for l in levels]
    mean_vol = sum(volumes) / len(volumes)
    std_vol = math.sqrt(sum((v - mean_vol) ** 2 for v in volumes) / len(volumes))
    
    hvn_threshold = mean_vol + std_vol
    lvn_threshold = mean_vol - std_vol
    
    return VolumeProfile(
        poc=poc,
        vah=vah,
        val=val,
        hvn_threshold=hvn_threshold,
        lvn_threshold=lvn_threshold,
        levels=levels,
        total_volume=total_volume,
        poc_volume=poc_volume,
        value_area_volume=value_area_volume,
    )


# ─────────────────────────────────────────────
# Trend Detection
# ─────────────────────────────────────────────

def detect_trend(candles: List[Dict[str, Any]], lookback: int = 20) -> str:
    """
    Simple trend detection using swing highs/lows.
    Returns: 'bullish', 'bearish', or 'neutral'
    """
    if len(candles) < lookback:
        return "neutral"
    
    recent = candles[-lookback:]
    closes = [_safe_float(c.get("close")) for c in recent]
    closes = [c for c in closes if c is not None]
    
    if len(closes) < 10:
        return "neutral"
    
    # Use linear regression slope
    n = len(closes)
    x_mean = (n - 1) / 2
    y_mean = sum(closes) / n
    
    numerator = sum((i - x_mean) * (closes[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return "neutral"
    
    slope = numerator / denominator
    slope_pct = (slope / y_mean) * 100 if y_mean != 0 else 0
    
    if slope_pct > 0.05:   # > 0.05% per candle = bullish
        return "bullish"
    elif slope_pct < -0.05:
        return "bearish"
    else:
        return "neutral"


# ─────────────────────────────────────────────
# Candle Pattern Detection
# ─────────────────────────────────────────────

def is_bullish_rejection(candle: Dict[str, Any]) -> bool:
    """Check if candle is a bullish rejection (hammer/pin bar)"""
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
    
    # Hammer: small body, long lower wick (>2x body), close near high
    return (
        body > 0 and
        lower_wick > 2 * body and
        upper_wick < body * 0.5 and
        (c - l) / total_range > 0.65  # Close in upper third
    )


def is_bearish_rejection(candle: Dict[str, Any]) -> bool:
    """Check if candle is a bearish rejection (shooting star)"""
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
    
    # Shooting star: small body, long upper wick (>2x body), close near low
    return (
        body > 0 and
        upper_wick > 2 * body and
        lower_wick < body * 0.5 and
        (h - c) / total_range > 0.65  # Close in lower third
    )


def is_bullish_engulfing(candle: Dict[str, Any], prev: Dict[str, Any]) -> bool:
    """Check for bullish engulfing pattern"""
    o = _safe_float(candle.get("open"))
    c = _safe_float(candle.get("close"))
    po = _safe_float(prev.get("open"))
    pc = _safe_float(prev.get("close"))
    
    if any(x is None for x in [o, c, po, pc]):
        return False
    
    # Previous bearish, current bullish, current body engulfs previous
    return (
        pc < po and      # Previous candle bearish
        c > o and         # Current candle bullish
        o <= pc and       # Current open <= previous close
        c >= po           # Current close >= previous open
    )


def is_bearish_engulfing(candle: Dict[str, Any], prev: Dict[str, Any]) -> bool:
    """Check for bearish engulfing pattern"""
    o = _safe_float(candle.get("open"))
    c = _safe_float(candle.get("close"))
    po = _safe_float(prev.get("open"))
    pc = _safe_float(prev.get("close"))
    
    if any(x is None for x in [o, c, po, pc]):
        return False
    
    return (
        pc > po and      # Previous candle bullish
        c < o and         # Current candle bearish
        o >= pc and       # Current open >= previous close
        c <= po           # Current close <= previous open
    )


# ─────────────────────────────────────────────
# Paper Trading Engine
# ─────────────────────────────────────────────

@dataclass
class PaperTrade:
    """A single paper trade"""
    trade_id: int
    coin: str
    direction: str           # 'long' or 'short'
    entry_price: float
    stop_loss: float
    tp1: float               # Take profit 1 (50% exit)
    tp2: float               # Take profit 2 (full exit)
    position_size: float     # Notional value
    risk_amount: float       # Dollar risk
    entry_time: str
    entry_candle_idx: int
    
    # Status
    status: str = "open"     # open, tp1_hit, closed, stopped
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    exit_candle_idx: Optional[int] = None
    pnl: float = 0.0
    pnl_r: float = 0.0       # PnL in R-multiples
    partial_closed: bool = False
    notes: str = ""


@dataclass
class PerformanceMetrics:
    """Trading performance metrics"""
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
    avg_rr: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    avg_win_r: float = 0.0
    avg_loss_r: float = 0.0
    sharpe_ratio: float = 0.0
    total_r: float = 0.0


class POCPaperTrader:
    """Paper trading engine for POC retest strategy"""
    
    def __init__(self, coin: str, config: POCConfig):
        self.coin = coin
        self.config = config
        self.equity = config.starting_capital
        self.peak_equity = config.starting_capital
        self.trades: List[PaperTrade] = []
        self.open_trades: List[PaperTrade] = []
        self.trade_counter = 0
        self.equity_curve: List[float] = [config.starting_capital]
    
    def _fetch_candles(self, interval: str, hours: float) -> List[Dict[str, Any]]:
        """Fetch candle data from Hyperliquid API"""
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
            raise ValueError(f"No candles returned for {self.coin} ({interval}, {hours}h)")
        
        return candles
    
    def _calculate_position_size(self, entry_price: float, stop_price: float) -> Tuple[float, float]:
        """Calculate position size based on risk management"""
        risk_pct = self.config.risk_per_trade
        risk_dollars = self.equity * risk_pct
        
        # Stop distance in price
        stop_distance = abs(entry_price - stop_price)
        if stop_distance == 0:
            return 0.0, 0.0
        
        # Position size = risk_dollars / stop_distance
        position_size = risk_dollars / stop_distance
        
        return position_size, risk_dollars
    
    def _check_entry_signal(
        self,
        candles: List[Dict[str, Any]],
        idx: int,
        vp: VolumeProfile,
        trend: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Check for POC retest entry signal at candle index.
        Returns signal dict or None.
        """
        if idx < 1:
            return None
        
        candle = candles[idx]
        prev_candle = candles[idx - 1]
        
        close = _safe_float(candle.get("close"))
        high = _safe_float(candle.get("high"))
        low = _safe_float(candle.get("low"))
        volume = _safe_float(candle.get("volume"))
        
        if any(x is None for x in [close, high, low, volume]):
            return None
        
        # Check if price is near POC
        poc_distance_pct = abs(close - vp.poc) / vp.poc
        
        # Check for POC retest (price touched POC zone during the candle)
        poc_touched = (
            (low <= vp.poc * (1 + self.config.poc_tolerance_pct)) and
            (high >= vp.poc * (1 - self.config.poc_tolerance_pct))
        )
        
        if not poc_touched:
            return None
        
        # Check minimum distance between retests
        if self.open_trades:
            last_trade = max(self.open_trades, key=lambda t: t.entry_candle_idx)
            if idx - last_trade.entry_candle_idx < self.config.min_candles_between_retests:
                return None
        
        # Determine direction based on trend + candle confirmation
        direction = None
        confirmation = ""
        
        # Check for rejection candles
        if is_bullish_rejection(candle):
            direction = "long"
            confirmation = "bullish_rejection"
        elif is_bearish_rejection(candle):
            direction = "short"
            confirmation = "bearish_rejection"
        elif idx >= 2:
            if is_bullish_engulfing(candle, prev_candle):
                direction = "long"
                confirmation = "bullish_engulfing"
            elif is_bearish_engulfing(candle, prev_candle):
                direction = "short"
                confirmation = "bearish_engulfing"
        
        # If no candle pattern, use trend + position in value area
        if direction is None:
            if trend == "bullish" and close < vp.poc:
                direction = "long"
                confirmation = "trend_bullish_at_poc"
            elif trend == "bearish" and close > vp.poc:
                direction = "short"
                confirmation = "trend_bearish_at_poc"
            elif close > vp.vah:
                direction = "short"
                confirmation = "above_value_area"
            elif close < vp.val:
                direction = "long"
                confirmation = "below_value_area"
        
        if direction is None:
            return None
        
        # Trend alignment filter
        if self.config.require_htf_trend:
            if trend == "neutral":
                # Allow neutral trend but reduce confidence
                pass
            elif trend == "bullish" and direction == "short":
                return None  # Don't short into bullish trend
            elif trend == "bearish" and direction == "long":
                return None  # Don't long into bearish trend
        
        # Volume filter
        if self.config.require_volume_spike:
            # Calculate average volume over recent candles
            lookback = min(20, idx)
            avg_vol = sum(
                _safe_float(candles[i].get("volume")) or 0
                for i in range(idx - lookback, idx)
            ) / lookback
            
            if avg_vol > 0 and volume < avg_vol * self.config.volume_spike_mult:
                return None
        
        # Calculate stop and target
        if direction == "long":
            stop = min(low, vp.val) * (1 - self.config.stop_buffer_pct)
            # Target: VAH or next structural level
            target1 = vp.poc + (vp.poc - stop) * self.config.tp1_rr
            target2 = vp.poc + (vp.poc - stop) * self.config.tp2_rr
            # Use VAH as minimum target if closer
            target1 = max(target1, vp.vah)
        else:
            stop = max(high, vp.vah) * (1 + self.config.stop_buffer_pct)
            target1 = vp.poc - (stop - vp.poc) * self.config.tp1_rr
            target2 = vp.poc - (stop - vp.poc) * self.config.tp2_rr
            # Use VAL as minimum target if closer
            target1 = min(target1, vp.val)
        
        # Check R:R ratio
        risk = abs(close - stop)
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
            "confirmation": confirmation,
            "trend": trend,
            "poc": vp.poc,
            "vah": vp.vah,
            "val": vp.val,
            "volume_ratio": volume / (sum(_safe_float(candles[i].get("volume")) or 0 for i in range(max(0, idx-20), idx)) / min(20, idx)) if idx > 0 else 0,
        }
    
    def _open_trade(self, signal: Dict[str, Any], candle: Dict[str, Any], candle_idx: int) -> PaperTrade:
        """Open a new paper trade"""
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
            notes=f"Signal: {signal['confirmation']}, Trend: {signal['trend']}, R:R={signal['rr_ratio']:.2f}"
        )
        
        self.open_trades.append(trade)
        self.trades.append(trade)
        return trade
    
    def _check_exits(self, candles: List[Dict[str, Any]], idx: int) -> List[str]:
        """Check for stop loss, TP1, TP2 hits on open trades"""
        candle = candles[idx]
        high = _safe_float(candle.get("high"))
        low = _safe_float(candle.get("low"))
        
        if high is None or low is None:
            return []
        
        events = []
        closed_trades = []
        
        for trade in self.open_trades:
            if trade.status == "tp1_hit":
                # Already took partial — check TP2 or trailing stop
                if trade.direction == "long" and high >= trade.tp2:
                    # TP2 hit — close remainder
                    remaining_size = trade.position_size * 0.5
                    pnl = (trade.tp2 - trade.entry_price) * remaining_size
                    trade.pnl += pnl
                    trade.pnl_r = trade.pnl / trade.risk_amount
                    trade.status = "closed"
                    trade.exit_price = trade.tp2
                    trade.exit_time = _format_timestamp_ms(candle.get("time"))
                    trade.exit_candle_idx = idx
                    self.equity += pnl
                    events.append(f"TP2 HIT: {trade.coin} {trade.direction.upper()} @ {trade.tp2:.4f} | PnL: ${pnl:+.2f} ({trade.pnl_r:+.2f}R)")
                    closed_trades.append(trade)
                
                elif trade.direction == "short" and low <= trade.tp2:
                    remaining_size = trade.position_size * 0.5
                    pnl = (trade.entry_price - trade.tp2) * remaining_size
                    trade.pnl += pnl
                    trade.pnl_r = trade.pnl / trade.risk_amount
                    trade.status = "closed"
                    trade.exit_price = trade.tp2
                    trade.exit_time = _format_timestamp_ms(candle.get("time"))
                    trade.exit_candle_idx = idx
                    self.equity += pnl
                    events.append(f"TP2 HIT: {trade.coin} {trade.direction.upper()} @ {trade.tp2:.4f} | PnL: ${pnl:+.2f} ({trade.pnl_r:+.2f}R)")
                    closed_trades.append(trade)
                continue
            
            if trade.direction == "long":
                # Check stop loss
                if low <= trade.stop_loss:
                    pnl = (trade.stop_loss - trade.entry_price) * trade.position_size
                    trade.pnl = pnl
                    trade.pnl_r = -1.0  # Always -1R on stop
                    trade.status = "stopped"
                    trade.exit_price = trade.stop_loss
                    trade.exit_time = _format_timestamp_ms(candle.get("time"))
                    trade.exit_candle_idx = idx
                    self.equity += pnl
                    events.append(f"STOPPED: {trade.coin} {trade.direction.upper()} @ {trade.stop_loss:.4f} | PnL: ${pnl:+.2f} (-1.0R)")
                    closed_trades.append(trade)
                
                # Check TP1
                elif high >= trade.tp1 and not trade.partial_closed:
                    pnl = (trade.tp1 - trade.entry_price) * (trade.position_size * 0.5)
                    trade.pnl += pnl
                    trade.partial_closed = True
                    trade.status = "tp1_hit"
                    events.append(f"TP1 HIT: {trade.coin} {trade.direction.upper()} @ {trade.tp1:.4f} | Partial PnL: ${pnl:+.2f}")
            
            else:  # short
                # Check stop loss
                if high >= trade.stop_loss:
                    pnl = (trade.entry_price - trade.stop_loss) * trade.position_size
                    trade.pnl = pnl
                    trade.pnl_r = -1.0
                    trade.status = "stopped"
                    trade.exit_price = trade.stop_loss
                    trade.exit_time = _format_timestamp_ms(candle.get("time"))
                    trade.exit_candle_idx = idx
                    self.equity += pnl
                    events.append(f"STOPPED: {trade.coin} {trade.direction.upper()} @ {trade.stop_loss:.4f} | PnL: ${pnl:+.2f} (-1.0R)")
                    closed_trades.append(trade)
                
                # Check TP1
                elif low <= trade.tp1 and not trade.partial_closed:
                    pnl = (trade.entry_price - trade.tp1) * (trade.position_size * 0.5)
                    trade.pnl += pnl
                    trade.partial_closed = True
                    trade.status = "tp1_hit"
                    events.append(f"TP1 HIT: {trade.coin} {trade.direction.upper()} @ {trade.tp1:.4f} | Partial PnL: ${pnl:+.2f}")
        
        for trade in closed_trades:
            if trade in self.open_trades:
                self.open_trades.remove(trade)
        
        return events
    
    def run(self, interval: str = "1h", hours: float = 168) -> Dict[str, Any]:
        """Run the paper trading simulation"""
        print(f"\n{'='*60}")
        print(f"  POC Paper Trader — {self.coin}")
        print(f"  Interval: {interval} | Lookback: {hours}h")
        print(f"  Capital: ${self.config.starting_capital:,.2f}")
        print(f"  Risk per trade: {self.config.risk_per_trade*100:.1f}%")
        print(f"{'='*60}\n")
        
        # Fetch data
        print("Fetching candle data from Hyperliquid...")
        candles = self._fetch_candles(interval, hours)
        print(f"Loaded {len(candles)} candles")
        
        # Calculate Volume Profile
        print(f"Calculating Volume Profile (lookback: {self.config.vp_lookback} candles)...")
        
        all_events = []
        
        # Simulate through candles
        vp_lookback = self.config.vp_lookback
        
        for idx in range(vp_lookback, len(candles)):
            # Calculate rolling Volume Profile
            vp_slice = candles[max(0, idx - vp_lookback):idx + 1]
            vp = calculate_volume_profile(vp_slice, self.config.price_bins, self.config.value_area_pct)
            
            # Detect trend
            trend = detect_trend(candles[:idx + 1])
            
            # Check for exits first
            exit_events = self._check_exits(candles, idx)
            all_events.extend(exit_events)
            
            # Check for entry signals (if not at max positions)
            if len(self.open_trades) < self.config.max_open_trades:
                signal = self._check_entry_signal(candles, idx, vp, trend)
                
                if signal:
                    trade = self._open_trade(signal, candles[idx], idx)
                    entry_event = (
                        f"ENTRY: {trade.coin} {trade.direction.upper()} @ {trade.entry_price:.4f} | "
                        f"Stop: {trade.stop_loss:.4f} | TP1: {trade.tp1:.4f} | TP2: {trade.tp2:.4f} | "
                        f"R:R: {signal['rr_ratio']:.2f} | Signal: {signal['confirmation']}"
                    )
                    all_events.append(entry_event)
            
            # Update equity curve
            self.equity_curve.append(self.equity)
            self.peak_equity = max(self.peak_equity, self.equity)
        
        # Force close any remaining open trades at last candle
        for trade in list(self.open_trades):
            last_candle = candles[-1]
            last_close = _safe_float(last_candle.get("close"))
            if last_close:
                if trade.direction == "long":
                    pnl = (last_close - trade.entry_price) * trade.position_size
                else:
                    pnl = (trade.entry_price - last_close) * trade.position_size
                
                trade.pnl += pnl
                trade.pnl_r = trade.pnl / trade.risk_amount
                trade.status = "closed"
                trade.exit_price = last_close
                trade.exit_time = _format_timestamp_ms(last_candle.get("time"))
                trade.exit_candle_idx = len(candles) - 1
                trade.notes += " | Force-closed at end of data"
                self.equity += pnl
        
        self.open_trades.clear()
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        return {
            "coin": self.coin,
            "interval": interval,
            "hours": hours,
            "candles": len(candles),
            "config": asdict(self.config),
            "metrics": asdict(metrics),
            "trades": [asdict(t) for t in self.trades],
            "equity_curve": self.equity_curve,
            "events": all_events,
            "final_vp": {
                "poc": vp.poc if 'vp' in dir() else None,
                "vah": vp.vah if 'vp' in dir() else None,
                "val": vp.val if 'vp' in dir() else None,
            } if 'vp' in locals() else None,
        }
    
    def _calculate_metrics(self) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        if not self.trades:
            return PerformanceMetrics()
        
        metrics = PerformanceMetrics()
        metrics.total_trades = len(self.trades)
        
        # Separate wins and losses
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        breakeven_trades = [t for t in self.trades if t.pnl == 0]
        
        metrics.wins = len(winning_trades)
        metrics.losses = len(losing_trades)
        metrics.win_rate = (metrics.wins / metrics.total_trades * 100) if metrics.total_trades > 0 else 0
        
        # PnL
        metrics.total_pnl = sum(t.pnl for t in self.trades)
        metrics.avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        metrics.avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # R-multiples
        r_values = [t.pnl_r for t in self.trades if t.pnl_r != 0]
        metrics.total_r = sum(r_values)
        metrics.expectancy_r = sum(r_values) / len(r_values) if r_values else 0
        metrics.avg_win_r = sum(t.pnl_r for t in winning_trades) / len(winning_trades) if winning_trades else 0
        metrics.avg_loss_r = sum(t.pnl_r for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Profit Factor
        gross_profits = sum(t.pnl for t in winning_trades)
        gross_losses = abs(sum(t.pnl for t in losing_trades))
        metrics.profit_factor = gross_profits / gross_losses if gross_losses > 0 else float('inf')
        
        # Best/Worst
        metrics.best_trade = max(t.pnl_r for t in self.trades) if self.trades else 0
        metrics.worst_trade = min(t.pnl_r for t in self.trades) if self.trades else 0
        
        # Average R:R
        rr_values = [abs(t.pnl_r) for t in self.trades if t.pnl_r != 0]
        metrics.avg_rr = sum(rr_values) / len(rr_values) if rr_values else 0
        
        # Max Drawdown
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
            metrics.max_drawdown = max_dd
            metrics.max_drawdown_pct = max_dd_pct * 100
        
        # Sharpe Ratio (simplified)
        if len(r_values) > 1:
            mean_r = sum(r_values) / len(r_values)
            std_r = math.sqrt(sum((r - mean_r) ** 2 for r in r_values) / (len(r_values) - 1))
            # Annualize: assume ~1 trade per day for simplicity
            trades_per_year = min(len(r_values), 365)
            metrics.sharpe_ratio = (mean_r / std_r) * math.sqrt(trades_per_year) if std_r > 0 else 0
        
        return metrics


# ─────────────────────────────────────────────
# Rendering
# ─────────────────────────────────────────────

def render_results(data: Dict[str, Any]) -> str:
    """Render paper trading results as human-readable text"""
    metrics = data["metrics"]
    config = data["config"]
    
    lines = [
        f"\n{'='*60}",
        f"  PAPER TRADING RESULTS — {data['coin']}",
        f"{'='*60}",
        f"",
        f"  Period: {data['candles']} candles ({data['interval']}, {data['hours']}h)",
        f"  Starting Capital: ${config['starting_capital']:,.2f}",
        f"  Final Equity: ${config['starting_capital'] + metrics['total_pnl']:,.2f}",
        f"",
        f"  {'─'*56}",
        f"  PERFORMANCE SUMMARY",
        f"  {'─'*56}",
        f"  Total Trades:     {metrics['total_trades']}",
        f"  Wins / Losses:    {metrics['wins']} / {metrics['losses']}",
        f"  Win Rate:         {metrics['win_rate']:.1f}%",
        f"",
        f"  Total PnL:        ${metrics['total_pnl']:+,.2f}",
        f"  Total R:          {metrics['total_r']:+.2f}R",
        f"  Expectancy:       {metrics['expectancy_r']:+.3f}R per trade",
        f"",
        f"  Avg Win:          ${metrics['avg_win']:+,.2f} ({metrics['avg_win_r']:+.2f}R)",
        f"  Avg Loss:         ${metrics['avg_loss']:+,.2f} ({metrics['avg_loss_r']:+.2f}R)",
        f"  Profit Factor:    {metrics['profit_factor']:.2f}",
        f"",
        f"  Best Trade:       {metrics['best_trade']:+.2f}R",
        f"  Worst Trade:      {metrics['worst_trade']:+.2f}R",
        f"",
        f"  Max Drawdown:     ${metrics['max_drawdown']:,.2f} ({metrics['max_drawdown_pct']:.1f}%)",
        f"  Sharpe Ratio:     {metrics['sharpe_ratio']:.2f}",
    ]
    
    # Trade log
    if data["trades"]:
        lines.extend([
            f"",
            f"  {'─'*56}",
            f"  TRADE LOG",
            f"  {'─'*56}",
        ])
        
        for trade in data["trades"][:20]:  # Last 20 trades
            status_icon = "✓" if trade["pnl"] > 0 else "✗" if trade["pnl"] < 0 else "="
            lines.append(
                f"  {status_icon} #{trade['trade_id']:3d} | {trade['direction']:5s} @ {trade['entry_price']:>12,.4f} → "
                f"{trade['exit_price']:>12,.4f} | {trade['pnl_r']:+.2f}R | ${trade['pnl']:+,.2f} | {trade['notes'][:30]}"
            )
    
    # Events (entries/exits)
    if data["events"]:
        lines.extend([
            f"",
            f"  {'─'*56}",
            f"  KEY EVENTS (last 20)",
            f"  {'─'*56}",
        ])
        for event in data["events"][-20:]:
            lines.append(f"  • {event}")
    
    lines.append(f"\n{'='*60}\n")
    
    return "\n".join(lines)


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="POC Paper Trading Bot for Hyperliquid",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 poc_paper_trader.py BTC --interval 1h --hours 168
  python3 poc_paper_trader.py ETH --interval 15m --hours 72 --risk 0.02
  python3 poc_paper_trader.py BTC --interval 4h --hours 336 --json
        """,
    )
    
    parser.add_argument("coin", help="Coin to trade (e.g., BTC, ETH, SOL)")
    parser.add_argument("--interval", default="1h", help="Candle interval (default: 1h)")
    parser.add_argument("--hours", type=float, default=168, help="Lookback in hours (default: 168 = 7 days)")
    parser.add_argument("--risk", type=float, default=0.01, help="Risk per trade as decimal (default: 0.01 = 1%%)")
    parser.add_argument("--capital", type=float, default=10000, help="Starting capital (default: 10000)")
    parser.add_argument("--vp-lookback", type=int, default=100, help="Volume Profile lookback candles (default: 100)")
    parser.add_argument("--poc-tolerance", type=float, default=0.003, help="POC retest tolerance (default: 0.003 = 0.3%%)")
    parser.add_argument("--min-rr", type=float, default=1.5, help="Minimum R:R ratio (default: 1.5)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    # Build config
    config = POCConfig(
        risk_per_trade=args.risk,
        starting_capital=args.capital,
        vp_lookback=args.vp_lookback,
        poc_tolerance_pct=args.poc_tolerance,
        min_rr_ratio=args.min_rr,
    )
    
    # Run
    trader = POCPaperTrader(args.coin.upper(), config)
    results = trader.run(args.interval, args.hours)
    
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(render_results(results))


if __name__ == "__main__":
    main()
