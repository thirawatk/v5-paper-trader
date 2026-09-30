#!/usr/bin/env python3
"""
Backtest MACD+HA+VIX 3-way confluence across all US stocks (market cap > $50M).
Outputs results to CSV and summary.
"""

import yfinance as yf
import pandas as pd
import json
import sys
import time
from datetime import datetime, timedelta

FAST, SLOW, SIG = 12, 26, 9
MACD_THRESH = -0.5
VIX_THRESH = 20.0
FORWARD_DAYS = [5, 10, 20]
START_DATE = "2022-10-01"
END_DATE = "2026-07-01"


def compute_macd(close):
    ema_f = close.ewm(span=FAST, adjust=False).mean()
    ema_s = close.ewm(span=SLOW, adjust=False).mean()
    macd = ema_f - ema_s
    signal = macd.rolling(window=SIG).mean()
    hist = macd - signal
    return macd, signal, hist


def compute_ha(df):
    ha_close = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4
    ha_open = df["Open"].copy()
    ha_open.iloc[0] = (df["Open"].iloc[0] + df["Close"].iloc[0]) / 2
    for i in range(1, len(ha_open)):
        ha_open.iloc[i] = (ha_open.iloc[i - 1] + ha_close.iloc[i - 1]) / 2
    return ha_open, ha_close


def get_stock_list():
    """Get US stock tickers from multiple sources."""
    tickers = set()

    # S&P 500
    try:
        sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        tickers.update(sp500["Symbol"].tolist())
        print(f"  S&P 500: {len(sp500)} tickers")
    except Exception as e:
        print(f"  S&P 500 fetch failed: {e}")

    # NASDAQ
    try:
        nasdaq = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[4]
        tickers.update(nasdaq["Ticker"].tolist())
        print(f"  NASDAQ-100 added")
    except:
        pass

    # Russell 2000 subset — use a known list of large/mid caps
    # Add common large/mid cap tickers
    extra = [
        "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "VXUS", "VEA", "VWO", "BND",
        "ARKK", "XLF", "XLE", "XLK", "XLV", "XLI", "XLP", "XLY", "XLU", "XLB",
        "GLD", "SLV", "USO", "TLT", "HYG", "LQD", "EMB",
        "BRK-B", "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP",
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX", "AMD",
        "INTC", "CRM", "ADBE", "PYPL", "SQ", "SHOP", "SNOW", "PLTR", "COIN",
        "JNJ", "PFE", "UNH", "ABBV", "MRK", "LLY", "BMY", "AMGN", "GILD",
        "PG", "KO", "PEP", "WMT", "COST", "HD", "MCD", "NKE", "SBUX",
        "DIS", "CMCSA", "VZ", "T", "TMUS",
        "BA", "CAT", "HON", "UPS", "RTX", "LMT", "GD",
        "XOM", "CVX", "COP", "SLB", "EOG",
        "NEE", "DUK", "SO", "D", "AEP",
        "AMT", "PLD", "CCI", "SPG", "O",
        "TSM", "BABA", "PDD", "JD", "NIO", "XPEV", "LI",
        "SQ", "ROKU", "SNAP", "PINS", "UBER", "LYFT", "ABNB", "DASH",
        "RIVN", "LCID", "F", "GM", "RACE",
        "SOFI", "AFRM", "HOOD", "MARA", "RIOT", "MSTR",
    ]
    tickers.update(extra)

    # Clean tickers
    cleaned = set()
    for t in tickers:
        t = str(t).strip().upper().replace(".", "-")
        if t and len(t) <= 6 and not t.startswith("^"):
            cleaned.add(t)

    return sorted(cleaned)


def filter_by_market_cap(tickers, min_cap=50_000_000):
    """Filter tickers by market cap using yfinance."""
    print(f"\nFiltering {len(tickers)} tickers by market cap > ${min_cap/1e6:.0f}M...")
    passed = []
    failed = 0

    for i, sym in enumerate(tickers):
        if (i + 1) % 100 == 0:
            print(f"  Checked {i+1}/{len(tickers)} ({len(passed)} passed)...")
        try:
            t = yf.Ticker(sym)
            info = t.info
            cap = info.get("marketCap", 0) or 0
            if cap >= min_cap:
                passed.append(sym)
        except:
            failed += 1
            continue

    print(f"  Filtered: {len(passed)} stocks passed (market cap > ${min_cap/1e6:.0f}M), {failed} errors)")
    return passed


def run_backtest(tickers, vix_map):
    """Run backtest across all tickers."""
    results = []
    total = len(tickers)

    for i, sym in enumerate(tickers):
        if (i + 1) % 50 == 0:
            print(f"  Backtesting {i+1}/{total} ({len(results)} signals found)...")

        try:
            df = yf.Ticker(sym).history(start=START_DATE, end=END_DATE)
            if df.empty or len(df) < 100:
                continue

            macd, signal, hist = compute_macd(df["Close"])
            ha_open, ha_close = compute_ha(df)

            for j in range(1, len(hist)):
                if df.index[j].year < 2023:
                    continue

                crossed = hist.iloc[j - 1] < 0 and hist.iloc[j] >= 0
                if not crossed:
                    continue

                macd_val = macd.iloc[j]
                if macd_val >= MACD_THRESH:
                    continue

                ha_green = ha_close.iloc[j] > ha_open.iloc[j]
                if not ha_green:
                    continue

                # Check VIX
                date_str = df.index[j].strftime("%Y-%m-%d")
                vix_val = vix_map.get(date_str)
                if vix_val is None:
                    # Try prior days
                    for k in range(1, 6):
                        prev = (df.index[j] - timedelta(days=k)).strftime("%Y-%m-%d")
                        if prev in vix_map:
                            vix_val = vix_map[prev]
                            break
                if vix_val is None or vix_val < VIX_THRESH:
                    continue

                # All 4 conditions met — compute forward returns
                rets = {}
                max_dd = 0
                for d in FORWARD_DAYS:
                    if j + d < len(df):
                        rets[d] = ((df["Close"].iloc[j + d] - df["Close"].iloc[j]) / df["Close"].iloc[j]) * 100
                        window_low = df["Low"].iloc[j:j+d+1].min()
                        dd = ((window_low - df["Close"].iloc[j]) / df["Close"].iloc[j]) * 100
                        max_dd = min(max_dd, dd)
                    else:
                        rets[d] = None

                results.append({
                    "symbol": sym,
                    "date": date_str,
                    "close": round(df["Close"].iloc[j], 2),
                    "macd": round(macd_val, 4),
                    "vix": round(vix_val, 1),
                    "ret_5d": round(rets.get(5) or 0, 2),
                    "ret_10d": round(rets.get(10) or 0, 2),
                    "ret_20d": round(rets.get(20) or 0, 2),
                    "max_dd": round(max_dd, 2),
                })

        except Exception:
            continue

    return results


def main():
    print("=" * 80)
    print("  MACD + HA + VIX 3-Way Confluence — US Stocks Backtest 2023-2026")
    print("=" * 80)

    # 1. Get stock list
    print("\n[1/4] Fetching stock list...")
    tickers = get_stock_list()
    print(f"  Total unique tickers: {len(tickers)}")

    # 2. Fetch VIX data
    print("\n[2/4] Fetching VIX data...")
    vix_df = yf.Ticker("^VIX").history(start=START_DATE, end=END_DATE)
    vix_map = {}
    for idx in vix_df.index:
        vix_map[idx.strftime("%Y-%m-%d")] = vix_df.loc[idx, "Close"]
    print(f"  VIX data points: {len(vix_map)}")

    # 3. Filter by market cap
    print("\n[3/4] Filtering by market cap...")
    filtered = filter_by_market_cap(tickers, min_cap=50_000_000)

    # 4. Run backtest
    print(f"\n[4/4] Running backtest on {len(filtered)} stocks...")
    results = run_backtest(filtered, vix_map)

    # Output results
    print(f"\n{'=' * 80}")
    print(f"  RESULTS: {len(results)} confluence signals found")
    print(f"{'=' * 80}")

    if results:
        # Sort by date
        results.sort(key=lambda x: x["date"])

        # Print table
        print(f"\n  {'Date':<12} {'Symbol':<8} {'Close':>8} {'MACD':>8} {'VIX':>6} {'5d':>8} {'10d':>8} {'20d':>8} {'MaxDD':>8}")
        print(f"  {'-' * 80}")

        wins = 0
        for r in results:
            r20 = r["ret_20d"]
            icon = "✅" if r20 > 0 else "❌"
            if r20 > 0:
                wins += 1
            print(f"  {icon} {r['date']} {r['symbol']:<8} ${r['close']:>7.2f} {r['macd']:>+8.2f} {r['vix']:>5.1f} {r['ret_5d']:>+7.2f}% {r['ret_10d']:>+7.2f}% {r['ret_20d']:>+7.2f}% {r['max_dd']:>+7.2f}%")

        # Summary
        print(f"\n  {'SUMMARY':=^60}")
        print(f"  Total signals: {len(results)}")
        print(f"  Wins (20d): {wins} | Losses: {len(results) - wins}")
        print(f"  Win rate: {wins / len(results) * 100:.0f}%")

        avg_5 = sum(r["ret_5d"] for r in results) / len(results)
        avg_10 = sum(r["ret_10d"] for r in results) / len(results)
        avg_20 = sum(r["ret_20d"] for r in results) / len(results)
        avg_dd = sum(r["max_dd"] for r in results) / len(results)
        print(f"  Avg 5d: {avg_5:+.2f}% | 10d: {avg_10:+.2f}% | 20d: {avg_20:+.2f}%")
        print(f"  Avg Max DD: {avg_dd:+.2f}%")

        # By year
        for year in sorted(set(r["date"][:4] for r in results)):
            yr = [r for r in results if r["date"].startswith(str(year))]
            yr_wins = sum(1 for r in yr if r["ret_20d"] > 0)
            print(f"  {year}: {len(yr)} signals, {yr_wins}/{len(yr)} wins ({yr_wins/len(yr)*100:.0f}%)")

        # Save CSV
        csv_path = "/root/.hermes/profiles/trader/scripts/backtest_results.csv"
        pd.DataFrame(results).to_csv(csv_path, index=False)
        print(f"\n  Results saved to {csv_path}")
    else:
        print("  No confluence signals found in this period.")


if __name__ == "__main__":
    main()
