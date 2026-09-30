#!/usr/bin/env python3
"""
V5 Daily Portfolio Backtest — Apples-to-Apples with 4h/1h R4
=============================================================
- Same walk-forward, 5-cap portfolio methodology
- 8 factors (daily VIX works here), original V5 weights
- Original daily V5 params: SL=2.0×ATR, TP1=1.2R, TP2=2.5R, MinScore=4.0
"""

import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from collections import defaultdict
import yfinance as yf

# ═══ CONFIG ═══
UNIVERSE_SIZE = 100
STARTING_CAPITAL = 1000.0
RISK_PER_TRADE = 0.01
MAX_POSITIONS = 5
MIN_CONFLUENCE = 4.0
STOP_ATR = 2.0
TP1_R = 1.2
TP2_R = 2.5
MAX_HOLD_DAYS = 30
VOLUME_FILTER = 1.2

# V5 daily weights (9 factors — added momentum)
W_TREND=1.5; W_VWAP=2.0; W_OBV=1.0; W_CMF=1.0
W_MFI=1.0; W_VIX=2.0; W_VPQ=2.0; W_CANDLE=1.5; W_MOM=1.5
TOTAL_W = W_TREND+W_VWAP+W_OBV+W_CMF+W_MFI+W_VIX+W_VPQ+W_CANDLE+W_MOM

SP500_FILE = "/root/.hermes/profiles/trader/scripts/sp500_universe.txt"

# ═══ HELPERS ═══

def load_tickers(path, limit=None):
    tks = []
    with open(path) as f:
        for l in f:
            l = l.strip()
            if l and not l.startswith("#"): tks.append(l.upper())
    return tks[:limit] if limit else tks

# ═══ INDICATORS ═══

def compute_atr(df, period=14):
    high, low, close = df["high"], df["low"], df["close"]
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()

def compute_vwap_bands(df, period=20):
    typical = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (typical * df["volume"]).rolling(period).sum() / df["volume"].rolling(period).sum()
    std = typical.rolling(period).std()
    return vwap, vwap + 2 * std, vwap - 2 * std

def compute_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i-1]:
            obv.append(obv[-1] + df["volume"].iloc[i])
        elif df["close"].iloc[i] < df["close"].iloc[i-1]:
            obv.append(obv[-1] - df["volume"].iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)

def compute_cmf(df, period=20):
    mf_mult = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"]).replace(0, np.nan)
    mf_vol = mf_mult * df["volume"]
    return mf_vol.rolling(period).sum() / df["volume"].rolling(period).sum()

def compute_mfi(df, period=14):
    typical = (df["high"] + df["low"] + df["close"]) / 3
    raw_mf = typical * df["volume"]
    pos_flow = raw_mf.where(typical > typical.shift(), 0).rolling(period).sum()
    neg_flow = raw_mf.where(typical < typical.shift(), 0).rolling(period).sum()
    mfr = pos_flow / neg_flow.replace(0, np.nan)
    return 100 - (100 / (1 + mfr))

def compute_vp_quality(df, period=50):
    typical = (df["high"] + df["low"] + df["close"]) / 3
    spread = (df["high"].rolling(period).max() - df["low"].rolling(period).min())
    return (spread / typical.rolling(period).mean()).rolling(period).mean().fillna(0)

def detect_pattern(df, idx):
    if idx < 3: return "none"
    o, h, l, c = df["open"].iloc[idx], df["high"].iloc[idx], df["low"].iloc[idx], df["close"].iloc[idx]
    body = abs(c - o)
    upper = h - max(o, c)
    lower = min(o, c) - l
    rgb = body / (h - l) if h != l else 0
    if body > 0 and rgb > 0.6:
        if c > o and lower < body * 0.1: return "bullish marubozu"
        if c < o and upper < body * 0.1: return "bearish marubozu"
    if lower > body * 2 and upper < body * 0.3: return "bullish hammer"
    if upper > body * 2 and lower < body * 0.3: return "bearish shooting star"
    if idx > 0:
        po, pc = df["open"].iloc[idx-1], df["close"].iloc[idx-1]
        if c > o and po > pc and o <= pc and c >= po: return "bullish engulfing"
        if c < o and pc > po and o >= pc and c <= po: return "bearish engulfing"
    return "none"

# ═══ SCORING (8 factors, original V5) ═══

def score_signal(df, vix_val, idx):
    s = {}
    close = float(df["close"].iloc[idx])

    # Trend
    ema50 = df["EMA50"].iloc[idx]
    ema200 = df["EMA200"].iloc[idx]
    if pd.notna(ema200) and ema200 > 0:
        ratio = close / ema200
        if ratio > 1.05: s["trend"] = 0.8
        elif ratio > 1.02: s["trend"] = 0.5
        elif ratio > 1.00: s["trend"] = 0.2
        elif ratio > 0.98: s["trend"] = -0.2
        else: s["trend"] = -0.5
        if idx > 5 and ema50 > df["EMA50"].iloc[idx-5]: s["trend"] += 0.2
    else: s["trend"] = 0.0

    # VWAP
    vwap = df["VWAP"].iloc[idx]
    upper = df["VWAP_Upper"].iloc[idx]
    lower = df["VWAP_Lower"].iloc[idx]
    if pd.notna(vwap) and pd.notna(upper) and pd.notna(lower) and (upper - lower) > 0:
        pos = (close - vwap) / (upper - lower)
        s["vwap"] = min(1.0, max(-1.0, (pos + 0.2) * 3))
    else: s["vwap"] = 0.0

    # OBV
    obv = df["OBV"].iloc[idx]
    if idx > 10:
        obv_sma = df["OBV"].iloc[idx-10:idx+1].mean()
        if obv > obv_sma * 1.02: s["obv"] = 0.6
        elif obv > obv_sma: s["obv"] = 0.3
        elif obv > obv_sma * 0.98: s["obv"] = -0.2
        else: s["obv"] = -0.5
    else: s["obv"] = 0.0

    # CMF
    cmf = df["CMF"].iloc[idx]
    if pd.notna(cmf):
        if cmf > 0.15: s["cmf"] = 0.8
        elif cmf > 0.05: s["cmf"] = 0.4
        elif cmf > -0.05: s["cmf"] = 0.0
        elif cmf > -0.15: s["cmf"] = -0.3
        else: s["cmf"] = -0.6
    else: s["cmf"] = 0.0

    # MFI
    mfi = df["MFI"].iloc[idx]
    if pd.notna(mfi):
        if 30 <= mfi <= 70: s["mfi"] = 0.3
        elif mfi < 25: s["mfi"] = 0.7
        elif mfi > 85: s["mfi"] = -0.4
        else: s["mfi"] = 0.0
    else: s["mfi"] = 0.0

    # VIX
    if vix_val < 15: s["vix"] = 0.5
    elif vix_val < 20: s["vix"] = 0.2
    elif vix_val < 25: s["vix"] = 0.0
    elif vix_val < 30: s["vix"] = -0.3
    else: s["vix"] = -0.6

    # VP Quality
    vq = df["VP_Quality"].iloc[idx]
    if pd.notna(vq):
        if vq > 0.12: s["vp_quality"] = min(1.0, vq * 5)
        elif vq > 0.08: s["vp_quality"] = 0.4
        else: s["vp_quality"] = 0.0
    else: s["vp_quality"] = 0.0

    # Candle
    pat = detect_pattern(df, idx)
    if "bullish" in pat:
        if "engulfing" in pat: s["candle"] = 1.0
        elif "hammer" in pat: s["candle"] = 0.7
        elif "marubozu" in pat: s["candle"] = 0.6
        else: s["candle"] = 0.4
    elif "bearish" in pat:
        if "engulfing" in pat: s["candle"] = -1.0
        elif "star" in pat: s["candle"] = -0.7
        elif "marubozu" in pat: s["candle"] = -0.6
        else: s["candle"] = -0.4
    else: s["candle"] = 0.0

    # Momentum: MACD histogram
    macd_hist = df["MACD_Hist"].iloc[idx]
    if pd.notna(macd_hist):
        prev = df["MACD_Hist"].iloc[idx-1] if idx > 0 else 0
        if macd_hist > 0 and macd_hist > prev: s["momentum"] = min(1.0, macd_hist * 2.5)
        elif macd_hist > 0: s["momentum"] = 0.3
        elif macd_hist < 0 and macd_hist < prev: s["momentum"] = max(-1.0, macd_hist * 2.5)
        elif macd_hist < 0: s["momentum"] = -0.3
        else: s["momentum"] = 0.0
    else: s["momentum"] = 0.0

    # Composite (9 factors)
    wsum = (s.get("trend",0)*W_TREND + s.get("vwap",0)*W_VWAP + s.get("obv",0)*W_OBV +
            s.get("cmf",0)*W_CMF + s.get("mfi",0)*W_MFI + s.get("vix",0)*W_VIX +
            s.get("vp_quality",0)*W_VPQ + s.get("candle",0)*W_CANDLE + s.get("momentum",0)*W_MOM)
    raw = (wsum / TOTAL_W) * 10
    s["composite"] = round(raw**1.15 if raw > 0 else -(abs(raw)**1.15), 2)
    return s

# ═══ PORTFOLIO BACKTEST ═══

def backtest():
    tickers = load_tickers(SP500_FILE, UNIVERSE_SIZE)
    print(f"Daily Portfolio Backtest: {len(tickers)} stocks")
    print(f"Config: SL={STOP_ATR}×ATR, TP={TP1_R}/{TP2_R}R, MaxH={MAX_HOLD_DAYS}d, MinScore={MIN_CONFLUENCE}")
    print(f"Factors: 8 (Trend, VWAP, OBV, CMF, MFI, VIX, VPQ, Candle)\n")

    # Fetch daily data
    print(f"[1] Fetching daily data for {len(tickers)} stocks...")
    all_data = {}
    for i in range(0, len(tickers), 50):
        batch = tickers[i:i+50]
        try:
            data = yf.download(" ".join(batch), period="5y", progress=False, group_by="ticker", threads=True)
            if len(batch) == 1:
                df = data.copy()
                if not df.empty and len(df) > 200:
                    df.columns = df.columns.str.lower()
                    all_data[batch[0]] = df
            else:
                for sym in batch:
                    try:
                        df = data[sym].dropna(how="all")
                        if not df.empty and len(df) > 200:
                            df.columns = df.columns.str.lower()
                            all_data[sym] = df
                    except: pass
        except Exception as e:
            print(f"  Batch error: {e}")
    print(f"  Loaded {len(all_data)} stocks\n")

    # Fetch VIX daily
    print("[2] Fetching VIX...")
    vix_data = yf.download("^VIX", period="5y", progress=False)
    if hasattr(vix_data.columns, 'levels'):
        vix_series = vix_data.iloc[:, 0]
    else:
        vix_series = vix_data["Close"]

    # Compute indicators
    print("[3] Computing indicators...")
    for sym, df in all_data.items():
        df["ATR"] = compute_atr(df, 14)
        df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
        df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()
        df["VWAP"], df["VWAP_Upper"], df["VWAP_Lower"] = compute_vwap_bands(df, 20)
        df["OBV"] = compute_obv(df)
        df["CMF"] = compute_cmf(df, 20)
        df["MFI"] = compute_mfi(df, 14)
        df["VP_Quality"] = compute_vp_quality(df, 50)
        # MACD: 12,26,9 → histogram
        ema12 = df["close"].ewm(span=12, adjust=False).mean()
        ema26 = df["close"].ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        df["MACD_Hist"] = macd_line - signal_line

    # Build unified timeline
    print("[4] Running portfolio backtest...\n")
    all_dates = set()
    for df in all_data.values():
        all_dates.update(df.index)
    timeline = sorted(all_dates)
    start_idx = 300  # Enough warmup for EMA200 + all indicators
    end_idx = len(timeline) - 5

    capital = STARTING_CAPITAL
    positions = []
    closed_trades = []

    for t_idx in range(start_idx, end_idx):
        dt = timeline[t_idx]

        # Get VIX for this day
        try:
            vix_val = float(vix_series.loc[dt]) if dt in vix_series.index else 20.0
        except:
            vix_val = 20.0

        # ── Check exits ──
        surviving = []
        for pos in positions:
            sym = pos["ticker"]
            df = all_data.get(sym)
            if df is None or dt not in df.index:
                surviving.append(pos); continue

            idx = df.index.get_loc(dt)
            days_held = idx - pos["entry_bar"]
            lo = float(df["low"].iloc[idx])
            hi = float(df["high"].iloc[idx])
            cl = float(df["close"].iloc[idx])

            exit_reason = None
            exit_price = cl
            exit_r = 0.0

            if lo <= pos["sl"]:
                exit_reason = "SL"
                exit_price = pos["sl"]
                exit_r = -1.0
            elif hi >= pos["tp2"]:
                exit_reason = "TP2"
                exit_price = pos["tp2"]
                exit_r = TP2_R
            elif hi >= pos["tp1"]:
                exit_reason = "TP1"
                exit_price = pos["tp1"]
                exit_r = TP1_R
            elif days_held >= MAX_HOLD_DAYS:
                exit_reason = "EXPIRED"
                exit_price = cl
                risk_per_share = pos["entry_price"] - pos["sl"]
                exit_r = round((cl - pos["entry_price"]) / max(risk_per_share, 0.01), 2)

            if exit_reason:
                pnl = pos["risked"] * exit_r
                capital += pos["risked"] + pnl
                closed_trades.append({
                    "ticker": sym,
                    "entry_date": str(df.index[pos["entry_bar"]]),
                    "exit_date": str(dt),
                    "entry_price": pos["entry_price"],
                    "exit_price": round(exit_price, 2),
                    "exit_reason": exit_reason,
                    "r_multiple": round(exit_r, 2),
                    "pnl": round(pnl, 2),
                    "days_held": days_held,
                    "score": pos["score"],
                })
            else:
                surviving.append(pos)

        positions = surviving

        # ── Scan for entries ──
        if len(positions) >= MAX_POSITIONS: continue

        open_syms = {p["ticker"] for p in positions}
        candidates = []

        for sym, df in all_data.items():
            if sym in open_syms: continue
            if dt not in df.index: continue
            idx = df.index.get_loc(dt)
            if idx < 200: continue

            vol_20avg = df["volume"].iloc[max(0,idx-20):idx].mean()
            if df["volume"].iloc[idx] < VOLUME_FILTER * vol_20avg:
                continue

            sc = score_signal(df, vix_val, idx)
            if sc["composite"] < MIN_CONFLUENCE: continue

            close = float(df["close"].iloc[idx])
            atr = float(df["ATR"].iloc[idx])
            if pd.isna(atr) or atr <= 0: continue

            candidates.append((sym, idx, sc, close, atr))

        candidates.sort(key=lambda x: x[2]["composite"], reverse=True)
        slots = MAX_POSITIONS - len(positions)

        for sym, idx, sc, close, atr in candidates[:slots]:
            sl = close - STOP_ATR * atr
            risk_per_share = close - sl
            risked = capital * RISK_PER_TRADE
            shares = max(1, int(risked / risk_per_share))
            actual_risk = shares * risk_per_share
            tp1 = close + TP1_R * risk_per_share
            tp2 = close + TP2_R * risk_per_share

            capital -= actual_risk
            positions.append({
                "ticker": sym, "entry_bar": idx,
                "entry_price": round(close, 2), "shares": shares,
                "sl": round(sl, 2), "tp1": round(tp1, 2), "tp2": round(tp2, 2),
                "risked": round(actual_risk, 2), "score": sc["composite"],
            })

    # Return capital from open positions
    for pos in positions:
        capital += pos["risked"]

    # ── Results ──
    if not closed_trades:
        print("❌ No trades!")
        return

    df_t = pd.DataFrame(closed_trades)
    wins = (df_t["r_multiple"] > 0).sum()
    total = len(df_t)
    total_r = df_t["r_multiple"].sum()
    avg_r = total_r / total
    win_rate = wins / total * 100
    losers = df_t[df_t["r_multiple"] < 0]
    winners = df_t[df_t["r_multiple"] > 0]
    avg_loss = losers["r_multiple"].mean() if len(losers) > 0 else 0
    avg_win = winners["r_multiple"].mean() if len(winners) > 0 else 0
    pf = abs(avg_win * wins / (avg_loss * (total - wins))) if len(losers) > 0 else 99

    total_return = (capital - STARTING_CAPITAL) / STARTING_CAPITAL * 100
    cumulative = (1 + df_t["r_multiple"] * 0.01).prod() - 1
    years = (timeline[end_idx-1] - timeline[start_idx]).days / 365

    print("=" * 60)
    print("  DAILY PORTFOLIO BACKTEST RESULTS")
    print("=" * 60)
    print(f"  Universe: {len(all_data)} stocks (of {UNIVERSE_SIZE})")
    print(f"  Period: {timeline[start_idx].strftime('%Y-%m-%d')} → {timeline[end_idx-1].strftime('%Y-%m-%d')} ({years:.1f}yr)")
    print(f"  Total trades: {total}")
    print(f"  Win rate: {wins}/{total} ({win_rate:.1f}%)")
    print(f"  Avg R/trade: {avg_r:+.3f}")
    print(f"  Avg win R: {avg_win:+.3f} | Avg loss R: {avg_loss:+.3f}")
    print(f"  Profit factor: {pf:.2f}")
    print(f"  Cumulative return (1% risk): {cumulative*100:+.1f}%")
    print(f"  Ending capital: ${capital:.2f} ({total_return:+.1f}%)")
    print(f"  Annualized: {total_return/years:.1f}%/yr")
    print()
    
    print("  Exit breakdown:")
    for reason in ["TP1", "TP2", "SL", "EXPIRED"]:
        cnt = (df_t["exit_reason"] == reason).sum()
        avg_r_reason = df_t[df_t["exit_reason"] == reason]["r_multiple"].mean() if cnt > 0 else 0
        print(f"    {reason}: {cnt} ({cnt/max(total,1)*100:.1f}%) avg {avg_r_reason:+.2f}R")

    print()
    print("  Top 5 trades:")
    for _, t in df_t.nlargest(5, "r_multiple").iterrows():
        print(f"    {t['ticker']}: {t['exit_reason']} +{t['r_multiple']:.2f}R ({t['days_held']}d)")
    print("  Worst 5 trades:")
    for _, t in df_t.nsmallest(5, "r_multiple").iterrows():
        print(f"    {t['ticker']}: {t['exit_reason']} {t['r_multiple']:.2f}R ({t['days_held']}d)")


if __name__ == "__main__":
    backtest()
