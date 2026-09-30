#!/usr/bin/env python3
"""
Coin Selection Analyzers for Hyperliquid Paper Trader
=======================================================
Scans the full perp market and ranks coins by multiple criteria.
Each analyzer returns a score (-10 to +10) for every coin.
CompositeSelector aggregates them and picks the top candidates.

Usage:
  python3 coin_analyzers.py scan --top 5
  python3 coin_analyzers.py scan --analyzers momentum,funding,oi --min-score 3
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

# ── Hyperliquid data layer ──
_hl_dir = "/root/.hermes/profiles/trader/skills/hyperliquid/scripts"
if _hl_dir not in sys.path:
    sys.path.insert(0, _hl_dir)
from hyperliquid_client import (
    _post_info, _normalize_candles, _normalize_perp_markets,
    _normalize_funding_history, _hours_ago_ms, _safe_float,
)

# ── Import existing V2 indicators for spot-check ──
sys.path.insert(0, "/root/.hermes/profiles/trader/scripts")
from poc_paper_trader_v2 import (
    calculate_vwap, calculate_obv, calculate_cmf, calculate_mfi,
    detect_trend, calculate_volume_profile, fetch_funding_sentiment,
    get_candle_signal, calculate_confluence, IndicatorSnapshot,
)


# ═══════════════════════════════════════════════
# Data Types
# ═══════════════════════════════════════════════

@dataclass
class CoinProfile:
    """Scanned data snapshot for one coin"""
    coin: str = ""
    mark_px: float = 0.0
    prev_day_px: float = 0.0
    change_pct: float = 0.0
    day_ntl_vlm: float = 0.0          # 24h notional volume in USD
    day_base_vlm: float = 0.0         # 24h base volume
    funding_rate: float = 0.0
    open_interest: float = 0.0
    max_leverage: int = 50
    sz_decimals: int = 0
    
    # Computed
    atr_pct: float = 0.0              # ATR as % of price
    volume_rank: float = 0.0          # Percentile rank 0-1
    oi_change_pct: float = 0.0        # OI change vs 1h ago (requires cache)
    momentum_score: float = 0.0       # Price rate of change score
    vp_quality: float = 0.0           # Volume profile concentration
    btc_corr: float = 0.0             # Correlation with BTC
    is_tradeable: bool = True         # Minimum liquidity gate
    dex: str = "main"                 # DEX source: 'main' (crypto) or 'xyz' (equity/commodity/index)


@dataclass
class AnalyzerResult:
    """Output of a single analyzer"""
    name: str = ""
    scores: Dict[str, float] = field(default_factory=dict)  # coin -> score
    direction: Dict[str, str] = field(default_factory=dict)  # coin -> long/short/none
    details: str = ""


@dataclass
class CompositeResult:
    """Final coin selection output"""
    timestamp: str = ""
    ranked_coins: List[Dict[str, Any]] = field(default_factory=list)  # ordered by composite score
    analyzer_results: List[AnalyzerResult] = field(default_factory=list)
    total_coins_scanned: int = 0
    tradeable_coins: int = 0


# ═══════════════════════════════════════════════
# Data Fetching
# ═══════════════════════════════════════════════

def fetch_all_markets() -> List[Dict[str, Any]]:
    """Fetch all perp markets from the main Hyperliquid DEX (crypto)"""
    payload2 = {"type": "metaAndAssetCtxs"}
    raw2 = _safe_info_query(payload2)
    return _normalize_perp_markets(raw2)


def fetch_xyz_markets() -> List[Dict[str, Any]]:
    """
    Fetch all XYZ (equity/commodity/index/forex) perp markets from 
    the Trade.xyz HIP-3 DEX on Hyperliquid.
    
    Uses the same metaAndAssetCtxs endpoint with dex='xyz'.
    Returns data in the same normalized format as fetch_all_markets().
    Coin names are prefixed with 'xyz:' (e.g. 'xyz:NVDA', 'xyz:SP500').
    """
    payload = {"type": "metaAndAssetCtxs", "dex": "xyz"}
    raw = _safe_info_query(payload)
    return _normalize_perp_markets(raw)


def fetch_unified_markets(include_xyz: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch markets from main DEX, optionally merged with XYZ DEX.
    Returns unified list with 'dex' field added to each market row.
    """
    markets = fetch_all_markets()
    for m in markets:
        m["dex"] = "main"
    
    if include_xyz:
        try:
            xyz_markets = fetch_xyz_markets()
            for m in xyz_markets:
                m["dex"] = "xyz"
            markets.extend(xyz_markets)
        except Exception:
            pass  # XYZ fetch failure = non-fatal, continue with crypto only
    
    return markets


def _safe_info_query(payload: Dict[str, Any]) -> Any:
    """Safe query with retry"""
    return _post_info(payload)


def fetch_candles_fast(coin: str, interval: str = "1h", hours: float = 48) -> List[Dict[str, Any]]:
    """Fetch candles for a coin (fewer hours for scan speed)"""
    end_ms = int(time.time() * 1000)
    start_ms = _hours_ago_ms(hours, end_ms)
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": interval,
            "startTime": start_ms,
            "endTime": end_ms,
        },
    }
    raw = _safe_info_query(payload)
    return _normalize_candles(raw)


# ═══════════════════════════════════════════════
# Liquidity Gate (fast filter)
# ═══════════════════════════════════════════════

def is_tradeable(row: Dict[str, Any], min_volume: float = 100_000) -> bool:
    """Minimum liquidity check — must not be delisted, minimum volume"""
    if row.get("is_delisted", False):
        return False
    vol = _safe_float(row.get("day_ntl_vlm")) or 0
    return vol >= min_volume


# ═══════════════════════════════════════════════
# Analyzer: Momentum / Volume Score
# ═══════════════════════════════════════════════

def analyze_momentum(profiles: Dict[str, CoinProfile]) -> AnalyzerResult:
    """
    Score coins by: price change + volume momentum.
    High momentum = trending hard. Zero = dead.
    """
    result = AnalyzerResult(name="momentum")
    
    # Gather metrics for percentile ranking
    abs_changes = [(c.coin, abs(c.change_pct)) for c in profiles.values()]
    volumes = [(c.coin, c.day_ntl_vlm) for c in profiles.values()]
    
    for coin, profile in profiles.items():
        score = 0.0
        direction = "none"
        
        # Price change component (-5 to +5)
        cp = profile.change_pct
        if cp > 10:
            score += 5.0
        elif cp > 5:
            score += 4.0
        elif cp > 2:
            score += 3.0
        elif cp > 1:
            score += 2.0
        elif cp > 0.5:
            score += 1.0
        elif cp < -10:
            score -= 5.0
        elif cp < -5:
            score -= 4.0
        elif cp < -2:
            score -= 3.0
        elif cp < -1:
            score -= 2.0
        elif cp < -0.5:
            score -= 1.0
        
        # Volume component (0 to +5 based on percentile)
        day_vol = profile.day_ntl_vlm
        if volumes:
            vol_vals = [v for _, v in volumes if v > 0]
            if vol_vals:
                # Percentile rank
                below = sum(1 for v in vol_vals if v < day_vol)
                pctile = below / len(vol_vals) if vol_vals else 0.5
                score += pctile * 5.0  # 0-5
        
        # Direction
        if cp > 1:
            direction = "long"
        elif cp < -1:
            direction = "short"
        
        result.scores[coin] = score
        result.direction[coin] = direction
    
    result.details = f"Momentum scored {len(result.scores)} coins"
    return result


# ═══════════════════════════════════════════════
# Analyzer: Funding Rate Divergence
# ═══════════════════════════════════════════════

def analyze_funding(profiles: Dict[str, CoinProfile]) -> AnalyzerResult:
    """
    Score coins by funding rate.
    Extreme funding = potential reversal (contrarian).
    Moderate aligned funding = trend confirmation.
    """
    result = AnalyzerResult(name="funding")
    
    for coin, profile in profiles.items():
        score = 0.0
        direction = "none"
        fr = profile.funding_rate
        
        # Contrarian at extremes
        if fr > 0.001:  # >0.1% = extremely overleveraged longs
            score = -4.0
            direction = "short"
        elif fr > 0.0005:
            score = -2.0
            direction = "short"
        elif fr > 0.0002:
            score = -0.5
            direction = "short"
        elif fr < -0.001:  # >0.1% negative = extremely short
            score = 4.0
            direction = "long"
        elif fr < -0.0005:
            score = 2.0
            direction = "long"
        elif fr < -0.0002:
            score = 0.5
            direction = "long"
        
        result.scores[coin] = score
        result.direction[coin] = direction
    
    result.details = f"Funding scored {len(result.scores)} coins"
    return result


# ═══════════════════════════════════════════════
# Analyzer: Open Interest Change
# ═══════════════════════════════════════════════

def analyze_open_interest(profiles: Dict[str, CoinProfile]) -> AnalyzerResult:
    """
    Score coins by OI level.
    High OI = institutional interest, but not over-extended.
    Note: We don't have OI history in the scan, so use absolute OI as proxy
    and infer from market context.
    """
    result = AnalyzerResult(name="open_interest")
    
    # Get OI percentile
    oi_vals = [p.open_interest for p in profiles.values() if p.open_interest > 0]
    
    for coin, profile in profiles.items():
        score = 0.0
        direction = "none"
        oi = profile.open_interest
        
        if oi_vals:
            below = sum(1 for v in oi_vals if v < oi)
            pctile = below / len(oi_vals)
            
            # Mid-range OI is ideal (some interest but not crowded)
            # Very low OI (<20th pctile) = not interesting
            # Very high OI (>90th pctile) = crowded
            if 0.3 <= pctile <= 0.8:
                score = 2.0
            elif pctile > 0.9:
                score = -1.0  # Crowded
            elif pctile < 0.2:
                score = -2.0  # No interest
        
        result.scores[coin] = score
        result.direction[coin] = direction
    
    result.details = f"OI scored {len(result.scores)} coins"
    return result


# ═══════════════════════════════════════════════
# Analyzer: Volatility / ATR
# ═══════════════════════════════════════════════

def analyze_volatility(profiles: Dict[str, CoinProfile]) -> AnalyzerResult:
    """
    Score by price volatility.
    Too low = no movement to capture.
    Too high = unpredictable, wide stops.
    Sweet spot: 1-5% daily range.
    """
    result = AnalyzerResult(name="volatility")
    
    for coin, profile in profiles.items():
        score = 0.0
        direction = "none"
        
        # Use change_pct as rough volatility proxy
        abs_cp = abs(profile.change_pct) if profile.change_pct else 0
        
        if 1.0 <= abs_cp <= 5.0:
            score = 3.0  # Sweet spot
        elif 5.0 < abs_cp <= 10.0:
            score = 1.0  # Hot but manageable
        elif 0.5 <= abs_cp < 1.0:
            score = 1.0  # Low but okay
        elif abs_cp > 10.0:
            score = -2.0  # Too wild
        elif abs_cp < 0.5:
            score = -3.0  # Dead
        
        result.scores[coin] = score
        result.direction[coin] = direction
    
    result.details = f"Volatility scored {len(result.scores)} coins"
    return result


# ═══════════════════════════════════════════════
# Analyzer: Liquidity Depth
# ═══════════════════════════════════════════════

def analyze_liquidity(profiles: Dict[str, CoinProfile]) -> AnalyzerResult:
    """
    Score by absolute dollar volume.
    Higher = easier to enter/exit without slippage.
    """
    result = AnalyzerResult(name="liquidity")
    
    vol_vals = [p.day_ntl_vlm for p in profiles.values() if p.day_ntl_vlm > 0]
    
    for coin, profile in profiles.items():
        score = 0.0
        vol = profile.day_ntl_vlm
        
        if vol >= 10_000_000:
            score = 3.0  # Top tier liquidity
        elif vol >= 3_000_000:
            score = 2.0  # Good
        elif vol >= 1_000_000:
            score = 1.0  # Adequate
        elif vol >= 500_000:
            score = 0.5  # Minimum
        else:
            score = -2.0  # Too thin
        
        result.scores[coin] = profile.coin if not hasattr(profile, 'coin') else coin
        result.scores[coin] = score
        result.direction[coin] = "none"
    
    result.details = f"Liquidity scored {len(result.scores)} coins"
    return result


# ═══════════════════════════════════════════════
# Analyzer: Correlation Divergence (comparative)
# ═══════════════════════════════════════════════

def analyze_correlation_divergence(
    profiles: Dict[str, CoinProfile],
    candle_cache: Dict[str, List[Dict[str, Any]]],
) -> AnalyzerResult:
    """
    Score coins that move independently of their market baseline.
    Main DEX → BTC baseline; XYZ DEX → SP500/XYZ100 baseline.
    Low correlation = more alpha potential.
    """
    result = AnalyzerResult(name="correlation")
    
    # ── Determine baselines ──
    btc_candles = candle_cache.get("BTC", [])
    xyz_baseline_candles = candle_cache.get("xyz:SP500") or candle_cache.get("xyz:XYZ100") or []
    
    def _get_returns(candles: List[Dict], max_n: int = 50) -> List[float]:
        returns = []
        n = min(max_n, len(candles))
        for i in range(1, n):
            prev = _safe_float(candles[i-1].get("close"))
            curr = _safe_float(candles[i].get("close"))
            if prev and curr and prev > 0:
                returns.append((curr - prev) / prev)
        return returns
    
    def _calc_pearson(a: List[float], b: List[float]) -> float:
        n = min(len(a), len(b))
        if n < 10:
            return 0.0
        a_r = a[-n:]; b_r = b[-n:]
        mean_a = sum(a_r) / n; mean_b = sum(b_r) / n
        num = sum((x - mean_a) * (y - mean_b) for x, y in zip(a_r, b_r))
        den_a = math.sqrt(sum((x - mean_a)**2 for x in a_r))
        den_b = math.sqrt(sum((y - mean_b)**2 for y in b_r))
        return num / (den_a * den_b) if den_a * den_b > 0 else 0.0
    
    btc_returns = _get_returns(btc_candles) if len(btc_candles) >= 20 else []
    xyz_baseline_returns = _get_returns(xyz_baseline_candles) if len(xyz_baseline_candles) >= 20 else []
    
    for coin, profile in profiles.items():
        score = 0.0
        coin_candles = candle_cache.get(coin, [])
        is_xyz = profile.dex == "xyz"
        is_baseline = coin in ("BTC", "xyz:SP500", "xyz:XYZ100")
        
        if is_baseline or len(coin_candles) < 20:
            result.scores[coin] = 0.0
            result.direction[coin] = "none"
            continue
        
        # Pick baseline based on DEX
        if is_xyz and xyz_baseline_returns:
            baseline_returns = xyz_baseline_returns
        elif not is_xyz and btc_returns:
            baseline_returns = btc_returns
        else:
            result.scores[coin] = 0.0
            result.direction[coin] = "none"
            continue
        
        coin_returns = _get_returns(coin_candles)
        if len(coin_returns) < 10:
            result.scores[coin] = 0.0
            result.direction[coin] = "none"
            continue
        
        corr = _calc_pearson(baseline_returns, coin_returns)
        
        # Score: low absolute correlation = more alpha potential
        abs_corr = abs(corr)
        if abs_corr < 0.3:
            score = 3.0  # Independent mover = alpha
        elif abs_corr < 0.5:
            score = 1.5
        elif abs_corr < 0.7:
            score = 0.0
        elif abs_corr < 0.85:
            score = -1.0  # Tight follower
        else:
            score = -2.0  # Clone
        
        # Bonus: divergence (coin up while baseline down)
        if corr < 0 and profile.change_pct:
            recent_baseline = sum(baseline_returns[-5:]) / 5 if len(baseline_returns) >= 5 else 0
            if profile.change_pct > 1 and recent_baseline < -0.5:
                score += 2.0  # Strong alpha signal
        
        result.scores[coin] = score
        result.direction[coin] = "long" if score > 1 else "short" if score < -1 else "none"
    
    result.details = f"Correlation scored {len(result.scores)} coins"
    return result


# ═══════════════════════════════════════════════
# Analyzer: Volume Profile Quality (deeper scan)
# ═══════════════════════════════════════════════

def analyze_vp_quality(
    profiles: Dict[str, CoinProfile],
    candle_cache: Dict[str, List[Dict[str, Any]]],
) -> AnalyzerResult:
    """
    Score coins by Volume Profile structure quality.
    Clean POC with clear value area = easier to trade.
    Scattered VP = unreliable levels.
    """
    result = AnalyzerResult(name="vp_quality")
    
    for coin, profile in profiles.items():
        candles = candle_cache.get(coin, [])
        score = 0.0
        
        if len(candles) < 50:
            result.scores[coin] = 0.0
            result.direction[coin] = "none"
            continue
        
        vp = calculate_volume_profile(candles[-100:])
        if vp is None:
            result.scores[coin] = 0.0
            result.direction[coin] = "none"
            continue
        
        # Concentration: higher = cleaner
        if vp.concentration > 0.25:
            score = 3.0
        elif vp.concentration > 0.18:
            score = 2.0
        elif vp.concentration > 0.12:
            score = 1.0
        elif vp.concentration > 0.08:
            score = 0.0
        else:
            score = -2.0  # Scattered
        
        # Bonus: price near POC = potential retest setup
        close = _safe_float(candles[-1].get("close")) or 0
        if vp.poc > 0:
            dist = abs(close - vp.poc) / vp.poc
            if dist < 0.01:
                score += 1.0  # At POC = ready for move
        
        result.scores[coin] = score
        result.direction[coin] = "none"
    
    result.details = f"VP quality scored {len(result.scores)} coins"
    return result


# ═══════════════════════════════════════════════
# Composite Coin Selector
# ═══════════════════════════════════════════════

@dataclass
class SelectorConfig:
    """Configuration for coin selection"""
    top_n: int = 5                      # How many coins to return
    min_total_score: float = -5.0       # Minimum composite to include
    max_correlation_within_set: float = 0.7  # Don't pick correlated coins together
    min_volume: float = 100_000         # Minimum 24h volume
    max_coins_returned: int = 3         # How many actually get fed to trader
    include_xyz: bool = False           # Include Trade.xyz equity/commodity/index markets
    analyzer_weights: Dict[str, float] = field(default_factory=lambda: {
        "momentum": 2.0,
        "funding": 1.5,
        "open_interest": 1.0,
        "volatility": 1.5,
        "liquidity": 1.0,
        "correlation": 1.5,
        "vp_quality": 1.5,
    })


def select_coins(config: Optional[SelectorConfig] = None) -> CompositeResult:
    """
    Full coin selection pipeline:
    1. Fetch all markets (fast metadata scan)
    2. Apply liquidity gate
    3. Run all analyzers
    4. Composite score and rank
    5. De-duplicate correlated coins
    """
    if config is None:
        config = SelectorConfig()
    
    result = CompositeResult()
    result.timestamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    
    # Step 1: Fetch all markets (crypto + optionally XYZ)
    markets = fetch_unified_markets(include_xyz=config.include_xyz)
    result.total_coins_scanned = len(markets)
    
    # Step 2: Build profiles + liquidity gate
    profiles: Dict[str, CoinProfile] = {}
    for row in markets:
        coin = row.get("coin", "")
        if not coin or row.get("is_delisted", False):
            continue
        
        vol = _safe_float(row.get("day_ntl_vlm")) or 0
        if vol < config.min_volume:
            continue
        
        profile = CoinProfile(
            coin=coin,
            mark_px=_safe_float(row.get("mark_px")) or 0.0,
            prev_day_px=_safe_float(row.get("prev_day_px")) or 0.0,
            change_pct=_safe_float(row.get("change_pct")) or 0.0,
            day_ntl_vlm=vol,
            day_base_vlm=_safe_float(row.get("day_base_vlm")) or 0.0,
            funding_rate=_safe_float(row.get("funding")) or 0.0,
            open_interest=_safe_float(row.get("open_interest")) or 0.0,
            max_leverage=row.get("max_leverage", 50),
            is_tradeable=True,
            dex=row.get("dex", "main"),
        )
        profiles[coin] = profile
    
    result.tradeable_coins = len(profiles)
    
    if len(profiles) < 2:
        result.ranked_coins = [{"coin": "BTC", "composite_score": 0, "direction": "none"}]
        return result
    
    # Step 3: Fetch candle data for deeper analyzers (top volume coins only)
    # Only scan the top 15 by volume + BTC for correlation
    vol_sorted = sorted(profiles.values(), key=lambda p: p.day_ntl_vlm, reverse=True)
    deep_scan_coins = [p.coin for p in vol_sorted[:20]]
    if "BTC" not in deep_scan_coins:
        deep_scan_coins.append("BTC")
    
    # If XYZ markets are included, also fetch SP500/XYZ100 as baseline
    if config.include_xyz:
        for baseline in ["xyz:SP500", "xyz:XYZ100"]:
            if baseline in profiles and baseline not in deep_scan_coins:
                deep_scan_coins.append(baseline)
    
    candle_cache: Dict[str, List[Dict[str, Any]]] = {}
    for coin in deep_scan_coins:
        try:
            candles = fetch_candles_fast(coin, "1h", 48)
            if len(candles) >= 20:
                candle_cache[coin] = candles
        except Exception:
            pass
    
    # Step 4: Run all analyzers
    momentum_result = analyze_momentum(profiles)
    funding_result = analyze_funding(profiles)
    oi_result = analyze_open_interest(profiles)
    vol_result = analyze_volatility(profiles)
    liq_result = analyze_liquidity(profiles)
    corr_result = analyze_correlation_divergence(profiles, candle_cache)
    vp_result = analyze_vp_quality(profiles, candle_cache)
    
    result.analyzer_results = [
        momentum_result, funding_result, oi_result,
        vol_result, liq_result, corr_result, vp_result,
    ]
    
    # Step 5: Composite score
    all_analyzer_names = [a.name for a in result.analyzer_results]
    coin_composites: Dict[str, Dict[str, Any]] = {}
    
    for coin in profiles:
        total = 0.0
        total_weight = 0.0
        breakdown = {}
        direction_votes: Dict[str, float] = {"long": 0.0, "short": 0.0, "none": 0.0}
        
        for ar in result.analyzer_results:
            weight = config.analyzer_weights.get(ar.name, 1.0)
            score = ar.scores.get(coin, 0.0)
            total += score * weight
            total_weight += weight
            breakdown[ar.name] = round(score, 2)
            
            dir_vote = ar.direction.get(coin, "none")
            direction_votes[dir_vote] = direction_votes.get(dir_vote, 0) + weight
        
        composite = total / total_weight if total_weight > 0 else 0
        
        # Direction from weighted votes — only count analyzers that gave a signal
        directional_weight = direction_votes["long"] + direction_votes["short"]
        if directional_weight > 0 and direction_votes["long"] / directional_weight > 0.55:
            direction = "long"
        elif directional_weight > 0 and direction_votes["short"] / directional_weight > 0.55:
            direction = "short"
        else:
            direction = "none"
        
        coin_composites[coin] = {
            "coin": coin,
            "price": profiles[coin].mark_px,
            "composite_score": round(composite, 2),
            "direction": direction,
            "change_pct": profiles[coin].change_pct,
            "volume_24h": profiles[coin].day_ntl_vlm,
            "funding_rate": profiles[coin].funding_rate,
            "open_interest": profiles[coin].open_interest,
            "breakdown": breakdown,
        }
    
    # Step 6: Rank by composite score
    ranked = sorted(coin_composites.values(), key=lambda x: abs(x["composite_score"]), reverse=True)
    
    # Step 7: De-duplicate correlated coins
    selected = []
    for candidate in ranked:
        if len(selected) >= config.max_coins_returned:
            break
        
        score = candidate["composite_score"]
        if score < config.min_total_score:
            continue
        
        # Check correlation with already selected
        too_correlated = False
        for sel in selected:
            if candidate["coin"] in candle_cache and sel["coin"] in candle_cache:
                c_can = candle_cache.get(candidate["coin"], [])
                c_sel = candle_cache.get(sel["coin"], [])
                if len(c_can) >= 15 and len(c_sel) >= 15:
                    # Quick correlation check
                    can_close = [_safe_float(c.get("close")) for c in c_can[-15:]]
                    sel_close = [_safe_float(c.get("close")) for c in c_sel[-15:]]
                    can_close = [c for c in can_close if c]
                    sel_close = [c for c in sel_close if c]
                    if len(can_close) >= 10 and len(sel_close) >= 10:
                        n = min(len(can_close), len(sel_close))
                        can_r = [(can_close[i] - can_close[i-1]) / can_close[i-1] for i in range(1, n)]
                        sel_r = [(sel_close[i] - sel_close[i-1]) / sel_close[i-1] for i in range(1, n)]
                        if can_r and sel_r:
                            m_c = sum(can_r) / len(can_r)
                            m_s = sum(sel_r) / len(sel_r)
                            num = sum((a - m_c) * (b - m_s) for a, b in zip(can_r, sel_r))
                            d_a = math.sqrt(sum((a - m_c) ** 2 for a in can_r))
                            d_b = math.sqrt(sum((b - m_s) ** 2 for b in sel_r))
                            corr = num / (d_a * d_b) if d_a * d_b > 0 else 0
                            if abs(corr) > config.max_correlation_within_set:
                                too_correlated = True
                                break
        
        if not too_correlated:
            selected.append(candidate)
    
    # If we got nothing, return top coin
    if not selected and ranked:
        selected = [ranked[0]]
    
    result.ranked_coins = selected
    return result


# ═══════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════

def render_result(result: CompositeResult) -> str:
    """Renders composite result to readable string"""
    lines = [
        f"┌─ COIN SELECTION REPORT ─────────────────────",
        f"│ Scan: {result.timestamp}",
        f"│ Scanned: {result.total_coins_scanned} total → {result.tradeable_coins} tradeable",
        f"└─────────────────────────────────────────────",
        "",
    ]
    
    if not result.ranked_coins:
        lines.append("No tradeable coins found.")
        return "\n".join(lines)
    
    # Ranked coins table
    lines.append("  Rank │ Coin          │ Score  │ Dir  │ 24h Chg  │ Volume     │ Funding")
    lines.append("  ─────┼───────────────┼────────┼──────┼──────────┼────────────┼─────────")
    
    for i, c in enumerate(result.ranked_coins):
        coin = c["coin"].ljust(13)
        score = f"{c['composite_score']:+.1f}".rjust(6)
        direction = c["direction"].ljust(6).upper()
        chg = f"{c['change_pct']:+.2f}%".rjust(8) if c["change_pct"] else "    N/A"
        vol = f"${c['volume_24h']/1e6:.1f}M".rjust(10)
        funding = f"{c['funding_rate']*100:.4f}%".rjust(7)
        lines.append(f"  #{i+1:<4} │ {coin} │ {score} │ {direction} │ {chg} │ {vol} │ {funding}")
    
    # Per-analyzer breakdown for top coins
    lines.append("")
    lines.append("  ── Analyzer Breakdown (top coins) ──")
    
    for c in result.ranked_coins:
        lines.append(f"")
        lines.append(f"  {c['coin']} (score: {c['composite_score']:+.1f}, dir: {c['direction'].upper()}):")
        bd = c.get("breakdown", {})
        for name, score in sorted(bd.items(), key=lambda x: abs(x[1]), reverse=True):
            bar = "█" * min(20, max(0, int(score * 3))) if score > 0 else "░" * min(20, max(0, int(abs(score) * 3)))
            lines.append(f"    {name:<15s} {score:+.2f} {bar}")
    
    lines.append("")
    return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Coin Selection Analyzers")
    parser.add_argument("action", nargs="?", default="scan", help="scan (default)")
    parser.add_argument("--top", type=int, default=5, help="Top N coins to return")
    parser.add_argument("--min-score", type=float, default=-5.0)
    parser.add_argument("--xyz", action="store_true", help="Include Trade.xyz equity/commodity/index/forex markets")
    parser.add_argument("--json", action="store_true")
    
    args = parser.parse_args()
    
    config = SelectorConfig(
        top_n=args.top,
        min_total_score=args.min_score,
        max_coins_returned=args.top,
        include_xyz=args.xyz,
    )
    
    result = select_coins(config)
    
    if args.json:
        # Convert for JSON serialization
        output = {
            "timestamp": result.timestamp,
            "total_scanned": result.total_coins_scanned,
            "tradeable": result.tradeable_coins,
            "ranked": result.ranked_coins,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print(render_result(result))


if __name__ == "__main__":
    main()
