#!/usr/bin/env python3
"""Stock-adapted confluence scorer (daily bars).
Mirrors confluence_score.py (11-factor) using daily equity data:
Trend, VWAP20, OBV, CMF, MFI, Momentum(ROC10), Candle, Wyckoff, VPOC, RSI-regime, VolDry.
Each factor scored -1..+1; composite = weighted mean. Gate: |score| >= 0.50.
"""
import json, sys, warnings
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np

def rsi(c, n=14):
    d = c.diff(); up = d.clip(lower=0).rolling(n).mean(); dn = (-d.clip(upper=0)).rolling(n).mean()
    return 100 - 100/(1 + up/dn.replace(0, np.nan))

def mf(c, h, l, v, n=14):
    tp = (h+l+c)/3; mf_ = tp*v
    pos = mf_.where(tp > tp.shift(1), 0.0)
    neg = mf_.where(tp < tp.shift(1), 0.0)
    return 100 - 100/(1 + pos.rolling(n).sum()/neg.rolling(n).sum().replace(0, np.nan))

def cmf(h, l, c, v, n=20):
    mfm = ((c-l)-(h-c))/(h-l).replace(0, np.nan)
    return (mfm*v).rolling(n).sum()/v.rolling(n).sum()

def score(t):
    import yfinance as yf
    df = yf.download(t, period='9mo', interval='1d', auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.dropna(how='all')
    if len(df) < 60: return {'error': 'short history'}
    c, h, l, v = df['Close'], df['High'], df['Low'], df['Volume']
    px = float(c.iloc[-1])
    s20, s50 = c.rolling(20).mean(), c.rolling(50).mean()
    s200 = float(c.ewm(span=200, adjust=False).mean().iloc[-1])
    tp = (h+l+c)/3
    vwap20 = float((tp.tail(20)*v.tail(20)).sum()/v.tail(20).sum())
    obv = (np.sign(c.diff().fillna(0))*v).cumsum()
    obv_slope = float(obv.iloc[-1]-obv.iloc[-21]) / float(v.tail(20).mean()*20) if float(v.tail(20).mean())>0 else 0
    cmf20 = float(cmf(h,l,c,v).iloc[-1])
    mfi14 = float(mf(c,h,l,v).iloc[-1])
    roc10 = float(c.iloc[-1]/c.iloc[-11]-1)*100
    rng = float(h.iloc[-1]-l.iloc[-1]); cpos = (px-float(l.iloc[-1]))/rng if rng>0 else 0.5
    w = df.tail(60); lo, hi = float(w['Low'].min()), float(w['High'].max())
    nb=24; edges=np.linspace(lo,hi,nb+1)
    tpx=((w['High']+w['Low']+w['Close'])/3)
    idx=np.clip(((tpx-lo)/(hi-lo)*nb).astype(int),0,nb-1)
    vp=np.zeros(nb)
    for i,vv in zip(idx,w['Volume']): vp[i]+=vv
    vpoc=float((edges[int(vp.argmax())]+edges[int(vp.argmax())+1])/2)
    pos60=(px-lo)/(hi-lo) if hi>lo else 0.5
    # volume on down bars vs up bars (last 20)
    ret = c.diff().tail(20); vol20 = v.tail(20)
    down_v = float(vol20[ret<0].mean()) if (ret<0).any() else 0
    up_v = float(vol20[ret>0].mean()) if (ret>0).any() else 0
    r = float(rsi(c).iloc[-1])
    volR = float(v.iloc[-1])/float(v.iloc[-21:-1].mean())

    f = {}
    # 1 Trend: price vs 20/50 + slope
    f['Trend'] = 1.0 if (px>s20.iloc[-1] and s20.iloc[-1]>s50.iloc[-1]) else (0.4 if px>s50.iloc[-1] else (-1.0 if px<s20.iloc[-1] and px<s50.iloc[-1] else -0.3))
    # 2 VWAP20
    f['VWAP'] = 1.0 if px>vwap20*1.005 else (-1.0 if px<vwap20*0.995 else 0.0)
    # 3 OBV
    f['OBV'] = 1.0 if obv_slope>0.15 else (0.4 if obv_slope>0.03 else (-1.0 if obv_slope<-0.15 else -0.3))
    # 4 CMF
    f['CMF'] = 1.0 if cmf20>0.1 else (0.4 if cmf20>0.02 else (-1.0 if cmf20<-0.1 else -0.3))
    # 5 MFI
    f['MFI'] = 1.0 if mfi14<30 else (0.5 if mfi14<45 else (-1.0 if mfi14>75 else 0.0))
    # 6 Momentum ROC10
    f['Mom'] = 1.0 if roc10>5 else (0.4 if roc10>0 else (-1.0 if roc10<-8 else -0.4))
    # 7 Candle
    f['Candle'] = 1.0 if (cpos>0.66 and px>float(c.iloc[-2])) else (-1.0 if cpos<0.33 else 0.0)
    # 8 Wyckoff structure (up-vol vs down-vol + range position)
    if up_v>0 and down_v>0:
        ratio = up_v/down_v
        f['Wyckoff'] = 1.0 if (ratio>1.15 and pos60>0.5) else (-1.0 if (ratio<0.85 and pos60<0.5) else (0.4 if ratio>1.0 else -0.4))
    else:
        f['Wyckoff'] = 0.0
    # 9 VPOC
    f['VPOC'] = 1.0 if px>vpoc*1.01 else (-1.0 if px<vpoc*0.99 else 0.0)
    # 10 RSI regime (oversold-in-uptrend bonus / overbought penalty)
    trend_up = px > s200
    f['RSIreg'] = 1.0 if (r<35 and trend_up) else (0.5 if r<45 and trend_up else (-1.0 if r>75 else (-0.5 if r<30 and not trend_up else 0.0)))
    # 11 Volume dryness on pullback
    f['VolDry'] = 1.0 if (volR<0.7 and px>s50.iloc[-1]) else (-1.0 if volR>1.8 else (-0.5 if volR>1.4 else 0.0))

    comp = sum(f.values())/len(f)
    return {'ticker': t, 'px': round(px,2), 'composite': round(comp,3), 'factors': {k: round(v,2) for k,v in f.items()},
            'raw': {'rsi': round(r,1), 'cmf': round(cmf20,3), 'mfi': round(mfi14,1), 'roc10': round(roc10,1),
                    'obv_slope': round(obv_slope,3), 'cpos': round(cpos,2), 'pos60': round(pos60,2),
                    'vwap20': round(vwap20,2), 'vpoc': round(vpoc,2), 'volR': round(volR,2),
                    'upv': int(up_v), 'downv': int(down_v), 'sma20': round(float(s20.iloc[-1]),2),
                    'sma50': round(float(s50.iloc[-1]),2), 'ema200': round(s200,2)}}

if __name__ == '__main__':
    out = [score(t) for t in (sys.argv[1:] or ['GME','MRVL','GDDY','GOOG','CRWV','ACMR','MKSI','ZS','AMZN'])]
    json.dump(out, open('/root/.hermes/profiles/trader/scripts/_confluence_latest.json','w'), indent=1)
    for o in out:
        if 'error' in o: print(o['ticker'], 'ERR', o['error']); continue
        print(f"{o['ticker']}: composite {o['composite']:+.2f} | {' '.join(f'{k}={v:+.1f}' for k,v in o['factors'].items())}")
        print(f"   raw {o['raw']}")
