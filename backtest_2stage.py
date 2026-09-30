#!/usr/bin/env python3
"""Backtest 2-stage system: Stage 1 (4-way) + Stage 2 (EMA golden cross within 30 days)."""

import yfinance as yf
import pandas as pd
import sys
from datetime import datetime, timedelta

FAST, SLOW, SIG = 12, 26, 9
MACD_THRESH = -0.5
VIX_THRESH = 20.0
EMA_FAST = 50
EMA_SLOW = 200
CONFIRM_WINDOW = 30  # trading days
FORWARD_DAYS = [5, 10, 20]
START_DATE = "2022-01-01"
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
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
        for table in tables:
            for col in table.columns:
                if 'ticker' in str(col).lower() or 'symbol' in str(col).lower():
                    tickers = table[col].dropna().tolist()
                    if len(tickers) > 50:
                        return [str(t).strip().upper().replace(".", "-") for t in tickers if len(str(t).strip()) <= 6]
    except:
        pass
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
    print("  2-STAGE BACKTEST — Nasdaq 100")
    print("  Stage 1: MACD cross + depth + HA green + VIX fear")
    print("  Stage 2: EMA 50/200 golden cross within 30 trading days")
    print("=" * 90)

    print("\n[1/3] Fetching Nasdaq 100...")
    tickers = get_nasdaq100()
    print(f"  Tickers: {len(tickers)}")

    print("\n[2/3] Fetching VIX...")
    vix_df = yf.Ticker("^VIX").history(start=START_DATE, end=END_DATE)
    vix_map = {}
    for idx in vix_df.index:
        vix_map[idx.strftime("%Y-%m-%d")] = vix_df.loc[idx, "Close"]
    print(f"  VIX data: {len(vix_map)} points")

    print(f"\n[3/3] Running 2-stage backtest on {len(tickers)} stocks...")
    stage1_signals = []
    stage2_signals = []
    stage2_misses = []

    for i, sym in enumerate(tickers):
        if (i + 1) % 25 == 0:
            print(f"  Progress: {i+1}/{len(tickers)} (S1:{len(stage1_signals)} S2:{len(stage2_signals)})...")

        try:
            df = yf.Ticker(sym).history(start=START_DATE, end=END_DATE)
            if df.empty or len(df) < 250:
                continue

            macd, signal, hist = compute_macd(df["Close"])
            ha_open, ha_close = compute_ha(df)
            ema_fast = df["Close"].ewm(span=EMA_FAST, adjust=False).mean()
            ema_slow = df["Close"].ewm(span=EMA_SLOW, adjust=False).mean()

            for j in range(200, len(hist)):
                if df.index[j].year < 2023:
                    continue

                # Stage 1: 4-way confluence
                crossed = hist.iloc[j - 1] < 0 and hist.iloc[j] >= 0
                if not crossed:
                    continue
                macd_val = macd.iloc[j]
                if macd_val >= MACD_THRESH:
                    continue
                if ha_close.iloc[j] <= ha_open.iloc[j]:
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

                # Stage 1 fired!
                entry_close = df["Close"].iloc[j]
                stage1_signals.append({
                    "symbol": sym,
                    "date": date_str,
                    "close": round(entry_close, 2),
                    "macd": round(macd_val, 4),
                    "vix": round(vix_val, 1),
                })

                # Check Stage 2: EMA golden cross within CONFIRM_WINDOW trading days
                ema_confirmed = False
                confirm_idx = None
                for k in range(j + 1, min(j + CONFIRM_WINDOW + 1, len(df))):
                    if (ema_fast.iloc[k] > ema_slow.iloc[k] and
                            ema_fast.iloc[k - 1] <= ema_slow.iloc[k - 1]):
                        ema_confirmed = True
                        confirm_idx = k
                        break

                # Forward returns from entry
                rets = {}
                max_dd = 0
                for d in FORWARD_DAYS:
                    if j + d < len(df):
                        rets[d] = ((df["Close"].iloc[j + d] - entry_close) / entry_close) * 100
                        window_low = df["Low"].iloc[j:j+d+1].min()
                        dd = ((window_low - entry_close) / entry_close) * 100
                        max_dd = min(max_dd, dd)
                    else:
                        rets[d] = None

                if ema_confirmed:
                    confirm_date = df.index[confirm_idx].strftime("%Y-%m-%d")
                    confirm_close = df["Close"].iloc[confirm_idx]
                    days_to_confirm = confirm_idx - j

                    # Forward returns from confirmation
                    confirm_rets = {}
                    for d in FORWARD_DAYS:
                        if confirm_idx + d < len(df):
                            confirm_rets[d] = ((df["Close"].iloc[confirm_idx + d] - confirm_close) / confirm_close) * 100
                        else:
                            confirm_rets[d] = None

                    stage2_signals.append({
                        "symbol": sym,
                        "entry_date": date_str,
                        "entry_close": round(entry_close, 2),
                        "confirm_date": confirm_date,
                        "confirm_close": round(confirm_close, 2),
                        "days_to_confirm": days_to_confirm,
                        "macd": round(macd_val, 4),
                        "vix": round(vix_val, 1),
                        "entry_ret_20d": round(rets.get(20) or 0, 2),
                        "confirm_ret_20d": round(confirm_rets.get(20) or 0, 2),
                        "entry_dd": round(max_dd, 2),
                    })
                else:
                    stage2_misses.append({
                        "symbol": sym,
                        "date": date_str,
                        "close": round(entry_close, 2),
                        "vix": round(vix_val, 1),
                        "ret_20d": round(rets.get(20) or 0, 2),
                        "dd": round(max_dd, 2),
                    })

        except Exception:
            continue

    # ── Results ──
    print(f"\n{'=' * 90}")
    print(f"  2-STAGE RESULTS")
    print(f"{'=' * 90}")

    # Stage 1 summary
    print(f"\n  STAGE 1 (Entry Signals): {len(stage1_signals)} total")

    # Stage 2 confirmed
    if stage2_signals:
        wins_s2 = sum(1 for s in stage2_signals if s["entry_ret_20d"] > 0)
        avg_confirm_days = sum(s["days_to_confirm"] for s in stage2_signals) / len(stage2_signals)
        avg_entry_ret = sum(s["entry_ret_20d"] for s in stage2_signals) / len(stage2_signals)
        avg_confirm_ret = sum(s["confirm_ret_20d"] for s in stage2_signals) / len(stage2_signals)

        print(f"\n  STAGE 2 CONFIRMED ({len(stage2_signals)} signals — EMA golden cross within {CONFIRM_WINDOW}d):")
        print(f"  {'Entry Date':<12} {'Symbol':<8} {'Entry$':>8} {'Confirm$':>10} {'Days':>6} {'VIX':>6} {'Entry20d':>10} {'Conf20d':>10}")
        print(f"  {'-' * 80}")

        for s in sorted(stage2_signals, key=lambda x: x["entry_date"]):
            icon = "✅" if s["entry_ret_20d"] > 0 else "❌"
            icon2 = "✅" if s["confirm_ret_20d"] > 0 else "❌"
            print(f"  {icon} {s['entry_date']} {s['symbol']:<8} ${s['entry_close']:>7.2f} ${s['confirm_close']:>8.2f} {s['days_to_confirm']:>4}d {s['vix']:>5.1f} {s['entry_ret_20d']:>+9.2f}% {icon2}{s['confirm_ret_20d']:>+8.2f}%")

        print(f"\n    Confirmed rate: {len(stage2_signals)}/{len(stage1_signals)} ({len(stage2_signals)/len(stage1_signals)*100:.0f}%)")
        print(f"    Avg days to confirm: {avg_confirm_days:.1f}")
        print(f"    Entry win rate (20d): {wins_s2}/{len(stage2_signals)} ({wins_s2/len(stage2_signals)*100:.0f}%)")
        print(f"    Avg entry 20d return: {avg_entry_ret:+.2f}%")
        print(f"    Avg confirm 20d return: {avg_confirm_ret:+.2f}%")

    # Stage 2 missed (no golden cross)
    if stage2_misses:
        wins_miss = sum(1 for s in stage2_misses if s["ret_20d"] > 0)
        avg_miss_ret = sum(s["ret_20d"] for s in stage2_misses) / len(stage2_misses)

        print(f"\n  STAGE 2 MISSED ({len(stage2_misses)} signals — NO EMA golden cross within {CONFIRM_WINDOW}d):")
        print(f"    Miss rate: {len(stage2_misses)}/{len(stage1_signals)} ({len(stage2_misses)/len(stage1_signals)*100:.0f}%)")
        print(f"    Win rate (20d): {wins_miss}/{len(stage2_misses)} ({wins_miss/len(stage2_misses)*100:.0f}%)")
        print(f"    Avg 20d return: {avg_miss_ret:+.2f}%")

        print(f"\n  {'Date':<12} {'Symbol':<8} {'Close':>8} {'VIX':>6} {'20d':>8} {'MaxDD':>8}")
        print(f"  {'-' * 55}")
        for s in sorted(stage2_misses, key=lambda x: x["date"]):
            icon = "✅" if s["ret_20d"] > 0 else "❌"
            print(f"  {icon} {s['date']} {s['symbol']:<8} ${s['close']:>7.2f} {s['vix']:>5.1f} {s['ret_20d']:>+7.2f}% {s['dd']:>+7.2f}%")

    # Final comparison
    print(f"\n  {'COMPARISON':=^60}")
    print(f"  4-way (no EMA): {len(stage1_signals)} signals, {sum(1 for s in stage1_signals)}/{len(stage1_signals)} available")
    if stage2_signals:
        print(f"  2-stage confirmed: {len(stage2_signals)} signals, {wins_s2}/{len(stage2_signals)} wins ({wins_s2/len(stage2_signals)*100:.0f}%), avg 20d: {avg_entry_ret:+.2f}%")
    if stage2_misses:
        print(f"  2-stage missed: {len(stage2_misses)} signals, {wins_miss}/{len(stage2_misses)} wins ({wins_miss/len(stage2_misses)*100:.0f}%), avg 20d: {avg_miss_ret:+.2f}%")
    print(f"  Previous 4-way Nasdaq 100: 309 signals, 67% WR, +7.21% avg 20d")

    # Save
    if stage2_signals:
        pd.DataFrame(stage2_signals).to_csv("/root/.hermes/profiles/trader/scripts/backtest_stage2_confirmed.csv", index=False)
    if stage2_misses:
        pd.DataFrame(stage2_misses).to_csv("/root/.hermes/profiles/trader/scripts/backtest_stage2_missed.csv", index=False)
    print(f"\n  CSVs saved.")


if __name__ == "__main__":
    main()
