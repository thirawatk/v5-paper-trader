#!/usr/bin/env python3
"""Extended backtest MACD+HA with depth filter + VIX context."""

import yfinance as yf
import pandas as pd

WATCHLIST = ["VOO", "VXUS"]
FAST, SLOW, SIG = 12, 26, 9
FORWARD_DAYS = [5, 10, 20]
MACD_THRESH = -0.5


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


# Fetch VIX data once
print("Fetching VIX data...")
vix_df = yf.Ticker("^VIX").history(start="2022-10-01", end="2026-07-01")
vix_map = {}
for idx in vix_df.index:
    vix_map[idx.strftime("%Y-%m-%d")] = vix_df.loc[idx, "Close"]


def get_vix(date_str):
    """Get VIX close for a date, or nearest prior trading day."""
    if date_str in vix_map:
        return vix_map[date_str]
    # Try up to 5 prior days (weekends/holidays)
    from datetime import datetime, timedelta
    d = datetime.strptime(date_str, "%Y-%m-%d")
    for i in range(1, 6):
        prev = (d - timedelta(days=i)).strftime("%Y-%m-%d")
        if prev in vix_map:
            return vix_map[prev]
    return None


for sym in WATCHLIST:
    print(f"\n{'='*100}")
    print(f"  {sym} — Backtest 2023-2026 (MACD < {MACD_THRESH}) + VIX")
    print(f"{'='*100}")

    df = yf.Ticker(sym).history(start="2022-10-01", end="2026-07-01")
    if df.empty:
        continue

    macd, signal, hist = compute_macd(df["Close"])
    ha_open, ha_close = compute_ha(df)

    all_signals = []
    filtered_signals = []

    for i in range(1, len(hist)):
        if df.index[i].year < 2023:
            continue
        crossed = hist.iloc[i - 1] < 0 and hist.iloc[i] >= 0
        ha_green = ha_close.iloc[i] > ha_open.iloc[i]
        if crossed and ha_green:
            rets = {}
            max_dd = 0
            for d in FORWARD_DAYS:
                if i + d < len(df):
                    rets[d] = ((df["Close"].iloc[i + d] - df["Close"].iloc[i]) / df["Close"].iloc[i]) * 100
                    window_low = df["Low"].iloc[i:i+d+1].min()
                    dd = ((window_low - df["Close"].iloc[i]) / df["Close"].iloc[i]) * 100
                    max_dd = min(max_dd, dd)
                else:
                    rets[d] = None

            date_str = df.index[i].strftime("%Y-%m-%d")
            vix_val = get_vix(date_str)

            entry = {
                "date": date_str,
                "close": df["Close"].iloc[i],
                "macd_val": macd.iloc[i],
                "returns": rets,
                "max_dd": max_dd,
                "vix": vix_val
            }
            all_signals.append(entry)
            if macd.iloc[i] < MACD_THRESH:
                filtered_signals.append(entry)

    # All signals table
    print(f"\n  ALL confluence signals ({len(all_signals)}):")
    print(f"  {'Date':<12} {'Close':>8} {'MACD':>8} {'VIX':>7} {'5d':>9} {'10d':>9} {'20d':>9} {'MaxDD':>8}")
    print(f"  {'-'*80}")
    for e in all_signals:
        r = e["returns"]
        r5 = f"{r[5]:+.1f}%" if r.get(5) else "N/A"
        r10 = f"{r[10]:+.1f}%" if r.get(10) else "N/A"
        r20 = f"{r[20]:+.1f}%" if r.get(20) else "N/A"
        r20v = r.get(20)
        icon = "✅" if r20v and r20v > 0 else "❌" if r20v else "⏳"
        vix_str = f"{e['vix']:.1f}" if e['vix'] else "N/A"
        kept = " ← kept" if e["macd_val"] < MACD_THRESH else ""
        print(f"  {icon} {e['date']} ${e['close']:>7.2f} {e['macd_val']:>+8.2f} {vix_str:>7} {r5:>9} {r10:>9} {r20:>9} {e['max_dd']:>+7.1f}%{kept}")

    # Filtered signals
    print(f"\n  FILTERED signals ({len(filtered_signals)}):")
    if filtered_signals:
        wins = 0
        for e in filtered_signals:
            r = e["returns"]
            r20 = r.get(20)
            if r20 and r20 > 0:
                wins += 1
            r5 = f"{r[5]:+.1f}%" if r.get(5) else "N/A"
            r10 = f"{r[10]:+.1f}%" if r.get(10) else "N/A"
            r20s = f"{r20:+.1f}%" if r20 else "N/A"
            icon = "✅" if r20 and r20 > 0 else "❌" if r20 else "⏳"
            vix_str = f"{e['vix']:.1f}" if e['vix'] else "N/A"
            print(f"    {icon} {e['date']} ${e['close']:.2f} | MACD={e['macd_val']:.2f} | VIX={vix_str} | 5d={r5} 10d={r10} 20d={r20s} | DD={e['max_dd']:+.1f}%")
        wr = wins / len(filtered_signals) * 100
        print(f"\n    Win rate: {wr:.0f}% ({wins}/{len(filtered_signals)})")

        # VIX analysis
        vix_vals = [e['vix'] for e in filtered_signals if e['vix']]
        if vix_vals:
            print(f"    VIX range: {min(vix_vals):.1f} - {max(vix_vals):.1f} | Avg: {sum(vix_vals)/len(vix_vals):.1f}")

            # Split by VIX level
            high_vix = [e for e in filtered_signals if e['vix'] and e['vix'] >= 20]
            low_vix = [e for e in filtered_signals if e['vix'] and e['vix'] < 20]
            if high_vix:
                hv_wins = sum(1 for e in high_vix if e['returns'].get(20) and e['returns'][20] > 0)
                print(f"    VIX >= 20: {len(high_vix)} signals, {hv_wins}/{len(high_vix)} wins")
            if low_vix:
                lv_wins = sum(1 for e in low_vix if e['returns'].get(20) and e['returns'][20] > 0)
                print(f"    VIX < 20: {len(low_vix)} signals, {lv_wins}/{len(low_vix)} wins")
    else:
        print("    No signals passed the filter.")

print(f"\n{'='*100}")
print("  Done.")
