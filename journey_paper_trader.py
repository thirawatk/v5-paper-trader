#!/usr/bin/env python3
"""
Trading Journey Paper Trader — NYSE + NASDAQ + AMEX
====================================================
$10,000 starting capital, 1% risk per trade, 5 positions max.
8-factor confluence scoring (V5 engine minus VIX — removed 2026-08-14).
Target: 1% daily ($100/day).
Universe: ~370 curated liquid stocks from NYSE, NASDAQ, AMEX.

Daily cron job → Telegram report.
"""

import json, os, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path

# ═══ CONFIG ═══
STARTING_CAPITAL = 10000.0
RISK_PER_TRADE = 0.01       # 1% of capital per trade
MAX_POSITIONS = 5
MIN_CONFLUENCE = 4.0
STOP_ATR = 2.0
TP1_R = 1.2
TP2_R = 2.5
MAX_HOLD_DAYS = 30
VOLUME_FILTER = 1.2         # entry requires vol > 1.2x 20-day avg
DAILY_LOSS_LIMIT = 0.03     # 3% daily loss = stop trading

# V5 weights (VIX removed from scoring 2026-08-14 — user decision)
W_TREND=1.5; W_VWAP=2.0; W_OBV=1.0; W_CMF=1.0
W_MFI=1.0; W_MOM=1.0; W_VPQ=2.0; W_CANDLE=1.5
TOTAL_W=W_TREND+W_VWAP+W_OBV+W_CMF+W_MFI+W_MOM+W_VPQ+W_CANDLE

# Paths
BASE = "/root/.hermes/profiles/trader/scripts"
STATE_FILE = f"{BASE}/journey_state.json"
UNIVERSE_FILE = f"{BASE}/journey_universe.txt"
LOG_FILE = f"{BASE}/journey_trades.csv"

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
    return {
        "capital": STARTING_CAPITAL,
        "peak_capital": STARTING_CAPITAL,
        "positions": [],
        "closed_trades": [],
        "last_run": None,
        "daily_pnl_today": 0.0,
        "daily_pnl_date": None,
    }

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
        on=df["OBV"].iloc[idx]; os_val=df["OBV"].iloc[idx-19:idx+1].mean()
        if pd.notna(on) and pd.notna(os_val) and os_val!=0:
            if on>os_val*1.03: s["obv"]=0.8
            elif on>os_val*1.01: s["obv"]=0.5
            elif on>os_val: s["obv"]=0.2
            elif on<os_val*0.97: s["obv"]=-0.8
            elif on<os_val*0.99: s["obv"]=-0.5
            elif on<os_val: s["obv"]=-0.2
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

    # VIX factor removed 2026-08-14 (user decision): it acted as a market-regime
    # penalty, not a confluence factor. In calm markets (VIX 14-15) it cost every
    # stock -0.2 × 2.0 weight, pushing top scores just below the 4.0 threshold.

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

    # Momentum
    mom_val=df["MOM"].iloc[idx] if pd.notna(df["MOM"].iloc[idx]) else 0.0
    mom_score=round(max(-1.0, min(1.0, mom_val / 2)), 2)
    s["momentum"]=mom_score

    # Composite
    wsum=(s.get("trend",0)*W_TREND+s.get("vwap",0)*W_VWAP+s.get("obv",0)*W_OBV+
          s.get("cmf",0)*W_CMF+s.get("mfi",0)*W_MFI+s.get("momentum",0)*W_MOM+
          s.get("vp_quality",0)*W_VPQ+s.get("candle",0)*W_CANDLE)
    raw=(wsum/TOTAL_W)*10
    s["composite"]=round(raw**1.15 if raw>0 else -(abs(raw)**1.15),2)
    return s

# ═══ TRADE LOGGING ═══

def log_trade(trade):
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a") as f:
        if not file_exists:
            f.write("date,ticker,entry_date,entry_price,exit_price,exit_reason,r_multiple,pnl,shares,days_held,composite\n")
        f.write(f"{trade['exit_date']},{trade['ticker']},{trade['entry_date']},"
                f"{trade['entry_price']},{trade['exit_price']},{trade['exit_reason']},"
                f"{trade['r_multiple']},{trade['pnl']},{trade['shares']},{trade['days_held']},"
                f"{trade.get('composite','')}\n")

# ═══ MARKET HOURS GUARD ═══

def is_market_closed():
    """US market hours: M-F 9:30-16:00 ET. Returns True if market is closed."""
    from datetime import timezone
    import pytz
    et = pytz.timezone("US/Eastern")
    now = datetime.now(et)
    # Weekend
    if now.weekday() >= 5:
        return True
    # Before 9:30 or after 16:00 ET
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return now < market_open or now >= market_close

# ═══ MAIN ═══

def scan_and_trade(force=False):
    """Main scan + trade cycle. Returns markdown report string."""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    state = load_state()
    capital = state["capital"]
    positions = state["positions"]
    closed_trades = state["closed_trades"]

    # Reset daily P&L tracker on new day
    if state.get("daily_pnl_date") != today_str:
        state["daily_pnl_today"] = 0.0
        state["daily_pnl_date"] = today_str

    # Check daily loss limit
    if state["daily_pnl_today"] <= -(STARTING_CAPITAL * DAILY_LOSS_LIMIT):
        msg = f"🛑 Daily loss limit hit (${state['daily_pnl_today']:.2f}). No new entries today."
        return msg, state

    # ── Fetch VIX ──
    try:
        vix_df = yf.download("^VIX", period="5d", progress=False)
        if hasattr(vix_df.columns, 'levels'):
            vix_val = float(vix_df.iloc[-1].iloc[0])
        else:
            vix_val = float(vix_df["Close"].iloc[-1])
    except:
        vix_val = 20.0  # default

    # ── Fetch universe ──
    tickers = load_tickers(UNIVERSE_FILE)

    # Batch download (100 per batch)
    all_data = {}
    for i in range(0, len(tickers), 100):
        batch = tickers[i:i+100]
        try:
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
        except: pass

    # ── Update existing positions ──
    exits_today = []
    signals_today = []
    new_positions = []

    for pos in positions:
        sym = pos["ticker"]
        if sym not in all_data:
            new_positions.append(pos)
            continue

        df = all_data[sym]
        today_close = float(df["close"].iloc[-1])
        today_low = float(df["low"].iloc[-1])
        today_high = float(df["high"].iloc[-1])
        days_held = pos.get("days_held", 0) + 1

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
            capital += pos["capital_risked"] + pnl
            state["daily_pnl_today"] = state.get("daily_pnl_today", 0) + pnl
            trade = {
                "ticker": sym, "entry_date": pos["entry_date"],
                "exit_date": today_str,
                "entry_price": pos["entry_price"], "exit_price": round(exit_price, 2),
                "shares": pos["shares"], "risk": round(pos["capital_risked"], 2),
                "exit_reason": exit_reason, "r_multiple": exit_r,
                "pnl": round(pnl, 2), "days_held": days_held,
                "composite": pos.get("composite", 0),
            }
            closed_trades.append(trade)
            exits_today.append(trade)
            log_trade(trade)
        else:
            pos["days_held"] = days_held
            pos["current_price"] = round(float(today_close), 2)
            new_positions.append(pos)

    positions = new_positions

    # ── Scan for new entries ──
    open_tickers = {p["ticker"] for p in positions}
    slots_available = MAX_POSITIONS - len(positions)

    # Only enter if daily loss limit not hit
    daily_limit = STARTING_CAPITAL * DAILY_LOSS_LIMIT
    can_enter = state["daily_pnl_today"] > -daily_limit and slots_available > 0

    if can_enter:
        # Score all stocks and sort by composite
        scored = []
        for sym, df in all_data.items():
            if sym in open_tickers: continue
            if len(df) < 200: continue

            df = df.copy()
            df["ATR"] = compute_atr(df)
            df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
            df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()
            df["VWAP"], df["VWAP_Upper"], df["VWAP_Lower"] = compute_vwap_bands(df)
            df["OBV"] = compute_obv(df)
            df["CMF"] = compute_cmf(df)
            df["MFI"] = compute_mfi(df)
            df["VP_Quality"] = compute_vp_quality(df)
            df["MOM"] = (df["close"] - df["close"].shift(10)) / df["close"].shift(10) * 100

            idx = len(df) - 1
            sc = score_signal(df, vix_val, idx)
            if sc["composite"] < MIN_CONFLUENCE: continue

            # Volume filter
            vol_20avg = df["volume"].iloc[max(0, idx-20):idx].mean()
            if df["volume"].iloc[idx] < VOLUME_FILTER * vol_20avg:
                continue

            scored.append((sc["composite"], sym, df, sc))

        # Sort by score descending, take top slots
        scored.sort(reverse=True)

        for score, sym, df, sc in scored[:slots_available]:
            idx = len(df) - 1
            close = float(df["close"].iloc[idx])
            atr = float(df["ATR"].iloc[idx])
            if pd.isna(atr) or atr <= 0: continue

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
                "factors": {k: v for k, v in sc.items() if k != "composite"},
            }

            capital -= actual_risk
            positions.append(pos)
            signals_today.append(pos)
            open_tickers.add(sym)

    # ── Save state ──
    state["capital"] = round(capital, 2)
    deployed = sum(p["capital_risked"] for p in positions)
    state["peak_capital"] = max(state["peak_capital"], capital + deployed)
    state["positions"] = positions
    state["closed_trades"] = closed_trades
    save_state(state)

    # ── Generate Report ──
    report = generate_report(state, signals_today, exits_today, vix_val, len(all_data))
    return report, state


def generate_report(state, signals_today, exits_today, vix_val, stocks_scanned):
    """Generate Telegram-friendly markdown report."""
    capital = state["capital"]
    positions = state["positions"]
    closed = state["closed_trades"]
    deployed = sum(p["capital_risked"] for p in positions)
    total_value = capital + deployed
    total_return = (total_value - STARTING_CAPITAL) / STARTING_CAPITAL * 100
    daily_pnl = state.get("daily_pnl_today", 0)
    now = datetime.now()

    lines = []
    lines.append(f"📊 **Trading Journey** — {now.strftime('%a %b %d, %Y')}")
    lines.append(f"NYSC/NASDAQ/AMEX | {stocks_scanned} stocks scanned | VIX {vix_val:.1f}")
    lines.append("")

    # Account
    pnl_emoji = "🟢" if total_return >= 0 else "🔴"
    daily_emoji = "🟢" if daily_pnl >= 0 else "🔴"
    lines.append(f"💰 **Capital:** ${capital:,.2f}")
    lines.append(f"📊 **Deployed:** ${deployed:,.2f} ({len(positions)}/{MAX_POSITIONS} positions)")
    lines.append(f"🏦 **Total:** ${total_value:,.2f} {pnl_emoji} {total_return:+.2f}%")
    lines.append(f"📅 **Today:** {daily_emoji} ${daily_pnl:+,.2f} ({daily_pnl/STARTING_CAPITAL*100:+.2f}%)")
    lines.append(f"🎯 **Target:** $100/day (1%)")
    lines.append("")

    # Closed trades today
    if exits_today:
        lines.append("**⚡ Exits Today:**")
        for t in exits_today:
            icon = "🟢" if t["r_multiple"] > 0 else "🔴"
            lines.append(f"  {icon} {t['ticker']} {t['exit_reason']} @ ${t['exit_price']:.2f} | {t['r_multiple']:+.1f}R | ${t['pnl']:+.2f} | {t['days_held']}d")
        lines.append("")

    # New entries today
    if signals_today:
        lines.append("**🆕 New Entries:**")
        for p in signals_today:
            factors = p.get("factors", {})
            factor_icons = []
            for k in ["trend", "vwap", "obv", "cmf", "mfi", "momentum", "vix", "vp_quality", "candle"]:
                v = factors.get(k, 0)
                if v > 0.1: factor_icons.append(f"🟢{k[:3].upper()}")
                elif v < -0.1: factor_icons.append(f"🔴{k[:3].upper()}")
            lines.append(f"  🆕 {p['ticker']} ${p['entry_price']:.2f} | Score {p['composite']:.1f} | {p['shares']}sh | SL ${p['sl']:.2f}")
            if factor_icons:
                lines.append(f"     {' '.join(factor_icons)}")
        lines.append("")

    # Open positions
    if positions:
        lines.append(f"**📋 Open Positions ({len(positions)}):**")
        for p in positions:
            cur = p.get("current_price", p["entry_price"])
            risk = p["entry_price"] - p["sl"]
            unrealized_r = (cur - p["entry_price"]) / max(risk, 0.01) if risk > 0 else 0
            pos_emoji = "🟢" if unrealized_r >= 0 else "🔴"
            lines.append(f"  {pos_emoji} {p['ticker']} ${p['entry_price']:.2f}→${cur:.2f} | {unrealized_r:+.1f}R | {p['days_held']}d")
        lines.append("")

    # Performance summary
    if closed:
        wins = sum(1 for t in closed if t["r_multiple"] > 0)
        losses = sum(1 for t in closed if t["r_multiple"] <= 0)
        total_r = sum(t["r_multiple"] for t in closed)
        total_pnl = sum(t["pnl"] for t in closed)
        avg_r = total_r / len(closed)
        win_rate = wins / len(closed) * 100
        profit_factor = 0
        gross_win = sum(t["pnl"] for t in closed if t["pnl"] > 0)
        gross_loss = abs(sum(t["pnl"] for t in closed if t["pnl"] < 0))
        if gross_loss > 0:
            profit_factor = gross_win / gross_loss
        elif gross_win > 0:
            profit_factor = 999

        # Max drawdown
        peak = STARTING_CAPITAL
        max_dd = 0
        running = STARTING_CAPITAL
        for t in closed:
            running += t["pnl"]
            peak = max(peak, running)
            dd = (peak - running) / peak * 100
            max_dd = max(max_dd, dd)

        lines.append("**📈 Journey Stats:**")
        lines.append(f"  Trades: {len(closed)} (W:{wins} L:{losses})")
        lines.append(f"  Win Rate: {win_rate:.0f}%")
        lines.append(f"  Total R: {total_r:+.2f} | Avg R: {avg_r:+.2f}")
        lines.append(f"  Total P&L: ${total_pnl:+,.2f}")
        lines.append(f"  Profit Factor: {profit_factor:.2f}")
        lines.append(f"  Max Drawdown: {max_dd:.1f}%")

        # Daily target tracking
        days_active = max(1, (datetime.now() - datetime.fromisoformat(state.get("last_run", datetime.now().isoformat()))).days) if state.get("last_run") else 1
        if total_pnl > 0 and days_active > 0:
            daily_avg = total_pnl / days_active
            lines.append(f"  Daily Avg P&L: ${daily_avg:+,.2f}")
            target_pct = daily_avg / 100 * 100  # vs $100 target
            lines.append(f"  vs $100 Target: {target_pct:.0f}%")

    if not exits_today and not signals_today and not positions:
        lines.append("_No activity today. Market may be closed or no signals._")

    return "\n".join(lines)


# ═══ CLI ═══

if __name__ == "__main__":
    report, state = scan_and_trade()
    print(report)
