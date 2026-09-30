#!/usr/bin/env python3
"""Backtest MACD+HA+VIX on Nasdaq 100 stocks."""

import yfinance as yf
import pandas as pd
import sys
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


def get_nasdaq100():
    """Get Nasdaq 100 tickers."""
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
        # Find the table with ticker symbols
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

    # Hardcoded fallback (recent Nasdaq 100)
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
    print("=" * 80)
    print("  MACD + HA + VIX — Nasdaq 100 Backtest 2023-2026")
    print("=" * 80)

    # Get tickers
    print("\n[1/3] Fetching Nasdaq 100 list...")
    tickers = get_nasdaq100()
    print(f"  Tickers: {len(tickers)}")

    # Fetch VIX
    print("\n[2/3] Fetching VIX data...")
    vix_df = yf.Ticker("^VIX").history(start=START_DATE, end=END_DATE)
    vix_map = {}
    for idx in vix_df.index:
        vix_map[idx.strftime("%Y-%m-%d")] = vix_df.loc[idx, "Close"]
    print(f"  VIX data points: {len(vix_map)}")

    # Backtest
    print(f"\n[3/3] Running backtest on {len(tickers)} stocks...")
    results = []
    errors = 0

    for i, sym in enumerate(tickers):
        if (i + 1) % 25 == 0:
            print(f"  Progress: {i+1}/{len(tickers)} ({len(results)} signals)...")

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
            errors += 1
            continue

    # Results
    print(f"\n{'=' * 90}")
    print(f"  RESULTS: {len(results)} confluence signals across Nasdaq 100")
    print(f"{'=' * 90}")

    if results:
        results.sort(key=lambda x: x["date"])

        print(f"\n  {'Date':<12} {'Symbol':<8} {'Close':>8} {'MACD':>8} {'VIX':>6} {'5d':>8} {'10d':>8} {'20d':>8} {'MaxDD':>8}")
        print(f"  {'-' * 82}")

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
            yr_avg = sum(r["ret_20d"] for r in yr) / len(yr)
            print(f"  {year}: {len(yr)} signals, {yr_wins}/{len(yr)} wins ({yr_wins/len(yr)*100:.0f}%), avg 20d: {yr_avg:+.2f}%")

        # Top 10 best
        print(f"\n  TOP 10 Best (by 20d return):")
        for r in sorted(results, key=lambda x: x["ret_20d"], reverse=True)[:10]:
            print(f"    ✅ {r['date']} {r['symbol']:<8} ${r['close']:>7.2f} | VIX={r['vix']:.1f} | 20d={r['ret_20d']:+.2f}% | DD={r['max_dd']:+.2f}%")

        # Worst 10
        print(f"\n  WORST 10 (by 20d return):")
        for r in sorted(results, key=lambda x: x["ret_20d"])[:10]:
            print(f"    ❌ {r['date']} {r['symbol']:<8} ${r['close']:>7.2f} | VIX={r['vix']:.1f} | 20d={r['ret_20d']:+.2f}% | DD={r['max_dd']:+.2f}%")

        # By stock
        print(f"\n  BY STOCK (min 2 signals):")
        stock_stats = {}
        for r in results:
            s = r["symbol"]
            if s not in stock_stats:
                stock_stats[s] = {"wins": 0, "total": 0, "rets": []}
            stock_stats[s]["total"] += 1
            stock_stats[s]["rets"].append(r["ret_20d"])
            if r["ret_20d"] > 0:
                stock_stats[s]["wins"] += 1

        for s, st in sorted(stock_stats.items(), key=lambda x: sum(x[1]["rets"])/len(x[1]["rets"]), reverse=True):
            if st["total"] >= 2:
                avg = sum(st["rets"]) / len(st["rets"])
                print(f"    {s:<8} {st['wins']}/{st['total']} wins ({st['wins']/st['total']*100:.0f}%) | avg 20d: {avg:+.2f}%")

        # Save CSV
        csv_path = "/root/.hermes/profiles/trader/scripts/backtest_nasdaq100.csv"
        pd.DataFrame(results).to_csv(csv_path, index=False)
        print(f"\n  Results saved to {csv_path}")
    else:
        print("  No confluence signals found.")

    print(f"\n  Errors: {errors}")


if __name__ == "__main__":
    main()
