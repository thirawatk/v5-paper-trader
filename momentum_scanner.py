#!/usr/bin/env python3
"""
Momentum Scanner — NYSE, NASDAQ, AMEX
======================================
Scans all 3 exchanges for momentum breakouts using MACD histogram.
Returns top-ranked stocks by momentum strength.
Runs on CT301, callable via MCP or cron.

Usage:
  python3 momentum_scanner.py --universe all --limit 50 --output /tmp/momentum_scan.json
  python3 momentum_scanner.py --universe nasdaq --limit 20
"""

import argparse, json, os, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from datetime import datetime
import yfinance as yf

# ── Config ──
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
MIN_VOLUME = 500_000          # Min daily volume
MIN_PRICE = 5.0               # Min price
BATCH_SIZE = 50               # yfinance batch size

# Universe files
UNIVERSE_FILES = {
    "sp500": "/root/.hermes/profiles/trader/scripts/sp500_universe.txt",
    "nasdaq": "/root/.hermes/profiles/trader/scripts/nasdaq100_universe.txt",
    "russell": "/root/.hermes/profiles/trader/scripts/russell2000_universe.txt",
}

def load_tickers(path):
    tks = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                tks.append(line.upper())
    return tks

def scan(universe="all", limit=50, min_volume=MIN_VOLUME):
    """Scan stocks for momentum breakouts. Returns sorted list of dicts."""
    
    # Collect tickers
    tickers = []
    if universe == "all":
        for path in UNIVERSE_FILES.values():
            if os.path.exists(path):
                tickers.extend(load_tickers(path))
        # Deduplicate
        tickers = list(dict.fromkeys(tickers))
    elif universe in UNIVERSE_FILES:
        tickers = load_tickers(UNIVERSE_FILES[universe])
    else:
        return {"error": f"Unknown universe: {universe}"}
    
    print(f"[momentum_scanner] Scanning {len(tickers)} tickers (universe={universe})...")
    
    # Fetch data in batches
    all_data = {}
    for i in range(0, len(tickers), BATCH_SIZE):
        batch = tickers[i:i+BATCH_SIZE]
        try:
            data = yf.download(
                " ".join(batch), period="6mo", progress=False,
                group_by="ticker", threads=True
            )
            if len(batch) == 1:
                df = data.copy()
                if not df.empty and len(df) > 50:
                    df.columns = df.columns.str.lower()
                    all_data[batch[0]] = df
            else:
                for sym in batch:
                    try:
                        df = data[sym].dropna(how="all")
                        if not df.empty and len(df) > 50:
                            df.columns = df.columns.str.lower()
                            all_data[sym] = df
                    except:
                        pass
        except Exception as e:
            print(f"  Batch error: {e}")
    
    print(f"  Loaded {len(all_data)} stocks with data")
    
    # Compute momentum scores
    results = []
    for sym, df in all_data.items():
        close = float(df["close"].iloc[-1])
        volume = float(df["volume"].iloc[-1])
        
        # Filters
        if close < MIN_PRICE: continue
        if volume < min_volume: continue
        
        # MACD
        ema12 = df["close"].ewm(span=MACD_FAST, adjust=False).mean()
        ema26 = df["close"].ewm(span=MACD_SLOW, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=MACD_SIGNAL, adjust=False).mean()
        hist = macd_line - signal_line
        
        hist_now = float(hist.iloc[-1])
        hist_prev = float(hist.iloc[-2]) if len(hist) > 1 else 0
        
        # EMA trend
        ema50 = df["close"].ewm(span=50, adjust=False).mean()
        ema200 = df["close"].ewm(span=200, adjust=False).mean()
        ema50_now = float(ema50.iloc[-1])
        ema200_now = float(ema200.iloc[-1])
        price_vs_50 = (close - ema50_now) / ema50_now * 100
        price_vs_200 = (close - ema200_now) / ema200_now * 100
        
        # Volume surge
        vol_20avg = df["volume"].iloc[-21:-1].mean()
        vol_ratio = volume / vol_20avg if vol_20avg > 0 else 1.0
        
        # ATR
        high, low = df["high"], df["low"]
        tr = pd.concat([
            high - low,
            (high - close).abs(),
            (low - close).abs()
        ], axis=1).max(axis=1)
        atr14 = tr.rolling(14).mean()
        atr_now = float(atr14.iloc[-1])
        atr_pct = atr_now / close * 100
        
        # Momentum score
        mom_score = 0.0
        
        # 1. MACD histogram
        if hist_now > 0 and hist_now > hist_prev:
            mom_score += min(3.0, hist_now * 5)
        elif hist_now > 0:
            mom_score += 1.0
        elif hist_now < 0 and hist_now < hist_prev:
            mom_score -= 2.0
        
        # 2. Histogram acceleration
        hist_accel = hist_now - hist_prev
        if hist_accel > 0:
            mom_score += min(2.0, hist_accel * 10)
        
        # 3. Trend alignment
        if close > ema50_now > ema200_now:
            mom_score += 2.0
        elif close > ema50_now:
            mom_score += 1.0
        elif close > ema200_now:
            mom_score += 0.5
        
        # 4. Volume surge
        if vol_ratio > 1.5:
            mom_score += 1.0
        elif vol_ratio > 1.2:
            mom_score += 0.5
        
        results.append({
            "ticker": sym,
            "price": round(close, 2),
            "momentum_score": round(mom_score, 2),
            "macd_hist": round(hist_now, 4),
            "hist_prev": round(hist_prev, 4),
            "hist_accel": round(hist_accel, 4),
            "price_vs_ema50": round(price_vs_50, 2),
            "price_vs_ema200": round(price_vs_200, 2),
            "volume_ratio": round(vol_ratio, 2),
            "atr_pct": round(atr_pct, 2),
            "trend": "bullish" if close > ema50_now > ema200_now else
                     "neutral" if close > ema200_now else "bearish",
        })
    
    results.sort(key=lambda x: x["momentum_score"], reverse=True)
    return results[:limit]


def main():
    parser = argparse.ArgumentParser(description="Momentum Scanner")
    parser.add_argument("--universe", default="all", choices=["all", "sp500", "nasdaq", "russell"])
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output", default=None)
    parser.add_argument("--min-volume", type=int, default=MIN_VOLUME)
    args = parser.parse_args()
    
    results = scan(universe=args.universe, limit=args.limit, min_volume=args.min_volume)
    
    if isinstance(results, dict) and "error" in results:
        print(f"ERROR: {results['error']}", file=sys.stderr)
        sys.exit(1)
    
    output = {
        "scan_time": datetime.now().isoformat(),
        "universe": args.universe,
        "total_scanned": len(results),
        "results": results,
    }
    
    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"  Saved {len(results)} results to {args.output}")
    else:
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
