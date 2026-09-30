#!/usr/bin/env python3
"""
V5 Rolling Walk-Forward + Position Sweep
=========================================
Rolling WF: train 3yr, test 1yr, step 1yr
Position sweep: 2, 3, 5, 8 positions
Config base: 3% risk, min=4.0, TP1=1.0R, TP2=1.5R, hold=30d
"""

import warnings
warnings.filterwarnings("ignore")
import json, sys, time
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime
import yfinance as yf

# ═══ CONFIG ═══
STARTING_CAPITAL = 10000.0
RISK_PER_TRADE = 0.03
MIN_CONFLUENCE = 4.0
STOP_ATR = 2.0
TP1_R = 1.0
TP2_R = 1.5
MAX_HOLD_DAYS = 30
VOLUME_FILTER = 1.2

# Rolling WF params
TRAIN_YEARS = 3
TEST_YEARS = 1
STEP_YEARS = 1

# Position counts to sweep
POSITION_COUNTS = [2, 3, 5, 8]

# Weights
W_TREND=1.5; W_VWAP=2.0; W_OBV=1.0; W_CMF=1.0
W_MFI=1.0; W_MOM=1.0; W_VIX=2.0; W_VPQ=2.0; W_CANDLE=1.5
TOTAL_W = W_TREND+W_VWAP+W_OBV+W_CMF+W_MFI+W_MOM+W_VIX+W_VPQ+W_CANDLE

SP100_FILE = "/root/.hermes/profiles/trader/scripts/sp100_subset.txt"

# ═══ INDICATORS (same as v5_backtest_exact.py) ═══

def compute_atr(df):
    h,l,c = df["high"],df["low"],df["close"]
    tr = pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(14).mean()

def compute_vwap_bands(df, lb=20, ns=2.0):
    tp = (df["high"]+df["low"]+df["close"])/3
    tv = tp*df["volume"]
    vw = tv.rolling(lb).sum()/df["volume"].rolling(lb).sum().replace(0,np.nan)
    st = tp.rolling(lb).std()
    return vw, vw+ns*st, vw-ns*st

def compute_obv(df):
    obv=[0.0]; c=df["close"].values; v=df["volume"].values
    for i in range(1,len(df)):
        if c[i]>c[i-1]: obv.append(obv[-1]+v[i])
        elif c[i]<c[i-1]: obv.append(obv[-1]-v[i])
        else: obv.append(obv[-1])
    return pd.Series(obv, index=df.index)

def compute_cmf(df, p=20):
    mfm = ((df["close"]-df["low"])-(df["high"]-df["close"]))/(df["high"]-df["low"]).replace(0,np.nan)
    return (mfm*df["volume"]).rolling(p).sum()/df["volume"].rolling(p).sum()

def compute_mfi(df, p=14):
    tp=(df["high"]+df["low"]+df["close"])/3; mf=tp*df["volume"]
    ta=tp.values; ma=mf.values
    pf=np.zeros(len(df)); nf=np.zeros(len(df))
    for i in range(1,len(df)):
        if ta[i]>ta[i-1]: pf[i]=ma[i]
        elif ta[i]<ta[i-1]: nf[i]=ma[i]
    ps=pd.Series(pf).rolling(p).sum(); ns=pd.Series(nf).rolling(p).sum()
    return 100-(100/(1+ps/ns.replace(0,np.nan)))

def compute_vp_quality(df, lb=50, bins=50):
    q=pd.Series(np.nan, index=df.index)
    lo=df["low"].values; hi=df["high"].values; cl=df["close"].values; op=df["open"].values; vo=df["volume"].values
    for i in range(lb, len(df)):
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

def detect_pattern(df, idx):
    if idx<1: return "none"
    o,h,l,c = df.iloc[idx][["open","high","low","close"]]
    po,ph,pl,pc = df.iloc[idx-1][["open","high","low","close"]]
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

def score_signal(df, vix_val, idx):
    c=df["close"].iloc[idx]; s={}
    e50=df["EMA50"].iloc[idx]; e200=df["EMA200"].iloc[idx]
    if pd.notna(e50) and pd.notna(e200) and idx>=5:
        e50_prev=df["EMA50"].iloc[max(0,idx-5)]
        slope=(e50-e50_prev)/max(e50_prev,0.01)*100
        rising=slope>0.3
        if c>e50>e200 and rising: s["trend"]=1.0
        elif c>e50>e200: s["trend"]=0.6
        elif c>e50 and e50<=e200: s["trend"]=0.5 if rising else 0.4
        elif c<e50>e200: s["trend"]=0.2
        elif c<e50<e200: s["trend"]=-1.0 if slope<-0.5 else -0.8
        elif c<e50 and e50>=e200: s["trend"]=-0.4
        else: s["trend"]=0.0
    else: s["trend"]=0.0
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
    cv=df["CMF"].iloc[idx]
    s["cmf"]=max(-1.0,min(1.0,cv*1.8)) if pd.notna(cv) else 0.0
    mv=df["MFI"].iloc[idx]
    if pd.notna(mv):
        if mv>75: s["mfi"]=-0.5
        elif mv<25: s["mfi"]=0.5
        elif mv>55: s["mfi"]=0.3
        elif mv<45: s["mfi"]=-0.3
        else: s["mfi"]=0.0
    else: s["mfi"]=0.0
    if vix_val>=35: s["vix"]=0.8
    elif vix_val>=25: s["vix"]=0.5
    elif vix_val>=20: s["vix"]=0.3
    elif vix_val<12: s["vix"]=-0.5
    elif vix_val<15: s["vix"]=-0.2
    else: s["vix"]=0.0
    vq=df["VP_Quality"].iloc[idx]
    if pd.notna(vq):
        if vq>0.12: s["vp_quality"]=min(1.0,vq*5)
        elif vq>0.08: s["vp_quality"]=0.4
        else: s["vp_quality"]=0.0
    else: s["vp_quality"]=0.0
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
    mom_val=df["MOM"].iloc[idx] if pd.notna(df["MOM"].iloc[idx]) else 0.0
    s["momentum"]=round(max(-1.0,min(1.0,mom_val/2)),2)
    wsum=(s.get("trend",0)*W_TREND+s.get("vwap",0)*W_VWAP+s.get("obv",0)*W_OBV+
          s.get("cmf",0)*W_CMF+s.get("mfi",0)*W_MFI+s.get("momentum",0)*W_MOM+
          s.get("vix",0)*W_VIX+s.get("vp_quality",0)*W_VPQ+s.get("candle",0)*W_CANDLE)
    raw=(wsum/TOTAL_W)*10
    s["composite"]=round(raw**1.15 if raw>0 else -(abs(raw)**1.15),2)
    return s

# ═══ BACKTEST ENGINE ═══

def run_backtest(all_data, vix_series, timeline, start_idx, end_idx, max_positions):
    capital=STARTING_CAPITAL; positions=[]; closed_trades=[]
    equity_curve=[]; peak=STARTING_CAPITAL; max_dd=0

    for t_idx in range(start_idx, end_idx):
        dt=timeline[t_idx]
        try: vix_val=float(vix_series.loc[dt]) if dt in vix_series.index else 20.0
        except: vix_val=20.0

        surviving=[]
        for pos in positions:
            sym=pos["ticker"]; df=all_data.get(sym)
            if df is None or dt not in df.index: surviving.append(pos); continue
            idx=df.index.get_loc(dt); days_held=idx-pos["entry_bar"]
            lo=float(df["low"].iloc[idx]); hi=float(df["high"].iloc[idx]); cl=float(df["close"].iloc[idx])
            exit_reason=None; exit_price=cl; exit_r=0.0
            if lo<=pos["sl"]: exit_reason="SL"; exit_price=pos["sl"]; exit_r=-1.0
            elif hi>=pos["tp2"]: exit_reason="TP2"; exit_price=pos["tp2"]; exit_r=TP2_R
            elif hi>=pos["tp1"]: exit_reason="TP1"; exit_price=pos["tp1"]; exit_r=TP1_R
            elif days_held>=MAX_HOLD_DAYS:
                exit_reason="EXPIRED"; exit_price=cl
                rps=pos["entry_price"]-pos["sl"]
                exit_r=round((cl-pos["entry_price"])/max(rps,0.01),2)
            if exit_reason:
                pnl=pos["risked"]*exit_r; capital+=pos["risked"]+pnl
                closed_trades.append({"ticker":sym,"r_multiple":round(exit_r,2),"pnl":round(pnl,2),
                    "exit_reason":exit_reason,"days_held":days_held,"score":pos["score"]})
            else: surviving.append(pos)
        positions=surviving

        if len(positions)>=max_positions:
            pos_value=sum(p["risked"] for p in positions)
            total_val=capital+pos_value; equity_curve.append(total_val)
            peak=max(peak,total_val); dd=(peak-total_val)/peak*100; max_dd=max(max_dd,dd)
            continue

        open_syms={p["ticker"] for p in positions}; candidates=[]
        for sym, df in all_data.items():
            if sym in open_syms: continue
            if dt not in df.index: continue
            idx=df.index.get_loc(dt)
            if idx<200: continue
            vol_20avg=df["volume"].iloc[max(0,idx-20):idx].mean()
            if df["volume"].iloc[idx]<VOLUME_FILTER*vol_20avg: continue
            sc=score_signal(df, vix_val, idx)
            if sc["composite"]<MIN_CONFLUENCE: continue
            close=float(df["close"].iloc[idx]); atr=float(df["ATR"].iloc[idx])
            if pd.isna(atr) or atr<=0: continue
            candidates.append((sym, idx, sc, close, atr))

        candidates.sort(key=lambda x: x[2]["composite"], reverse=True)
        slots=max_positions-len(positions)
        for sym, idx, sc, close, atr in candidates[:slots]:
            sl=close-STOP_ATR*atr; rps=close-sl
            risked=capital*RISK_PER_TRADE; shares=max(1,int(risked/rps))
            actual_risk=shares*rps
            tp1=close+TP1_R*rps; tp2=close+TP2_R*rps
            capital-=actual_risk
            positions.append({"ticker":sym,"entry_bar":idx,"entry_price":round(close,2),
                "shares":shares,"sl":round(sl,2),"tp1":round(tp1,2),"tp2":round(tp2,2),
                "risked":round(actual_risk,2),"score":sc["composite"]})

        pos_value=sum(p["risked"] for p in positions)
        total_val=capital+pos_value; equity_curve.append(total_val)
        peak=max(peak,total_val); dd=(peak-total_val)/peak*100; max_dd=max(max_dd,dd)

    for pos in positions: capital+=pos["risked"]

    if closed_trades:
        df_t=pd.DataFrame(closed_trades)
        wins=(df_t["r_multiple"]>0).sum(); losses=(df_t["r_multiple"]<0).sum()
        total=len(df_t); wr=wins/total*100 if total>0 else 0
        avg_r=df_t["r_multiple"].mean() if total>0 else 0
        winners=df_t[df_t["r_multiple"]>0]; losers=df_t[df_t["r_multiple"]<0]
        avg_win=winners["r_multiple"].mean() if len(winners)>0 else 0
        avg_loss=losers["r_multiple"].mean() if len(losers)>0 else 0
        pf=abs(avg_win*wins/(avg_loss*losses)) if losses>0 else 99
        expectancy=(wr/100*avg_win)+((1-wr/100)*avg_loss)
        total_ret=(capital-STARTING_CAPITAL)/STARTING_CAPITAL*100
        return {"trades":total,"wr":round(wr,1),"avg_r":round(avg_r,3),
                "pf":round(pf,2),"expectancy":round(expectancy,3),"mdd":round(max_dd,1),
                "return_pct":round(total_ret,1),"capital":round(capital,2)}
    return {"trades":0,"wr":0,"avg_r":0,"pf":0,"expectancy":0,"mdd":0,"return_pct":0,"capital":STARTING_CAPITAL}


def main():
    t0=time.time()
    print("="*70)
    print("  V5 ROLLING WALK-FORWARD + POSITION SWEEP")
    print(f"  Config: {RISK_PER_TRADE*100:.0f}% risk, min={MIN_CONFLUENCE}, TP2={TP2_R}R")
    print(f"  Rolling: {TRAIN_YEARS}yr train / {TEST_YEARS}yr test / {STEP_YEARS}yr step")
    print(f"  Sweeping positions: {POSITION_COUNTS}")
    print("="*70)

    # Load universe
    tickers=[]
    with open(SP100_FILE) as f:
        for l in f:
            l=l.strip()
            if l and not l.startswith("#"): tickers.append(l.upper())
    print(f"\n[1] Loading {len(tickers)} stocks (10yr)...")

    all_data={}
    for i in range(0,len(tickers),50):
        batch=tickers[i:i+50]
        try:
            data=yf.download(" ".join(batch),period="10y",progress=False,group_by="ticker",threads=True)
            if len(batch)==1:
                df=data.copy()
                if not df.empty and len(df)>250:
                    df.columns=df.columns.str.lower(); all_data[batch[0]]=df
            else:
                for sym in batch:
                    try:
                        df=data[sym].dropna(how="all")
                        if not df.empty and len(df)>250:
                            df.columns=df.columns.str.lower(); all_data[sym]=df
                    except: pass
        except: pass
    print(f"  Loaded {len(all_data)} stocks")

    # VIX + SPY
    print("[2] Fetching VIX + SPY...")
    try:
        vix_data=yf.download("^VIX",period="10y",progress=False)
        vix_data.columns=[c.lower() if isinstance(c,str) else c[0].lower() for c in vix_data.columns]
        vix_series=vix_data["close"]
    except: vix_series=pd.Series(dtype=float)

    try:
        spy_data=yf.download("SPY",period="10y",progress=False)
        spy_data.columns=[c.lower() if isinstance(c,str) else c[0].lower() for c in spy_data.columns]
    except: spy_data=None

    # Compute indicators
    print("[3] Computing indicators...")
    for sym, df in all_data.items():
        try:
            df["ATR"]=compute_atr(df)
            df["VWAP"],df["VWAP_Upper"],df["VWAP_Lower"]=compute_vwap_bands(df)
            df["OBV"]=compute_obv(df)
            df["CMF"]=compute_cmf(df)
            df["MFI"]=compute_mfi(df)
            df["VP_Quality"]=compute_vp_quality(df)
            df["EMA50"]=df["close"].ewm(span=50).mean()
            df["EMA200"]=df["close"].ewm(span=200).mean()
            df["MOM"]=df["close"].pct_change(10)*100
        except: pass

    # Build timeline
    all_dates=set()
    for df in all_data.values(): all_dates.update(df.index.tolist())
    if vix_series is not None: all_dates.update(vix_series.index.tolist())
    timeline=sorted(all_dates)
    warmup=200
    total_bars=len(timeline)-warmup
    bars_per_year=total_bars/((timeline[-1]-timeline[warmup]).days/365)
    train_bars=int(TRAIN_YEARS*bars_per_year)
    test_bars=int(TEST_YEARS*bars_per_year)
    step_bars=int(STEP_YEARS*bars_per_year)

    # Generate rolling windows
    windows=[]
    start=warmup
    while start+train_bars+test_bars <= len(timeline)-5:
        train_start=start
        train_end=start+train_bars
        test_start=train_end
        test_end=min(train_end+test_bars, len(timeline)-5)
        windows.append({
            "train_start":train_start,"train_end":train_end,
            "test_start":test_start,"test_end":test_end,
            "train_period":f"{timeline[train_start].strftime('%Y-%m')} → {timeline[train_end].strftime('%Y-%m')}",
            "test_period":f"{timeline[test_start].strftime('%Y-%m')} → {timeline[test_end].strftime('%Y-%m')}"
        })
        start+=step_bars

    print(f"\n[4] Rolling Walk-Forward: {len(windows)} windows")
    for i,w in enumerate(windows):
        print(f"  Window {i+1}: Train [{w['train_period']}] → Test [{w['test_period']}]")

    # SPY benchmark per test window
    spy_returns=[]
    if spy_data is not None:
        for w in windows:
            ts=timeline[w["test_start"]]; te=timeline[w["test_end"]]
            spy_in=spy_data.index[spy_data.index>=ts]
            spy_end=spy_data.index[spy_data.index<=te]
            if len(spy_in)>0 and len(spy_end)>0:
                s_price=float(spy_data.loc[spy_in[0],"close"])
                e_price=float(spy_data.loc[spy_end[-1],"close"])
                spy_ret=(e_price-s_price)/s_price*100
                spy_returns.append(round(spy_ret,1))
            else: spy_returns.append(0.0)

    # Run sweep
    print(f"\n[5] Running position sweep across {len(windows)} windows...")
    results={p:[] for p in POSITION_COUNTS}

    for wi, w in enumerate(windows):
        print(f"\n  Window {wi+1}/{len(windows)}: {w['test_period']}")
        for max_pos in POSITION_COUNTS:
            r=backtest_window(all_data, vix_series, timeline, w, max_pos)
            results[max_pos].append(r)
            sys.stdout.write(f"    {max_pos}pos: {r['trades']}t {r['wr']}%WR {r['return_pct']:+.1f}% MDD{r['mdd']:.1f}%  ")
            sys.stdout.flush()
        print()

    # Aggregate results
    print("\n"+"="*70)
    print("  AGGREGATED ROLLING WALK-FORWARD RESULTS")
    print("="*70)
    print(f"\n  {'Positions':<12} {'Avg Trades':<12} {'Avg WR%':<10} {'Avg PF':<10} {'Avg ExpR':<10} {'Avg Return':<12} {'Avg MDD':<10} {'Consistency':<12}")
    print("  "+"-"*88)

    for max_pos in POSITION_COUNTS:
        rs=results[max_pos]
        n=len(rs)
        avg_trades=sum(r["trades"] for r in rs)/n
        avg_wr=sum(r["wr"] for r in rs)/n
        avg_pf=sum(r["pf"] for r in rs)/n
        avg_exp=sum(r["expectancy"] for r in rs)/n
        avg_ret=sum(r["return_pct"] for r in rs)/n
        avg_mdd=sum(r["mdd"] for r in rs)/n
        profitable=sum(1 for r in rs if r["return_pct"]>0)
        consistency=f"{profitable}/{n} windows"

        print(f"  {max_pos:<12} {avg_trades:<12.0f} {avg_wr:<10.1f} {avg_pf:<10.2f} {avg_exp:<10.3f} {avg_ret:<+12.1f} {avg_mdd:<10.1f} {consistency:<12}")

    # SPY comparison
    if spy_returns:
        avg_spy=sum(spy_returns)/len(spy_returns)
        print(f"\n  SPY avg return per window: {avg_spy:+.1f}%")
        for max_pos in POSITION_COUNTS:
            rs=results[max_pos]
            avg_ret=sum(r["return_pct"] for r in rs)/len(rs)
            alpha=avg_ret-avg_spy
            print(f"  {max_pos}pos alpha vs SPY: {alpha:+.1f}%")

    # Per-window detail
    print(f"\n  Per-Window Detail:")
    print(f"  {'Window':<10} {'Period':<25} {'SPY':<8}", end="")
    for p in POSITION_COUNTS:
        print(f" {p}pos{'':<8}", end="")
    print()
    print("  "+"-"*80)
    for i,w in enumerate(windows):
        spy_r=spy_returns[i] if i<len(spy_returns) else 0
        print(f"  {i+1:<10} {w['test_period']:<25} {spy_r:<+8.1f}", end="")
        for p in POSITION_COUNTS:
            r=results[p][i]
            print(f" {r['return_pct']:<+12.1f}", end="")
        print()

    elapsed=time.time()-t0
    print(f"\n  Completed in {elapsed:.0f}s")


def backtest_window(all_data, vix_series, timeline, window, max_positions):
    """Run single backtest on a test window."""
    return run_backtest(all_data, vix_series, timeline,
                        window["test_start"], window["test_end"], max_positions)


if __name__=="__main__":
    main()
