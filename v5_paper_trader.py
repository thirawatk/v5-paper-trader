#!/usr/bin/env python3
"""
V5 Paper Trader — Real-Time S&P 500
====================================
$1,000 starting capital, 1% risk per trade.
V5 scoring (trend-slope, VWAP-center, OBV, CMF, MFI, VIX, VPQ, candle).
Entry: composite ≥ 4.0. Exit: SL=2.0×ATR | TP1=1.2R | TP2=2.5R | Max 30d.
"""

import json, os, time, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path

# ═══ CONFIG ═══
STARTING_CAPITAL = 1000.0
RISK_PER_TRADE = 0.01       # 1% of capital
MAX_POSITIONS = 5
MIN_CONFLUENCE = 4.0
STOP_ATR = 2.0
TP1_R = 1.2
TP2_R = 2.5
MAX_HOLD_DAYS = 30
VOLUME_FILTER = 1.2     # entry requires vol > 1.2× 20-day avg

# V5 weights
W_TREND=1.5; W_VWAP=2.0; W_OBV=1.0; W_CMF=1.0
W_MFI=1.0; W_VIX=2.0; W_VPQ=2.0; W_CANDLE=1.5
TOTAL_W=W_TREND+W_VWAP+W_OBV+W_CMF+W_MFI+W_VIX+W_VPQ+W_CANDLE

# Paths
STATE_FILE = "/root/.hermes/profiles/trader/scripts/v5_paper_state.json"
SP500_FILE = "/root/.hermes/profiles/trader/scripts/sp500_universe.txt"
LOG_FILE = "/root/.hermes/profiles/trader/scripts/v5_paper_trades.csv"
REPORT_FILE = "/root/.hermes/profiles/trader/scripts/v5_paper_report.md"

# ═══ HELPERS ═══

def load_tickers(path):
    tks = []
    with open(path) as f:
        for l in f:
            l = l.strip()
            if l and not l.startswith("#"): tks.append(l.upper())
    return tks

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"capital": STARTING_CAPITAL, "peak_capital": STARTING_CAPITAL,
            "positions": [], "closed_trades": [], "last_run": None}

def save_state(state):
    state["last_run"] = datetime.now().isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)

# ═══ INDICATORS ═══

def compute_atr(df):
    h,l,c=df["high"],df["low"],df["close"]
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(14).mean()

def compute_vwap_bands(df,lb=20,ns=2.0):
    tp=(df["high"]+df["low"]+df["close"])/3
    tv=tp*df["volume"]
    vw=tv.rolling(lb).sum()/df["volume"].rolling(lb).sum().replace(0,np.nan)
    st=tp.rolling(lb).std()
    return vw,vw+ns*st,vw-ns*st

def compute_obv(df):
    obv=[0.0]; c=df["close"].values; v=df["volume"].values
    for i in range(1,len(df)):
        if c[i]>c[i-1]: obv.append(obv[-1]+v[i])
        elif c[i]<c[i-1]: obv.append(obv[-1]-v[i])
        else: obv.append(obv[-1])
    return pd.Series(obv,index=df.index)

def compute_cmf(df,p=20):
    mfm=((df["close"]-df["low"])-(df["high"]-df["close"]))/(df["high"]-df["low"]).replace(0,np.nan)
    return (mfm*df["volume"]).rolling(p).sum()/df["volume"].rolling(p).sum()

def compute_mfi(df,p=14):
    tp=(df["high"]+df["low"]+df["close"])/3; mf=tp*df["volume"]
    ta=tp.values; ma=mf.values; pf=np.zeros(len(df)); nf=np.zeros(len(df))
    for i in range(1,len(df)):
        if ta[i]>ta[i-1]: pf[i]=ma[i]
        elif ta[i]<ta[i-1]: nf[i]=ma[i]
    ps=pd.Series(pf).rolling(p).sum(); ns=pd.Series(nf).rolling(p).sum()
    return 100-(100/(1+ps/ns.replace(0,np.nan)))

def compute_vp_quality(df,lb=50,bins=50):
    q=pd.Series(np.nan,index=df.index)
    lo=df["low"].values; hi=df["high"].values; cl=df["close"].values; op=df["open"].values; vo=df["volume"].values
    for i in range(lb,len(df)):
        pmin=lo[i-lb:i].min(); pmax=hi[i-lb:i].max()
        if pmax==pmin: q.iloc[i]=0.0; continue
        bs=(pmax-pmin)/bins; vb=defaultdict(float)
        for j in range(i-lb,i):
            ch=max(op[j],hi[j],lo[j],cl[j]); cl2=min(op[j],hi[j],lo[j],cl[j])
            if ch==cl2:
                bi=max(0,min(int((cl[j]-pmin)/bs),bins-1)); vb[bi]+=vo[j]
            else:
                lo2=max(0,min(int((cl2-pmin)/bs),bins-1)); hi2=max(0,min(int((ch-pmin)/bs),bins-1))
                n=hi2-lo2+1
                for b in range(lo2,hi2+1): vb[b]+=vo[j]/n
        if vb:
            tv=sum(vb.values()); q.iloc[i]=max(vb.values())/tv if tv>0 else 0.0
        else: q.iloc[i]=0.0
    return q

def detect_pattern(df,idx):
    if idx<1: return "none"
    o,h,l,c=df.iloc[idx][["open","high","low","close"]]
    po,ph,pl,pc=df.iloc[idx-1][["open","high","low","close"]]
    body=abs(c-o); tr=h-l
    if tr==0: return "none"
    br=body/tr
    if c>o and po>pc and c>po and o<pc: return "bullish_engulfing"
    if c<o and po<pc and c<po and o>pc: return "bearish_engulfing"
    if br<0.3 and (c-l)>2*body and (h-max(o,c))<0.3*body: return "bullish_hammer"
    if br<0.3 and (h-max(o,c))>2*body and (min(o,c)-l)<0.3*body: return "bearish_star"
    if br>0.8 and c>o and (h-c)<0.1*tr: return "bullish_marubozu"
    if br>0.8 and c<o and (o-h)<0.1*tr: return "bearish_marubozu"
    return "none"

# ═══ V5 SCORING ═══

def score_signal(df, vix_val, idx):
    c=df["close"].iloc[idx]; s={}

    # Trend (slope-gated)
    e50=df["EMA50"].iloc[idx]; e200=df["EMA200"].iloc[idx]
    if pd.notna(e50) and pd.notna(e200) and idx>=5:
        e50_prev=df["EMA50"].iloc[max(0,idx-5)]
        slope=(e50-e50_prev)/max(e50_prev,0.01)*100; rising=slope>0.3
        if c>e50>e200 and rising: s["trend"]=1.0
        elif c>e50>e200: s["trend"]=0.6
        elif c>e50 and e50<=e200: s["trend"]=0.5 if rising else 0.4
        elif c<e50>e200: s["trend"]=0.2
        elif c<e50<e200: s["trend"]=-1.0 if slope<-0.5 else -0.8
        elif c<e50 and e50>=e200: s["trend"]=-0.4
        else: s["trend"]=0.0
    else: s["trend"]=0.0

    # VWAP (shifted center)
    vw=df["VWAP"].iloc[idx]; vu=df["VWAP_Upper"].iloc[idx]; vl=df["VWAP_Lower"].iloc[idx]
    if pd.notna(vw) and pd.notna(vu) and pd.notna(vl) and vw>0:
        bw=vu-vl
        if bw>0:
            pct=(c-vw)/bw
            if pct<-1.5: s["vwap"]=min(1.0,abs(pct)*0.35)
            elif pct<-0.5: s["vwap"]=0.35+abs(pct+0.5)*0.5
            elif pct<0: s["vwap"]=0.2+abs(pct)*0.3
            elif pct>1.5: s["vwap"]=-0.2-(pct-1.5)*0.2
            elif pct>0.5: s["vwap"]=0.0-(pct-0.5)*0.2
            elif pct>0: s["vwap"]=0.1-pct*0.2
            else: s["vwap"]=0.2
        else: s["vwap"]=0.0
    else: s["vwap"]=0.0

    # OBV
    if idx>=20:
        on=df["OBV"].iloc[idx]; os=df["OBV"].iloc[idx-19:idx+1].mean()
        if pd.notna(on) and pd.notna(os) and os!=0:
            if on>os*1.03: s["obv"]=0.8
            elif on>os*1.01: s["obv"]=0.5
            elif on>os: s["obv"]=0.2
            elif on<os*0.97: s["obv"]=-0.8
            elif on<os*0.99: s["obv"]=-0.5
            elif on<os: s["obv"]=-0.2
            else: s["obv"]=0.0
        else: s["obv"]=0.0
    else: s["obv"]=0.0

    # CMF
    cv=df["CMF"].iloc[idx]; s["cmf"]=max(-1.0,min(1.0,cv*1.8)) if pd.notna(cv) else 0.0

    # MFI
    mv=df["MFI"].iloc[idx]
    if pd.notna(mv):
        if mv>75: s["mfi"]=-0.5
        elif mv<25: s["mfi"]=0.5
        elif mv>55: s["mfi"]=0.3
        elif mv<45: s["mfi"]=-0.3
        else: s["mfi"]=0.0
    else: s["mfi"]=0.0

    # VIX
    if vix_val>=35: s["vix"]=0.8
    elif vix_val>=25: s["vix"]=0.5
    elif vix_val>=20: s["vix"]=0.3
    elif vix_val<12: s["vix"]=-0.5
    elif vix_val<15: s["vix"]=-0.2
    else: s["vix"]=0.0

    # VP Quality
    vq=df["VP_Quality"].iloc[idx]
    if pd.notna(vq):
        if vq>0.12: s["vp_quality"]=min(1.0,vq*5)
        elif vq>0.08: s["vp_quality"]=0.4
        else: s["vp_quality"]=0.0
    else: s["vp_quality"]=0.0

    # Candle
    pat=detect_pattern(df,idx)
    if "bullish" in pat:
        if "engulfing" in pat: s["candle"]=1.0
        elif "hammer" in pat: s["candle"]=0.7
        elif "marubozu" in pat: s["candle"]=0.6
        else: s["candle"]=0.4
    elif "bearish" in pat:
        if "engulfing" in pat: s["candle"]=-1.0
        elif "star" in pat: s["candle"]=-0.7
        elif "marubozu" in pat: s["candle"]=-0.6
        else: s["candle"]=-0.4
    else: s["candle"]=0.0

    # Composite
    wsum=(s.get("trend",0)*W_TREND+s.get("vwap",0)*W_VWAP+s.get("obv",0)*W_OBV+
          s.get("cmf",0)*W_CMF+s.get("mfi",0)*W_MFI+s.get("vix",0)*W_VIX+
          s.get("vp_quality",0)*W_VPQ+s.get("candle",0)*W_CANDLE)
    raw=(wsum/TOTAL_W)*10
    s["composite"]=round(raw**1.15 if raw>0 else -(abs(raw)**1.15),2)
    return s

# ═══ MAIN ═══

def scan_and_trade():
    print(f"\n{'='*60}")
    print(f"  V5 PAPER TRADER — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    state = load_state()
    capital = state["capital"]
    positions = state["positions"]
    closed_trades = state["closed_trades"]

    print(f"  Capital: ${capital:.2f} | Positions: {len(positions)} | Closed: {len(closed_trades)}")

    # Track today's activity
    exits_today = []
    signals_today = []

    # ── Fetch VIX ──
    print("\n[1] Fetching VIX...")
    vix_df = yf.download("^VIX", period="5d", progress=False)
    if hasattr(vix_df.columns, 'levels'):
        vix_val = float(vix_df.iloc[-1].iloc[0])
    else:
        vix_val = float(vix_df["Close"].iloc[-1])
    print(f"  VIX: {vix_val:.1f}")

    # ── Fetch SP500 tickers ──
    tickers = load_tickers(SP500_FILE)
    print(f"\n[2] Scanning {len(tickers)} S&P 500 stocks...")

    # Batch download recent data
    all_data = {}
    for i in range(0, len(tickers), 100):
        batch = tickers[i:i+100]
        data = yf.download(" ".join(batch), period="1y", progress=False, group_by="ticker", threads=True)
        if len(batch) == 1:
            df = data.copy()
            if not df.empty:
                df.columns = df.columns.str.lower()
                if len(df) > 50: all_data[batch[0]] = df
        else:
            for sym in batch:
                try:
                    df = data[sym].dropna(how="all")
                    if not df.empty and len(df) > 50:
                        df.columns = df.columns.str.lower()
                        all_data[sym] = df
                except: pass

    print(f"  Loaded {len(all_data)} stocks")

    # ── Update existing positions ──
    print(f"\n[3] Checking {len(positions)} open positions...")
    new_positions = []
    for pos in positions:
        sym = pos["ticker"]
        if sym not in all_data:
            new_positions.append(pos)  # Keep if no data
            continue

        df = all_data[sym]
        today = df.index[-1]
        today_close = float(df["close"].iloc[-1])
        today_low = float(df["low"].iloc[-1])
        today_high = float(df["high"].iloc[-1])
        days_held = pos.get("days_held", 0) + 1

        # Check exits
        exit_reason = None
        exit_price = today_close
        exit_r = 0.0

        if today_low <= pos["sl"]:
            exit_reason = "SL"
            exit_price = pos["sl"]
            exit_r = -1.0
        elif today_high >= pos["tp2"]:
            exit_reason = "TP2"
            exit_price = pos["tp2"]
            exit_r = TP2_R
        elif today_high >= pos["tp1"]:
            exit_reason = "TP1"
            exit_price = pos["tp1"]
            exit_r = TP1_R
        elif days_held >= MAX_HOLD_DAYS:
            exit_reason = "EXPIRED"
            exit_price = today_close
            risk = pos["entry_price"] - pos["sl"]
            exit_r = round((today_close - pos["entry_price"]) / max(risk, 0.01), 2)

        if exit_reason:
            pnl = pos["capital_risked"] * exit_r
            capital += pos["capital_risked"] + pnl  # Return risked capital + P&L
            trade = {
                "ticker": sym, "entry_date": pos["entry_date"],
                "exit_date": today.strftime("%Y-%m-%d"),
                "entry_price": pos["entry_price"], "exit_price": round(exit_price, 2),
                "shares": pos["shares"], "risk": round(pos["capital_risked"], 2),
                "exit_reason": exit_reason, "r_multiple": exit_r,
                "pnl": round(pnl, 2), "days_held": days_held,
            }
            closed_trades.append(trade)
            exits_today.append(trade)
            print(f"  {'🔴' if exit_r<0 else '🟢'} {sym}: {exit_reason} @ ${exit_price:.2f} ({exit_r:+.2f}R, ${pnl:+.2f})")
            # Log to CSV
            log_trade(trade)
        else:
            pos["days_held"] = days_held
            new_positions.append(pos)

    positions = new_positions

    # ── Scan for new signals ──
    print(f"\n[4] Scanning for new entries (max {MAX_POSITIONS - len(positions)} slots)...")
    open_tickers = {p["ticker"] for p in positions}
    signals_found = 0

    for sym, df in all_data.items():
        if sym in open_tickers: continue
        if len(positions) >= MAX_POSITIONS: break
        if len(df) < 200: continue

        # Compute indicators
        df = df.copy()
        df["ATR"] = compute_atr(df)
        df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
        df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()
        df["VWAP"], df["VWAP_Upper"], df["VWAP_Lower"] = compute_vwap_bands(df)
        df["OBV"] = compute_obv(df)
        df["CMF"] = compute_cmf(df)
        df["MFI"] = compute_mfi(df)
        df["VP_Quality"] = compute_vp_quality(df)

        # Score last candle
        idx = len(df) - 1
        sc = score_signal(df, vix_val, idx)
        if sc["composite"] < MIN_CONFLUENCE: continue

        # Volume filter: require vol > 1.2× 20-day avg
        vol_20avg = df["volume"].iloc[max(0, idx-20):idx].mean()
        if df["volume"].iloc[idx] < VOLUME_FILTER * vol_20avg:
            continue

        close = float(df["close"].iloc[idx])
        atr = float(df["ATR"].iloc[idx])
        if pd.isna(atr) or atr <= 0: continue

        # Calculate position
        sl = close - STOP_ATR * atr
        risk_per_share = close - sl
        capital_risked = capital * RISK_PER_TRADE
        shares = max(1, int(capital_risked / risk_per_share))
        actual_risk = shares * risk_per_share

        tp1 = close + TP1_R * risk_per_share
        tp2 = close + TP2_R * risk_per_share

        pos = {
            "ticker": sym,
            "entry_date": df.index[idx].strftime("%Y-%m-%d"),
            "entry_price": round(close, 2),
            "shares": shares,
            "sl": round(sl, 2),
            "tp1": round(tp1, 2),
            "tp2": round(tp2, 2),
            "capital_risked": round(actual_risk, 2),
            "atr": round(atr, 2),
            "composite": sc["composite"],
            "days_held": 0,
        }

        capital -= actual_risk  # Reserve risk capital
        positions.append(pos)
        signals_today.append(pos)
        open_tickers.add(sym)
        signals_found += 1
        print(f"  🆕 {sym}: ${close:.2f} | Score={sc['composite']:.1f} | {shares}sh | Risk=${actual_risk:.2f} | SL=${sl:.2f}")

    # ── Save state ──
    state["capital"] = round(capital, 2)
    state["peak_capital"] = max(state["peak_capital"], capital + sum(p["capital_risked"] for p in positions))
    state["positions"] = positions
    state["closed_trades"] = closed_trades
    save_state(state)

    # ── Summary ──
    total_value = capital + sum(p["capital_risked"] for p in positions)
    total_return = (total_value - STARTING_CAPITAL) / STARTING_CAPITAL * 100

    print(f"\n{'='*60}")
    print(f"  DAILY SUMMARY")
    print(f"{'='*60}")
    print(f"  Cash: ${capital:.2f}")
    print(f"  In positions: ${sum(p['capital_risked'] for p in positions):.2f}")
    print(f"  Total value: ${total_value:.2f} ({total_return:+.1f}%)")
    print(f"  Open positions: {len(positions)} | Closed trades: {len(closed_trades)}")
    if closed_trades:
        wins = sum(1 for t in closed_trades if t["r_multiple"] > 0)
        total_r = sum(t["r_multiple"] for t in closed_trades)
        print(f"  Win rate: {wins}/{len(closed_trades)} ({wins/max(len(closed_trades),1)*100:.0f}%)")
        print(f"  Total R: {total_r:+.2f} | Total P&L: ${sum(t['pnl'] for t in closed_trades):+.2f}")

    # ── Generate Markdown Report ──
    report_path = generate_markdown_report(state, signals_today, exits_today)
    print(f"\n  📄 Report saved: {report_path}")

    return state


def log_trade(trade):
    """Append closed trade to CSV."""
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a") as f:
        if not file_exists:
            f.write("date,ticker,entry_date,entry_price,exit_price,exit_reason,r_multiple,pnl,shares,days_held\n")
        f.write(f"{trade['exit_date']},{trade['ticker']},{trade['entry_date']},"
                f"{trade['entry_price']},{trade['exit_price']},{trade['exit_reason']},"
                f"{trade['r_multiple']},{trade['pnl']},{trade['shares']},{trade['days_held']}\n")


def generate_markdown_report(state, signals_today, exits_today):
    """Write a formatted markdown report."""
    capital = state["capital"]
    positions = state["positions"]
    closed_trades = state["closed_trades"]
    total_value = capital + sum(p["capital_risked"] for p in positions)
    total_return = (total_value - STARTING_CAPITAL) / STARTING_CAPITAL * 100
    now = datetime.now().strftime("%Y-%m-%d %H:%M ICT")

    lines = []
    lines.append(f"# 📊 V5 Paper Trader Report")
    lines.append(f"**{now}** | S&P 500 | 8-Factor Confluence")
    lines.append("")
    lines.append("## 📈 Account Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| 💰 Cash | ${capital:.2f} |")
    lines.append(f"| 📊 In Positions | ${sum(p['capital_risked'] for p in positions):.2f} |")
    lines.append(f"| 🏦 **Total Value** | **${total_value:.2f}** ({total_return:+.1f}%) |")
    lines.append(f"| 📈 Peak Capital | ${state['peak_capital']:.2f} |")
    lines.append(f"| 📂 Open Positions | {len(positions)}/{MAX_POSITIONS} |")
    lines.append(f"| 📝 Closed Trades | {len(closed_trades)} |")

    if closed_trades:
        wins = sum(1 for t in closed_trades if t["r_multiple"] > 0)
        total_r = sum(t["r_multiple"] for t in closed_trades)
        total_pnl = sum(t["pnl"] for t in closed_trades)
        avg_r = total_r / len(closed_trades) if closed_trades else 0
        lines.append(f"| 🎯 Win Rate | {wins}/{len(closed_trades)} ({wins/max(len(closed_trades),1)*100:.0f}%) |")
        lines.append(f"| ⚡ Total R | {total_r:+.2f} |")
        lines.append(f"| 💵 Total P&L | ${total_pnl:+.2f} |")
        lines.append(f"| 📐 Avg R/Trade | {avg_r:+.2f} |")

    lines.append("")

    # ── Today's Activity ──
    if exits_today or signals_today:
        lines.append("## ⚡ Today's Activity")
        lines.append("")

    if exits_today:
        lines.append("### 🔴 Exits")
        lines.append("")
        lines.append("| Ticker | Exit | Price | R | P&L | Days |")
        lines.append("|--------|------|-------|---|-----|------|")
        for t in exits_today:
            emoji = "🟢" if t["r_multiple"] > 0 else "🔴"
            lines.append(f"| {t['ticker']} | {t['exit_reason']} | ${t['exit_price']:.2f} | {t['r_multiple']:+.2f}R | ${t['pnl']:+.2f} | {t['days_held']}d |")
        lines.append("")

    if signals_today:
        lines.append("### 🆕 New Entries")
        lines.append("")
        lines.append("| Ticker | Entry | Score | Shares | Risk | SL | TP1 | TP2 |")
        lines.append("|--------|-------|-------|--------|------|-----|------|------|")
        for p in signals_today:
            lines.append(f"| {p['ticker']} | ${p['entry_price']:.2f} | {p['composite']:.1f} | {p['shares']} | ${p['capital_risked']:.2f} | ${p['sl']:.2f} | ${p['tp1']:.2f} | ${p['tp2']:.2f} |")
        lines.append("")

    # ── Open Positions ──
    if positions:
        lines.append("## 📂 Open Positions")
        lines.append("")
        lines.append("| Ticker | Entry | Price | Score | SL | TP1 | TP2 | Days |")
        lines.append("|--------|-------|-------|-------|-----|------|------|------|")
        for p in sorted(positions, key=lambda x: x["composite"], reverse=True):
            days = p.get("days_held", 0)
            lines.append(f"| {p['ticker']} | {p['entry_date']} | ${p['entry_price']:.2f} | {p['composite']:.1f} | ${p['sl']:.2f} | ${p['tp1']:.2f} | ${p['tp2']:.2f} | {days}d |")
        lines.append("")

    # ── Closed Trades History ──
    if closed_trades:
        lines.append("## 📝 Closed Trades History")
        lines.append("")
        lines.append("| Date | Ticker | Entry | Exit | Reason | R | P&L | Days |")
        lines.append("|------|--------|-------|------|--------|---|-----|------|")
        for t in reversed(closed_trades[-20:]):  # last 20
            lines.append(f"| {t['exit_date']} | {t['ticker']} | ${t['entry_price']:.2f} | ${t['exit_price']:.2f} | {t['exit_reason']} | {t['r_multiple']:+.2f}R | ${t['pnl']:+.2f} | {t['days_held']}d |")
        lines.append("")

    lines.append("---")
    lines.append(f"*Auto-generated by V5 Paper Trader — {now}*")

    report = "\n".join(lines)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    return REPORT_FILE


if __name__ == "__main__":
    scan_and_trade()
