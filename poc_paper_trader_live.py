#!/usr/bin/env python3
"""
POC Paper Trader V2 — Live 24/7 Mode with Dynamic Coin Selection
==================================================================
Runs every N minutes via cron. No output = no signal (silent).
Prints notifications for: entries, exits (stop/TP), and time exits. Silent on watchlist changes and daily recap.

Coin Selection: runs the 7-analyzer scanner every WATCHLIST_REFRESH_MIN 
to dynamically pick the best coins. No more hardcoded BTC/HYPE.

State persisted to /root/.hermes/profiles/trader/paper_trader_data/
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# ── Import V2 indicator engine ──
_hl_dir = "/root/.hermes/profiles/trader/skills/hyperliquid/scripts"
if _hl_dir not in sys.path:
    sys.path.insert(0, _hl_dir)
from hyperliquid_client import (
    _post_info, _normalize_candles, _normalize_funding_history,
    _hours_ago_ms, _safe_float,
    _format_price, _format_percent, _format_timestamp_ms,
)

# Import V2 indicator functions
sys.path.insert(0, "/root/.hermes/profiles/trader/scripts")
from poc_paper_trader_v2 import (
    POCConfig, IndicatorSnapshot, VolumeProfile, ConfluenceScore,
    calculate_volume_profile, calculate_vwap, calculate_obv, calculate_cmf, calculate_mfi,
    detect_trend, fetch_funding_sentiment, get_candle_signal, calculate_confluence,
    PaperTrade, PerformanceMetrics, _format_price, _format_percent,
    # Wyckoff 2.0 imports
    WyckoffStructure, WyckoffEvents, VpocMigration,
    detect_structure_context, detect_wyckoff_events,
    track_vpoc_migration, score_wyckoff,
)

# Import coin selection analyzers
from coin_analyzers import (
    select_coins, SelectorConfig, CompositeResult,
    fetch_candles_fast, render_result,
)

# ── State Directory ──
STATE_DIR = "/root/.hermes/profiles/trader/paper_trader_data"
os.makedirs(STATE_DIR, exist_ok=True)

# ── Configuration ──
INTERVAL = "1h"
POLL_CANDLES = 150  # Enough for 1h indicators + Volume Profile
TOTAL_CAPITAL = 300.0
RISK_PER_TRADE = 0.005               # 0.5% per trade (3 positions × 0.5% = 1.5% total max)
MIN_SCORE = 3.0                      # Raised from 2.2 — require majority conviction
MIN_RR = 1.5

# Coin selection
WATCHLIST_REFRESH_MIN = 240          # Re-scan every 4 hours
MAX_WATCHLIST_COINS = 10             # Top 10 coins for ranking/display
ACTIVE_COIN_SLOTS = 3                # Up to 3 concurrent positions
COIN_SELECTOR_MIN_VOLUME = 100_000   # Min 24h volume for coin to be considered
CAPITAL_PER_SLOT = TOTAL_CAPITAL / ACTIVE_COIN_SLOTS  # $100 per slot

# Risk management
MAX_HOLD_HOURS = 24                  # Close if TP1 not hit within 24h
MAX_DRAWDOWN_PCT = 10.0              # Pause all entries if DD > 10%
ATR_STOP_MULTIPLIER = 1.5            # Stop = entry ± (ATR × 1.5)

# Fallback if scanner fails
FALLBACK_COINS = ["BTC", "HYPE"]


# ═══════════════════════════════════════════════
# Coin Watchlist Management
# ═══════════════════════════════════════════════

def refresh_watchlist() -> Tuple[List[str], str]:
    """
    Run the coin selection scanner and return (top N coins, scanner_report).
    Falls back to BTC/HYPE on failure.
    """
    try:
        config = SelectorConfig(
            min_volume=COIN_SELECTOR_MIN_VOLUME,
            max_coins_returned=MAX_WATCHLIST_COINS,
            include_xyz=True,
        )
        result = select_coins(config)
        coins = [c["coin"] for c in result.ranked_coins if c["composite_score"] > -3]
        
        if coins:
            return coins, render_result(result)
        
        # Fallback: top coins even if score is low
        coins = [c["coin"] for c in result.ranked_coins[:MAX_WATCHLIST_COINS]]
        if coins:
            return coins, render_result(result)
            
    except Exception as e:
        pass  # Fall through to fallback
    
    return list(FALLBACK_COINS), "Scanner failed, using fallback"


def should_refresh_watchlist(state: LiveState) -> bool:
    """Check if the watchlist needs refreshing based on time since last scan"""
    last_scan = state.last_watchlist_scan
    if not last_scan:
        return True
    try:
        last_dt = datetime.strptime(last_scan, "%Y-%m-%d %H:%M:%S UTC")
        elapsed = (datetime.now(timezone.utc) - last_dt.replace(tzinfo=timezone.utc)).total_seconds()
        return elapsed >= WATCHLIST_REFRESH_MIN * 60
    except (ValueError, AttributeError):
        return True


# ── State Management ──

@dataclass
class LiveState:
    """Persistent state for live trading"""
    # Per-coin state
    coin_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Trade history
    trades: Dict[str, List[Dict]] = field(default_factory=lambda: {})
    # Last run timestamp
    last_run: str = ""
    # Last daily recap date (YYYY-MM-DD)
    last_recap_date: str = ""
    # Starting capital
    starting_capital: float = 300.0
    # Current equity
    equity: float = 300.0
    # Peak equity (for drawdown tracking)
    peak_equity: float = 300.0
    # Decision log — captures every entry/skip with reasons
    decision_log: List[Dict[str, Any]] = field(default_factory=list)
    # Current watchlist (dynamic coin selection)
    watchlist: List[str] = field(default_factory=lambda: list(FALLBACK_COINS))
    # Last watchlist scan timestamp
    last_watchlist_scan: str = ""
    # Last scanner report text (for reference)
    last_scanner_report: str = ""


def load_state() -> LiveState:
    path = os.path.join(STATE_DIR, "live_state.json")
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        # Ensure trades dict has all watchlist coins
        state = LiveState(**data)
        return state
    return LiveState()


def save_state(state: LiveState) -> None:
    # Don't recalculate equity from coin_states — it loses value from pruned coins.
    # equity is already maintained by trade open/close logic (pnl adjustments).
    # Only update peak_equity.
    state.peak_equity = max(state.peak_equity, state.equity)
    path = os.path.join(STATE_DIR, "live_state.json")
    with open(path, "w") as f:
        json.dump(asdict(state), f, indent=2, default=str)


def get_coin_state(state: LiveState, coin: str, capital_per_coin: float = 0.0) -> Dict[str, Any]:
    if coin not in state.coin_states:
        state.coin_states[coin] = {
            "open_trades": [],
            "equity": capital_per_coin,
            "peak_equity": capital_per_coin,
            "trade_counter": 0,
        }
    return state.coin_states[coin]


# ── ATR Calculation ──

def calculate_atr(candles: List[Dict[str, Any]], period: int = 14) -> Optional[float]:
    """Calculate Average True Range for stop placement"""
    if len(candles) < period + 1:
        return None
    
    true_ranges = []
    for i in range(1, len(candles)):
        h = _safe_float(candles[i].get("high")) or 0.0
        l = _safe_float(candles[i].get("low")) or 0.0
        prev_c = _safe_float(candles[i-1].get("close")) or 0.0
        
        tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
        true_ranges.append(tr)
    
    if len(true_ranges) < period:
        return None
    
    # Use last N periods
    return sum(true_ranges[-period:]) / period


# ── Trade Execution ──

def _exit_log_entry(time_str, coin, action, reason, exit_type, pnl, trade):
    """Build an enriched exit log entry with entry criteria from the trade object."""
    entry = {
        "time": time_str,
        "coin": coin,
        "action": action,
        "reason": reason,
        "exit_type": exit_type,
        "pnl": pnl,
        # Entry criteria (from the original trade)
        "direction": trade.get("direction", "long"),
        "entry_price": trade.get("entry_price", 0),
        "confluence_score": trade.get("confluence_score", 0),
        "signal_breakdown": trade.get("signal_breakdown", ""),
        "stop_loss": trade.get("stop_loss", 0),
        "tp1": trade.get("tp1", 0),
        "tp2": trade.get("tp2", 0),
        "rr_ratio": trade.get("rr_ratio", 0),
    }
    return entry


def open_trade(
    coin: str,
    direction: str,
    entry_price: float,
    stop_loss: float,
    tp1: float,
    tp2: float,
    position_size: float,
    risk_amount: float,
    confluence_score: float,
    signal_breakdown: str,
    funding_rate: float,
    funding_sentiment: str,
    rr_ratio: float,
) -> Dict[str, Any]:
    return {
        "trade_id": 0,  # filled by caller
        "coin": coin,
        "direction": direction,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "tp1": tp1,
        "tp2": tp2,
        "position_size": position_size,
        "risk_amount": risk_amount,
        "entry_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "confluence_score": confluence_score,
        "signal_breakdown": signal_breakdown,
        "funding_rate": funding_rate,
        "funding_sentiment": funding_sentiment,
        "rr_ratio": rr_ratio,
        "status": "open",
        "partial_closed": False,
        "pnl": 0.0,
        "pnl_r": 0.0,
        "exit_price": None,
        "exit_time": None,
        "notes": "",
    }


def format_notification(coin: str, event_type: str, data: Dict[str, Any]) -> str:
    """Format a Telegram-friendly notification string"""
    if event_type == "entry":
        d = data["direction"].upper()
        return (
            f"🟢 *ENTRY {d} {coin}* @ ${data['entry_price']:,.2f}\n"
            f"├ Score: {data['confluence_score']:+.1f}/10\n"
            f"├ Stop: ${data['stop_loss']:,.2f} ({abs(data['entry_price']-data['stop_loss'])/data['entry_price']*100:.2f}%)\n"
            f"├ TP1: ${data['tp1']:,.2f} ({data['tp1_rr']:.1f}R)\n"
            f"├ TP2: ${data['tp2']:,.2f} ({data['tp2_rr']:.1f}R)\n"
            f"├ Size: {data['position_size']:.4f} units\n"
            f"├ Risk: ${data['risk_amount']:.2f}\n"
            f"└ Funding: {data.get('funding_rate',0)*100:.4f}% ({data.get('funding_sentiment','neutral')})"
        )
    
    elif event_type == "stop":
        return (
            f"🔴 *STOP LOSS {coin}*\n"
            f"├ Exit: ${data['exit_price']:,.2f}\n"
            f"├ PnL: ${data['pnl']:+,.2f} ({data['pnl_r']:+.2f}R)\n"
            f"└ {data.get('notes', '')}"
        )
    
    elif event_type == "tp1":
        return (
            f"✅ *TP1 HIT {coin}* (50% closed)\n"
            f"├ Exit: ${data['exit_price']:,.2f}\n"
            f"├ PnL so far: ${data['pnl']:+,.2f}\n"
            f"└ Remaining running to TP2: ${data['tp2']:,.2f}"
        )
    
    elif event_type == "tp2":
        return (
            f"🏆 *TP2 HIT {coin}* — FULL CLOSE\n"
            f"├ Exit: ${data['exit_price']:,.2f}\n"
            f"├ Total PnL: ${data['pnl']:+,.2f} ({data['pnl_r']:+.2f}R)\n"
            f"└ {data.get('notes', '')}"
        )
    
    elif event_type == "daily_recap":
        return data["text"]  # Pre-formatted
    
    elif event_type == "watchlist":
        return data["text"]
    
    return ""


# ── Core Trading Logic ──

def run_live_check(state: LiveState) -> List[str]:
    """Main trading check. Returns list of notification strings."""
    notifications = []
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    
    # ── Refresh watchlist if needed ──
    if should_refresh_watchlist(state):
        old_watchlist = list(state.watchlist)
        new_watchlist, scan_report = refresh_watchlist()
        state.watchlist = new_watchlist
        state.last_scanner_report = scan_report
        state.last_watchlist_scan = now.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Prune stale coin states and trades (coins no longer in watchlist)
        # BUT preserve coins with open positions so exits are still monitored
        stale_coins = [c for c in state.coin_states if c not in new_watchlist]
        for c in stale_coins:
            cs = state.coin_states.get(c, {})
            if cs.get("open_trades"):
                continue  # Keep monitoring exits for open positions
            state.coin_states.pop(c, None)
            # DON'T remove from trades — preserve trade history for dashboard/reporting
        
        # Compute allocation: full capital goes to the single active trading coin (#1 ranked)
        # All other coins are signal candidates with $0 equity
        cap_per_coin = 0.0
        
        # Notify on watchlist change — SILENT (user wants entry alerts only)
        
        # Initialize new coins with $0 equity
        for coin in new_watchlist:
            get_coin_state(state, coin, 0.0)
    
    COINS = state.watchlist.copy()
    # Include coins with open positions that rotated out of watchlist
    # so stop-loss, TP, and time-based exits are still monitored
    for _exit_coin, _exit_cs in state.coin_states.items():
        if _exit_coin not in COINS and _exit_cs.get("open_trades"):
            COINS.append(_exit_coin)

    # ── Calculate available capital ──
    # Use state.equity as authoritative total (not sum of coin_states which can drift)
    total_equity = state.equity
    if total_equity <= 0:
        total_equity = TOTAL_CAPITAL  # Bootstrap
    
    capital_locked = 0.0
    total_open_positions = 0
    for cs in state.coin_states.values():
        for trade in cs.get("open_trades", []):
            capital_locked += trade.get("risk_amount", 0)
            total_open_positions += 1
    
    available_slots = max(0, ACTIVE_COIN_SLOTS - total_open_positions)
    available_capital = max(0, total_equity - capital_locked)

    # ── Drawdown check ──
    current_dd = 0.0
    if state.peak_equity > 0:
        current_dd = (state.peak_equity - total_equity) / state.peak_equity * 100
    dd_paused = current_dd >= MAX_DRAWDOWN_PCT
    
    if dd_paused:
        # Log drawdown pause for all coins
        for coin in COINS:
            state.decision_log.append({
                "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                "coin": coin,
                "action": "skip",
                "reason": f"Drawdown circuit breaker: {current_dd:.1f}% >= {MAX_DRAWDOWN_PCT}%",
            })

    # ── Ensure trades dict has current coins ──
    for coin in COINS:
        if coin not in state.trades:
            state.trades[coin] = []

    for coin in COINS:
        cs = get_coin_state(state, coin)
        
        # ── Fetch candle data ──
        try:
            end_ms = int(time.time() * 1000)
            start_ms = _hours_ago_ms(POLL_CANDLES * 1.5, end_ms)
            payload = {
                "type": "candleSnapshot",
                "req": {
                    "coin": coin,
                    "interval": INTERVAL,
                    "startTime": start_ms,
                    "endTime": end_ms,
                },
            }
            raw = _post_info(payload)
            candles = _normalize_candles(raw)
            if not candles or len(candles) < 50:
                continue
        except Exception as e:
            continue
        
        # ── Fetch funding rate ──
        funding_rate = 0.0
        funding_sentiment = "neutral"
        try:
            funding_rate, funding_sentiment = fetch_funding_sentiment(coin, hours=72)
        except Exception:
            pass
        
        idx = len(candles) - 1
        
        # ── Calculate Indicators ──
        try:
            vp_lookback = min(100, len(candles) - 2)
            vp = calculate_volume_profile(
                candles[max(0, idx - vp_lookback):idx + 1],
                num_bins=100, value_area_pct=0.70
            )
            if vp is None:
                continue
            
            trend, trend_strength = detect_trend(candles[:idx + 1])
            
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
                vwap = close; vwap_upper = close; vwap_lower = close
                price_vs_vwap = 0
            
            # OBV
            obv_result = calculate_obv(candles[:idx+1], sma_period=20)
            if obv_result:
                obv, obv_sma, obv_trend = obv_result
            else:
                obv = 0; obv_sma = 0; obv_trend = "neutral"
            
            # CMF, MFI
            cmf = calculate_cmf(candles[:idx+1], period=20) or 0.0
            mfi = calculate_mfi(candles[:idx+1], period=14) or 50.0
            
            # Volume ratio
            lookback_v = min(20, idx)
            if lookback_v > 0:
                avg_vol = sum(
                    _safe_float(candles[i].get("volume")) or 0
                    for i in range(idx - lookback_v, idx)
                ) / lookback_v
                volume_ratio = volume / avg_vol if avg_vol > 0 else 1.0
            else:
                volume_ratio = 1.0
            
            poc_distance_pct = abs(close - vp.poc) / vp.poc if vp.poc > 0 else 0
            
            snapshot = IndicatorSnapshot(
                close=close, high=high, low=low, volume=volume,
                poc=vp.poc, vah=vp.vah, val=vp.val,
                vp_quality=vp.concentration, poc_distance_pct=poc_distance_pct,
                vwap=vwap, vwap_upper=vwap_upper, vwap_lower=vwap_lower,
                price_vs_vwap=price_vs_vwap,
                obv=obv, obv_sma=obv_sma, obv_trend=obv_trend,
                cmf=cmf, cmf_trend="bullish" if cmf > 0.05 else "bearish" if cmf < -0.05 else "neutral",
                mfi=mfi, mfi_zone="overbought" if mfi > 80 else "oversold" if mfi < 20 else "neutral",
                trend=trend, trend_strength=trend_strength,
                funding_rate=funding_rate, funding_sentiment=funding_sentiment,
                volume_ratio=volume_ratio,
            )
            
            prev_candle = candles[idx - 1] if idx > 0 else None
            candle_signal = get_candle_signal(candle, prev_candle)
            
            config = POCConfig(
                risk_per_trade=RISK_PER_TRADE,
                starting_capital=cs.get("equity", TOTAL_CAPITAL),
                min_confluence_score=MIN_SCORE,
                min_rr_ratio=MIN_RR,
            )

            # ── Wyckoff 2.0 Analysis ──
            wyckoff_structure = detect_structure_context(candles, vp)
            wyckoff_events = detect_wyckoff_events(candles, vp, wyckoff_structure)
            wyckoff_migration = track_vpoc_migration(candles, wyckoff_structure)
            wyckoff_struct_score, wyckoff_vpoc_score = score_wyckoff(
                wyckoff_structure, wyckoff_events, wyckoff_migration
            )

            confluence = calculate_confluence(
                snapshot, candle_signal, config,
                wyckoff_structure_score=wyckoff_struct_score,
                wyckoff_vpoc_score=wyckoff_vpoc_score,
            )
            
        except Exception:
            continue
        
        # ── Check Exits (Open positions) ──
        open_trades = cs.get("open_trades", [])
        remaining_open = []
        
        for trade in open_trades:
            t_dir = trade["direction"]
            t_stop = trade["stop_loss"]
            t_tp1 = trade["tp1"]
            t_tp2 = trade["tp2"]
            t_entry = trade["entry_price"]
            t_size = trade["position_size"]
            t_risk = trade["risk_amount"]
            
            trade_ended = False
            
            # ── Time-based exit: close if TP1 not hit within MAX_HOLD_HOURS ──
            entry_time_str = trade.get("entry_time", "")
            if entry_time_str and not trade.get("partial_closed"):
                try:
                    entry_dt = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
                    hours_held = (now - entry_dt).total_seconds() / 3600
                    if hours_held >= MAX_HOLD_HOURS:
                        # TP1 not hit in time — close at market (use current close)
                        pnl = (close - t_entry) * t_size if t_dir == "long" else (t_entry - close) * t_size
                        trade["pnl"] = pnl
                        trade["pnl_r"] = pnl / t_risk if t_risk > 0 else 0
                        trade["status"] = "timeout"
                        trade["exit_price"] = close
                        trade["exit_time"] = now.strftime("%Y-%m-%d %H:%M:%S UTC")
                        trade["notes"] = f"Time exit: {hours_held:.0f}h without TP1"
                        cs["equity"] += pnl
                        state.equity += pnl
                        if cs["equity"] > cs["peak_equity"]:
                            cs["peak_equity"] = cs["equity"]
                        if state.equity > state.peak_equity:
                            state.peak_equity = state.equity
                        notifications.append(format_notification(coin, "stop", {
                            **trade,
                            "notes": f"⏰ Time exit after {hours_held:.0f}h (no TP1)"
                        }))
                        state.decision_log.append(_exit_log_entry(
                            now.strftime("%Y-%m-%d %H:%M UTC"), coin, "exit",
                            f"Time exit after {hours_held:.0f}h | P&L: ${pnl:+.2f}",
                            "timeout", pnl, trade,
                        ))
                        trade_ended = True
                except (ValueError, TypeError):
                    pass
                # Skip stop/TP checks if time exit already fired
                if trade_ended:
                    state.trades[coin].append(trade)
                    continue
            
            if trade.get("partial_closed") and trade.get("status") == "tp1_hit":
                # TP2 check
                if t_dir == "long" and high >= t_tp2:
                    remaining = t_size * 0.5
                    pnl = (t_tp2 - t_entry) * remaining
                    trade["pnl"] += pnl
                    trade["pnl_r"] = trade["pnl"] / t_risk if t_risk > 0 else 0
                    trade["status"] = "closed"
                    trade["exit_price"] = t_tp2
                    trade["exit_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    cs["equity"] += pnl
                    state.equity += pnl
                    if cs["equity"] > cs["peak_equity"]:
                        cs["peak_equity"] = cs["equity"]
                    if state.equity > state.peak_equity:
                        state.peak_equity = state.equity
                    notifications.append(format_notification(coin, "tp2", trade))
                    state.decision_log.append(_exit_log_entry(
                        now.strftime("%Y-%m-%d %H:%M UTC"), coin, "exit",
                        f"TP2 hit @ {t_tp2:.2f} | P&L: ${pnl:+.2f}",
                        "tp2", pnl, trade,
                    ))
                    trade_ended = True
                elif t_dir == "short" and low <= t_tp2:
                    remaining = t_size * 0.5
                    pnl = (t_entry - t_tp2) * remaining
                    trade["pnl"] += pnl
                    trade["pnl_r"] = trade["pnl"] / t_risk if t_risk > 0 else 0
                    trade["status"] = "closed"
                    trade["exit_price"] = t_tp2
                    trade["exit_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    cs["equity"] += pnl
                    state.equity += pnl
                    if cs["equity"] > cs["peak_equity"]:
                        cs["peak_equity"] = cs["equity"]
                    if state.equity > state.peak_equity:
                        state.peak_equity = state.equity
                    notifications.append(format_notification(coin, "tp2", trade))
                    state.decision_log.append(_exit_log_entry(
                        now.strftime("%Y-%m-%d %H:%M UTC"), coin, "exit",
                        f"TP2 hit @ {t_tp2:.2f} | P&L: ${pnl:+.2f}",
                        "tp2", pnl, trade,
                    ))
                    trade_ended = True
                if trade_ended:
                    state.trades[coin].append(trade)
                    continue
            
            elif not trade.get("partial_closed"):
                # Check stop loss
                if t_dir == "long" and low <= t_stop:
                    pnl = (t_stop - t_entry) * t_size
                    trade["pnl"] = pnl
                    trade["pnl_r"] = -1.0
                    trade["status"] = "stopped"
                    trade["exit_price"] = t_stop
                    trade["exit_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    cs["equity"] += pnl
                    state.equity += pnl
                    notifications.append(format_notification(coin, "stop", trade))
                    state.decision_log.append(_exit_log_entry(
                        now.strftime("%Y-%m-%d %H:%M UTC"), coin, "exit",
                        f"Stop loss hit @ {t_stop:.2f} | P&L: ${pnl:+.2f}",
                        "stop", pnl, trade,
                    ))
                    trade_ended = True
                elif t_dir == "short" and high >= t_stop:
                    pnl = (t_entry - t_stop) * t_size
                    trade["pnl"] = pnl
                    trade["pnl_r"] = -1.0
                    trade["status"] = "stopped"
                    trade["exit_price"] = t_stop
                    trade["exit_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    cs["equity"] += pnl
                    state.equity += pnl
                    notifications.append(format_notification(coin, "stop", trade))
                    state.decision_log.append(_exit_log_entry(
                        now.strftime("%Y-%m-%d %H:%M UTC"), coin, "exit",
                        f"Stop loss hit @ {t_stop:.2f} | P&L: ${pnl:+.2f}",
                        "stop", pnl, trade,
                    ))
                    trade_ended = True

                # Check TP1
                if not trade_ended:
                    if t_dir == "long" and high >= t_tp1:
                        pnl = (t_tp1 - t_entry) * (t_size * 0.5)
                        trade["pnl"] += pnl
                        trade["partial_closed"] = True
                        trade["status"] = "tp1_hit"
                        trade["exit_price"] = t_tp1
                        trade["exit_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                        notifications.append(format_notification(coin, "tp1", trade))
                        state.decision_log.append(_exit_log_entry(
                            now.strftime("%Y-%m-%d %H:%M UTC"), coin, "partial_exit",
                            f"TP1 hit @ {t_tp1:.2f} (50% closed) | P&L: ${pnl:+.2f}",
                            "tp1", pnl, trade,
                        ))
                    elif t_dir == "short" and low <= t_tp1:
                        pnl = (t_entry - t_tp1) * (t_size * 0.5)
                        trade["pnl"] += pnl
                        trade["partial_closed"] = True
                        trade["status"] = "tp1_hit"
                        trade["exit_price"] = t_tp1
                        trade["exit_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                        notifications.append(format_notification(coin, "tp1", trade))
                        state.decision_log.append(_exit_log_entry(
                            now.strftime("%Y-%m-%d %H:%M UTC"), coin, "partial_exit",
                            f"TP1 hit @ {t_tp1:.2f} (50% closed) | P&L: ${pnl:+.2f}",
                            "tp1", pnl, trade,
                        ))
            if not trade_ended:
                remaining_open.append(trade)
        
        cs["open_trades"] = remaining_open
        
        # ── Entry: allow top N ranked coins ──
        entry_logged = False
        coin_rank = COINS.index(coin) if coin in COINS else -1
        
        if coin_rank < 0 or coin_rank >= ACTIVE_COIN_SLOTS:
            state.decision_log.append({
                "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                "coin": coin,
                "action": "skip",
                "reason": f"Not top {ACTIVE_COIN_SLOTS} ranked (#{coin_rank+1}). Trading: {', '.join(COINS[:ACTIVE_COIN_SLOTS])}",
                "score": confluence.total if 'confluence' in dir() else 0,
                "direction": confluence.direction if 'confluence' in dir() else "none",
            })
            entry_logged = True
        
        # ── Check Entry Signals ──
        if not entry_logged:
            entry_logged = False
            if available_slots <= 0:
                state.decision_log.append({
                    "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                    "coin": coin,
                    "action": "skip",
                    "reason": f"Max open trades reached ({total_open_positions}/{ACTIVE_COIN_SLOTS})",
                    "score": confluence.total,
                    "direction": confluence.direction,
                })
                entry_logged = True
            elif dd_paused:
                state.decision_log.append({
                    "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                    "coin": coin,
                    "action": "skip",
                    "reason": f"Drawdown circuit breaker: {current_dd:.1f}%",
                    "score": confluence.total,
                    "direction": confluence.direction,
                })
                entry_logged = True
            elif abs(confluence.total) < MIN_SCORE:
                state.decision_log.append({
                    "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                    "coin": coin,
                    "action": "skip",
                    "reason": f"Score too low ({confluence.total:+.1f} < {MIN_SCORE})",
                    "score": confluence.total,
                    "direction": confluence.direction,
                    "breakdown": f"T:{confluence.trend_score:+.1f} V:{confluence.vwap_score:+.1f} O:{confluence.obv_score:+.1f} C:{confluence.cmf_score:+.1f} M:{confluence.mfi_score:+.1f} F:{confluence.funding_score:+.1f} P:{confluence.vp_quality_score:+.1f} K:{confluence.candle_score:+.1f} W:{confluence.wyckoff_structure_score:+.1f} Z:{confluence.wyckoff_vpoc_score:+.1f}",
                    "wyckoff": f"{wyckoff_structure.context}/{wyckoff_structure.structure_type}({wyckoff_structure.phase})",
                })
                entry_logged = True
            elif confluence.direction == "none":
                state.decision_log.append({
                    "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                    "coin": coin,
                    "action": "skip",
                    "reason": f"Confluence direction is none (score {confluence.total:+.1f} but no clear direction)",
                    "score": confluence.total,
                    "direction": confluence.direction,
                })
                entry_logged = True
            elif (snapshot.trend == "bullish" and confluence.direction == "short") or \
                 (snapshot.trend == "bearish" and confluence.direction == "long"):
                state.decision_log.append({
                    "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                    "coin": coin,
                    "action": "skip",
                    "reason": f"Trend misalignment (trend={snapshot.trend}, signal={confluence.direction})",
                    "score": confluence.total,
                    "direction": confluence.direction,
                })
                entry_logged = True
            # ── Wyckoff 2.0 Pre-Filter: veto if structure contradicts signal direction ──
            elif (wyckoff_structure.structure_type == "distribution" and confluence.direction == "long") or \
                 (wyckoff_structure.structure_type == "accumulation" and confluence.direction == "short"):
                state.decision_log.append({
                    "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                    "coin": coin,
                    "action": "skip",
                    "reason": f"Wyckoff veto: structure={wyckoff_structure.structure_type}({wyckoff_structure.phase}) contradicts {confluence.direction}",
                    "score": confluence.total,
                    "direction": confluence.direction,
                    "wyckoff": f"struct={wyckoff_structure.structure_type}_{wyckoff_structure.phase} W:{wyckoff_struct_score:+.2f} P:{wyckoff_vpoc_score:+.2f}",
                })
                entry_logged = True
            else:
                # Check POC retest
                poc_tolerance = 0.003
                poc_touched = (
                    (low <= vp.poc * (1 + poc_tolerance)) and
                    (high >= vp.poc * (1 - poc_tolerance))
                )

                if not poc_touched:
                    state.decision_log.append({
                        "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                        "coin": coin,
                        "action": "skip",
                        "reason": f"No POC retest (price {close:.2f}, POC {vp.poc:.2f}, dist {abs(close-vp.poc)/vp.poc*100:.2f}%)",
                        "score": confluence.total,
                        "direction": confluence.direction,
                    })
                    entry_logged = True
                else:
                    # Calculate entry signal with ATR-based stops
                    direction = confluence.direction

                    # ATR-based stop (tighter than VP extremes)
                    atr = calculate_atr(candles[:idx+1])
                    if atr and atr > 0:
                        if direction == "long":
                            stop = close - (atr * ATR_STOP_MULTIPLIER)
                            # Cap stop at VAL — don't go wider than VP support
                            stop = max(stop, vp.val * 0.998)
                        else:
                            stop = close + (atr * ATR_STOP_MULTIPLIER)
                            # Cap stop at VAH — don't go wider than VP resistance
                            stop = min(stop, vp.vah * 1.002)
                    else:
                        # Fallback to VP-based stops
                        if direction == "long":
                            stop = min(low, vp.val) * 0.998
                        else:
                            stop = max(high, vp.vah) * 1.002
                    
                    if direction == "long":
                        risk = close - stop
                        target1 = close + risk * 1.5
                        target2 = close + risk * 3.0
                    else:
                        risk = stop - close
                        target1 = close - risk * 1.5
                        target2 = close - risk * 3.0

                    if risk <= 0:
                        state.decision_log.append({
                            "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                            "coin": coin,
                            "action": "skip",
                            "reason": f"Invalid risk (risk={risk:.2f}, entry={close:.2f}, stop={stop:.2f})",
                            "score": confluence.total,
                            "direction": confluence.direction,
                        })
                        entry_logged = True
                    else:
                        rr_ratio = abs(target1 - close) / risk

                        if rr_ratio < MIN_RR:
                            state.decision_log.append({
                                "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                                "coin": coin,
                                "action": "skip",
                                "reason": f"R:R too low ({rr_ratio:.2f} < {MIN_RR})",
                                "score": confluence.total,
                                "direction": confluence.direction,
                            })
                            entry_logged = True
                        else:
                            # ENTRY SIGNAL
                            cs["trade_counter"] += 1
                            # Position sizing: use per-slot capital, not full equity
                            slot_capital = min(CAPITAL_PER_SLOT, available_capital)
                            risk_amount = slot_capital * RISK_PER_TRADE
                            position_size = risk_amount / risk

                            sig_breakdown = (
                                f"T:{confluence.trend_score:+.1f} "
                                f"V:{confluence.vwap_score:+.1f} "
                                f"O:{confluence.obv_score:+.1f} "
                                f"C:{confluence.cmf_score:+.1f} "
                                f"M:{confluence.mfi_score:+.1f} "
                                f"F:{confluence.funding_score:+.1f} "
                                f"P:{confluence.vp_quality_score:+.1f} "
                                f"K:{confluence.candle_score:+.1f} "
                                f"W:{confluence.wyckoff_structure_score:+.1f} "
                                f"Z:{confluence.wyckoff_vpoc_score:+.1f}"
                            )

                            trade = open_trade(
                                coin=coin,
                                direction=direction,
                                entry_price=close,
                                stop_loss=stop,
                                tp1=target1,
                                tp2=target2,
                                position_size=position_size,
                                risk_amount=risk_amount,
                                confluence_score=confluence.total,
                                signal_breakdown=sig_breakdown,
                                funding_rate=funding_rate,
                                funding_sentiment=funding_sentiment,
                                rr_ratio=rr_ratio,
                            )
                            trade["trade_id"] = cs["trade_counter"]
                            cs["open_trades"].append(trade)

                            state.decision_log.append({
                                "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                                "coin": coin,
                                "action": "entry",
                                "direction": direction,
                                "entry_price": close,
                                "stop_loss": stop,
                                "tp1": target1,
                                "tp2": target2,
                                "score": confluence.total,
                                "breakdown": sig_breakdown,
                                "rr_ratio": rr_ratio,
                                "reason": f"10-factor confluence {direction.upper()} @ {close:.2f} | Score: {confluence.total:+.1f} | R:R: {rr_ratio:.2f} | W2:{wyckoff_structure.structure_type}({wyckoff_structure.phase})",
                            })
                            entry_logged = True

                            notif_data = {
                                **trade,
                                "tp1_rr": 1.5,
                                "tp2_rr": 3.0,
                            }
                            notifications.append(format_notification(coin, "entry", notif_data))

        if not entry_logged:
            state.decision_log.append({
                "time": now.strftime("%Y-%m-%d %H:%M UTC"),
                "coin": coin,
                "action": "pass",
                "reason": "No actionable signal",
                "score": confluence.total,
                "direction": confluence.direction,
            })
        
        state.coin_states[coin] = cs
    
    # ── Daily Recap ──
    if today != state.last_recap_date:
        state.last_recap_date = today
        
        COINS = state.watchlist
        
        # Top 10 ranking display (compact)
        ranking_lines = []
        for i, c in enumerate(COINS[:10]):
            marker = "▶" if i < ACTIVE_COIN_SLOTS else " "
            ranking_lines.append(f"{marker} #{i+1} {c}")
        ranking_str = "  ".join(ranking_lines[:5])
        if len(COINS) > 5:
            ranking_str += f"  ... (+{len(COINS)-5})"
        
        # Count open positions across all coins
        all_open = 0
        open_details = []
        for c in COINS[:ACTIVE_COIN_SLOTS]:
            c_cs = state.coin_states.get(c, {})
            c_open = len(c_cs.get("open_trades", []))
            if c_open > 0:
                all_open += c_open
                open_details.append(f"{c}({c_open})")
        
        # Drawdown
        drawdown = (state.peak_equity - state.equity) / state.peak_equity * 100 if state.peak_equity > 0 else 0
        
        tg_lines = [
            f"📊 *Daily Recap — {today}*\n",
            f"├ Portfolio Equity: ${state.equity:,.2f} ({(state.equity/state.starting_capital-1)*100:+.2f}%)",
            f"├ Peak Equity: ${state.peak_equity:,.2f}",
            f"├ Drawdown: {drawdown:.1f}%",
            f"├ Slots: {all_open}/{ACTIVE_COIN_SLOTS} open ({', '.join(open_details) if open_details else 'flat'})",
            f"├ Active Coins: {', '.join(COINS[:ACTIVE_COIN_SLOTS])}\n",
        ]
        
        # Show per-slot stats
        for c in COINS[:ACTIVE_COIN_SLOTS]:
            c_cs = state.coin_states.get(c, {})
            c_open = len(c_cs.get("open_trades", []))
            line = f"├ *{c}:*"
            if c_open > 0:
                for t in c_cs.get("open_trades", []):
                    line += f" {t['direction'].upper()} @ ${t['entry_price']:,.2f} ({t['confluence_score']:+.1f})"
                tg_lines.append(line)
            else:
                tg_lines.append(f"{line} waiting for signal")
        
        total_trades = 0
        total_pnl = 0.0
        wins = 0
        losses = 0
        for coin in COINS:
            coin_trades = state.trades.get(coin, [])
            total_trades += len(coin_trades)
            for t in coin_trades:
                total_pnl += t.get("pnl", 0.0)
                if t.get("pnl", 0) > 0: wins += 1
                elif t.get("pnl", 0) < 0: losses += 1
        
        tg_lines.append(f"\n├ Total Trades: {total_trades}")
        if total_trades > 0:
            wr = wins / total_trades * 100 if total_trades > 0 else 0
            tg_lines.append(f"├ Win/Loss: {wins}/{losses} ({wr:.0f}%)")
            tg_lines.append(f"├ Realized PnL: ${total_pnl:+,.2f}")
        
        if all_open > 0:
            tg_lines.append(f"\n⚠ *{all_open} open position(s)* — risk active")
        else:
            tg_lines.append(f"\n✅ No open positions — flat")
        
        # SILENT (entry alerts only)
    
    # ── Save state ──
    state.last_run = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    if len(state.decision_log) > 100:
        state.decision_log = state.decision_log[-100:]
    save_state(state)
    
    return notifications


# ── Main ──

def main():
    """Cron entry point. Print nothing = no signal (silent). Print = delivery."""
    state = load_state()
    notifications = run_live_check(state)
    for n in notifications:
        print(n)
        print()


if __name__ == "__main__":
    main()
