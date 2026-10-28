#!/usr/bin/env python3
"""Pull daily OHLCV + compute Wyckoff/VP/Thorp inputs for the daily entry report."""
import json, sys, warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np

TICKERS = sys.argv[1:] or ['GME','MRVL','MKSI','GDDY','ZS','AMZN']

def get(t):
    import yfinance as yf
    df = yf.download(t, period='9mo', interval='1d', auto_adjust=False, progress=False)
    if df is None or len(df) == 0:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna(how='all')
    return df if len(df) >= 30 else None

def atr(df, n=14):
    h, l, c = df['High'], df['Low'], df['Close']
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def rsi(df, n=14):
    d = df['Close'].diff()
    up = d.clip(lower=0).rolling(n).mean()
    dn = (-d.clip(upper=0)).rolling(n).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100/(1+rs)

out = {}
for t in TICKERS:
    try:
        df = get(t)
    except Exception as e:
        out[t] = {'error': str(e)}
        continue
    if df is None:
        out[t] = {'error': 'no data'}
        continue
    c = df['Close']
    a = float(atr(df).iloc[-1])
    r = float(rsi(df).iloc[-1])
    sma20 = float(c.rolling(20).mean().iloc[-1])
    sma50 = float(c.rolling(50).mean().iloc[-1])
    sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else float('nan')
    ema200 = float(c.ewm(span=200, adjust=False).mean().iloc[-1])
    macd = c.ewm(span=12).mean() - c.ewm(span=26).mean()
    sig = macd.ewm(span=9).mean()
    tp = (df['High']+df['Low']+df['Close'])/3
    vwap20 = float((tp.tail(20)*df['Volume'].tail(20)).sum()/df['Volume'].tail(20).sum())
    w = df.tail(60)
    lo, hi = float(w['Low'].min()), float(w['High'].max())
    nb = 24
    edges = np.linspace(lo, hi, nb+1)
    tpw = ((w['High']+w['Low']+w['Close'])/3)
    idx = np.clip(((tpw - lo)/(hi-lo)*nb).astype(int), 0, nb-1)
    vp = np.zeros(nb)
    for i, v in zip(idx, w['Volume']):
        vp[i] += v
    vpoc_i = int(vp.argmax())
    vpoc = float((edges[vpoc_i]+edges[vpoc_i+1])/2)
    total = vp.sum()
    order = np.argsort(-vp)
    cum = 0; va = set()
    for j in order:
        va.add(int(j)); cum += vp[j]
        if cum/total >= 0.70: break
    vah = float(edges[max(va)+1]); val = float(edges[min(va)])
    hvns = [round(float((edges[i]+edges[i+1])/2), 2) for i in range(nb) if vp[i] > 1.3*vp.mean()]
    bars = []
    for i in range(-6, 0):
        d = df.iloc[i]
        rng = float(d['High']-d['Low'])
        pos = float((d['Close']-d['Low'])/rng) if rng > 0 else 0.5
        bars.append({'date': str(df.index[i].date()), 'o': round(float(d['Open']),2),
                     'h': round(float(d['High']),2), 'l': round(float(d['Low']),2),
                     'c': round(float(d['Close']),2), 'v': int(d['Volume']),
                     'pos': round(pos,2)})
    vol20 = float(df['Volume'].iloc[-21:-1].mean())
    hvns_sorted = sorted(hvns, key=lambda x: abs(x-float(c.iloc[-1])))[:4]
    out[t] = {
        'last_date': str(df.index[-1].date()), 'close': round(float(c.iloc[-1]),2),
        'chg1d': round(float(c.iloc[-1]/c.iloc[-2]-1)*100, 2),
        'prev_close': round(float(c.iloc[-2]),2),
        'atr': round(a,2), 'atr_pct': round(a/float(c.iloc[-1])*100,2),
        'rsi': round(r,1),
        'sma20': round(sma20,2), 'sma50': round(sma50,2),
        'sma200': round(sma200,2) if sma200==sma200 else None,
        'ema200': round(ema200,2),
        'macd_hist': round(float((macd-sig).iloc[-1]),3),
        'vwap20': round(vwap20,2),
        'vol_ratio': round(float(df['Volume'].iloc[-1])/vol20,2),
        'hi20': round(float(df['High'].tail(20).max()),2),
        'lo20': round(float(df['Low'].tail(20).min()),2),
        'hi60': round(hi,2), 'lo60': round(lo,2),
        'hi3m': round(float(df['High'].tail(63).max()),2),
        'from_3m_high_pct': round((float(c.iloc[-1])/float(df['High'].tail(63).max())-1)*100,1),
        'vpoc': round(vpoc,2), 'vah': round(vah,2), 'val': round(val,2),
        'near_hvns': hvns_sorted,
        'sma50_slope_pct': round(float(c.rolling(50).mean().iloc[-1]/c.rolling(50).mean().iloc[-11]-1)*100,2),
        'bars': bars,
        'pos_in_60d_range': round((float(c.iloc[-1])-lo)/(hi-lo)*100,1) if hi>lo else None,
    }

print(json.dumps(out, indent=1))
json.dump(out, open('/root/.hermes/profiles/trader/scripts/_expert_data.json','w'), indent=1)
