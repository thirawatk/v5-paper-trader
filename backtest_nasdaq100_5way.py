#!/usr/bin/env python3
"""Backtest 5-way confluence: MACD crossover + MACD depth + HA green + VIX fear + EMA golden cross."""

import yfinance as yf
import pandas as pd
import sys
from datetime import datetime, timedelta

FAST, SLOW, SIG = 12, 26, 9
MACD_THRESH = -0.5
VIX_THRESH = 20.0
EMA_FAST = 50
EMA_SLOW = 200
FORWARD_DAYS = [5, 10, 20]
START_DATE = "2022-01-01"  # Need extra data for EMA 200 warmup
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


def compute_ema_cross(close, fast=50, slow=200):
    """Compute EMA 50/200 and detect golden cross."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    return ema_fast, ema_slow


def detect_ema_golden_cross(ema_fast, ema_slow, idx):
    """Check if EMA golden cross happened within the last N days."""
    # Exact same day
    if ema_fast.iloc[idx] > ema_slow.iloc[idx] and ema_fast.iloc[idx - 1] <= ema_slow.iloc[idx - 1]:
        return True
    return False


def detect_ema_above(ema_fast, ema_slow, idx):
    """Check if EMA 50 is above EMA 200 (in uptrend)."""
    return ema_fast.iloc[idx] > ema_slow.iloc[idx]


def get_nasdaq100():
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
        for table in tables:
            for col in table.columns:
                col_lower = str(col).lower()
                if 'ticker' in col_lower or 'symbol' in col_lower:
                    tickers = table[col].dropna().tolist()
                    if len(tickers) > 50:
                        cleaned = []
                        for t in tickers:
                            t = str(t).strip().upper().replace(".", "-")
                            if t and len(t) <= 6:
                                cleaned.append(t)
                        return cleaned
    except Exception as e:
        print(f"  Wikipedia fetch failed: {e}")

    return [
        "AAPL", "ABNB", "ADBE", "ADI", "ADP", "ADSK", "AEP", "AMAT", "AMD",
        "AMGN", "AMZN", "ANSS", "APP", "ARM", "ASML", "AVGO", "AZN", "BIIB",
        "BKNG", "BKR", "CDNS", "CDW", "CEG", "CHTR", "CMCSA", "COST", "CPRT",
        "CRWD", "CSCO", "CTAS", "CTSH", "DASH", "DDOG", "DLTR", "DXCM", "EA",
        "EXC", "FANG", "FAST", "FTNT", "GEHC", "GFS", "GILD", "GOOG", "GOOGL",
        "HON", "IDXX", "ILMN", "INTC", "INTU", "ISRG", "KDP", "KHC", "KLAC",
        "LRCX", "LULU", "MAR", "MCHP", "MDB", "MDLZ", "MELI", "META", "MNST",
        "MRNA", "MRVL", "MSFT", "MU", "NFLX", "NVDA", "NXPI", "ODFL", "ON",
        "ORLY", "PANW", "PAYX", "PCAR", "PDD", "PEP", "PYPL", "QCOM", "REGN",
        "ROST", "SBUX", "SNPS", "TEAM", "TMUS", "TSLA", "TTD", "TTWO", "TXN",
        "VRSK", "VRTX", "WBD", "WDAY", "XEL", "ZS"
    ]


def main():
    print("=" * 90)
    print("  5-Way Confluence — Nasdaq 100 Backtest 2023-2026")
    print("  MACD cross + MACD depth + HA green + VIX fear + EMA golden cross")
    print("=" * 90)

    print("\n[1/3] Fetching Nasdaq 100 list...")
    tickers = get_nasdaq100()
    print(f"  Tickers: {len(tickers)}")

    print("\n[2/3] Fetching VIX data...")
    vix_df = yf.Ticker("^VIX").history(start=START_DATE, end=END_DATE)
    vix_map = {}
    for idx in vix_df.index:
        vix_map[idx.strftime("%Y-%m-%d")] = vix_df.loc[idx, "Close"]
    print(f"  VIX data points: {len(vix_map)}")

    print(f"\n[3/3] Running backtest on {len(tickers)} stocks...")
    results = []
    skipped_no_ema = 0

    for i, sym in enumerate(tickers):
        if (i + 1) % 25 == 0:
            print(f"  Progress: {i+1}/{len(tickers)} ({len(results)} signals)...")

        try:
            df = yf.Ticker(sym).history(start=START_DATE, end=END_DATE)
            if df.empty or len(df) < 250:  # Need 200+ bars for EMA 200
                skipped_no_ema += 1
                continue

            macd, signal, hist = compute_macd(df["Close"])
            ha_open, ha_close = compute_ha(df)
            ema_fast, ema_slow = compute_ema_cross(df["Close"], EMA_FAST, EMA_SLOW)

            for j in range(200, len(hist)):  # Start after EMA 200 warmup
                if df.index[j].year < 2023:
                    continue

                # Condition 1: MACD crossover
                crossed = hist.iloc[j - 1] < 0 and hist.iloc[j] >= 0
                if not crossed:
                    continue

                # Condition 2: MACD depth
                macd_val = macd.iloc[j]
                if macd_val >= MACD_THRESH:
                    continue

                # Condition 3: HA green
                ha_green = ha_close.iloc[j] > ha_open.iloc[j]
                if not ha_green:
                    continue

                # Condition 4: VIX fear
                date_str = df.index[j].strftime("%Y-%m-%d")
                vix_val = vix_map.get(date_str)
                if vix_val is None:
                    for k in range(1, 6):
                        prev = (df.index[j] - timedelta(days=k)).strftime("%Y-%m-%d")
                        if prev in vix_map:
                            vix_val = vix_map[prev]
                            break
                if vix_val is None or vix_val < VIX_THRESH:
                    continue

                # Condition 5: EMA golden cross (within last 5 trading days)
                golden_cross = False
                for lookback in range(0, 6):
                    if j - lookback < 200:
                        continue
                    if ema_fast.iloc[j - lookback] > ema_slow.iloc[j - lookback] and \
                       ema_fast.iloc[j - lookback - 1] <= ema_slow.iloc[j - lookback - 1]:
                        golden_cross = True
                        break

                if not golden_cross:
                    continue

                # All 5 conditions met
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
                    "ema50": round(ema_fast.iloc[j], 2),
                    "ema200": round(ema_slow.iloc[j], 2),
                    "ret_5d": round(rets.get(5) or 0, 2),
                    "ret_10d": round(rets.get(10) or 0, 2),
                    "ret_20d": round(rets.get(20) or 0, 2),
                    "max_dd": round(max_dd, 2),
                })

        except Exception:
            continue

    # Results
    print(f"\n{'=' * 90}")
    print(f"  5-WAY CONFLUENCE RESULTS: {len(results)} signals")
    print(f"{'=' * 90}")

    if results:
        results.sort(key=lambda x: x["date"])

        print(f"\n  {'Date':<12} {'Symbol':<8} {'Close':>8} {'MACD':>8} {'VIX':>6} {'EMA50':>8} {'EMA200':>8} {'5d':>8} {'10d':>8} {'20d':>8} {'MaxDD':>8}")
        print(f"  {'-' * 100}")

        wins = 0
        for r in results:
            r20 = r["ret_20d"]
            icon = "✅" if r20 > 0 else "❌"
            if r20 > 0:
                wins += 1
            print(f"  {icon} {r['date']} {r['symbol']:<8} ${r['close']:>7.2f} {r['macd']:>+8.2f} {r['vix']:>5.1f} {r['ema50']:>8.2f} {r['ema200']:>8.2f} {r['ret_5d']:>+7.2f}% {r['ret_10d']:>+7.2f}% {r['ret_20d']:>+7.2f}% {r['max_dd']:>+7.2f}%")

        # Summary
        print(f"\n  {'SUMMARY':=^60}")
        print(f"  Total signals: {len(results)}")
        print(f"  Wins (20d): {wins} | Losses: {len(results) - wins}")
        if results:
            print(f"  Win rate: {wins / len(results) * 100:.0f}%")
            avg_5 = sum(r["ret_5d"] for r in results) / len(results)
            avg_10 = sum(r["ret_10d"] for r in results) / len(results)
            avg_20 = sum(r["ret_20d"] for r in results) / len(results)
            avg_dd = sum(r["max_dd"] for r in results) / len(results)
            print(f"  Avg 5d: {avg_5:+.2f}% | 10d: {avg_10:+.2f}% | 20d: {avg_20:+.2f}%")
            print(f"  Avg Max DD: {avg_dd:+.2f}%")

        # Compare with 4-way
        print(f"\n  COMPARISON (4-way vs 5-way):")
        print(f"    4-way (previous): 309 signals, 67% WR, +7.21% avg 20d")
        print(f"    5-way (this run): {len(results)} signals, {wins/len(results)*100:.0f}% WR, +{sum(r['ret_20d'] for r in results)/len(results):.2f}% avg 20d")

        # Save CSV
        csv_path = "/root/.hermes/profiles/trader/scripts/backtest_nasdaq100_5way.csv"
        pd.DataFrame(results).to_csv(csv_path, index=False)
        print(f"\n  Results saved to {csv_path}")
    else:
        print("  No 5-way confluence signals found.")
        print(f"  (Skipped {skipped_no_ema} stocks with insufficient data)")

    # Also run 4-way for direct comparison
    print(f"\n{'=' * 90}")
    print(f"  Running 4-way (without EMA) for direct comparison...")
    print(f"{'=' * 90}")

    results_4way = []
    for i, sym in enumerate(tickers):
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

                date_str = df.index[j].strftime("%Y-%m-%d")
                vix_val = vix_map.get(date_str)
                if vix_val is None:
                    for k in range(1, 6):
                        prev = (df.index[j] - timedelta(days=k)).strftime("%Y-%m-%d")
                        if prev in vix_map:
                            vix_val = vix_map[prev]
                            break
                if vix_val is None or vix_val < VIX_THRESH:
                    continue

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

                results_4way.append({
                    "symbol": sym,
                    "date": date_str,
                    "ret_20d": round(rets.get(20) or 0, 2),
                })
        except:
            continue

    if results_4way:
        wins_4 = sum(1 for r in results_4way if r["ret_20d"] > 0)
        avg_4 = sum(r["ret_20d"] for r in results_4way) / len(results_4way)
        print(f"  4-way: {len(results_4way)} signals, {wins_4}/{len(results_4way)} wins ({wins_4/len(results_4way)*100:.0f}%), avg 20d: {avg_4:+.2f}%")
    if results:
        wins_5 = wins
        avg_5 = sum(r["ret_20d"] for r in results) / len(results)
        print(f"  5-way: {len(results)} signals, {wins_5}/{len(results)} wins ({wins_5/len(results)*100:.0f}%), avg 20d: {avg_5:+.2f}%")


if __name__ == "__main__":
    main()
