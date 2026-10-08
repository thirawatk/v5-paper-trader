#!/usr/bin/env python3
"""22:00 ICT expert refresh — gates, medallion, wyckoff for the 5 routed signals + ZS exit.
Backtest stats reused from 03:00 ICT expert outputs (Oct-7 completed bar):
  _goog_expert_out.txt (GOOG, RDDT, pooled n=837), _gev_expert_out.txt (GEV),
  _mksi_amkr_expert_out.txt (MKSI, AMKR, gates baseline, ZS probe)."""
import sys, math
import numpy as np
import pandas as pd
import yfinance as yf

sys.path.insert(0, '/root/.hermes/profiles/trader/scripts')
import confluence_score as cs
cs.fetch_funding = lambda c: (0.0, 'neutral')   # equities: funding neutral
gate_score = cs.score

TICK = ['GOOG', 'RDDT', 'GEV', 'MKSI', 'AMKR', 'ZS', 'AMZN', 'SPY']
OUT = '/root/.hermes/profiles/trader/scripts/_entry_2200_expert_out.txt'
lines = []
def P(*a):
    s = ' '.join(str(x) for x in a)
    print(s); lines.append(s)

def sma(s, n): return s.rolling(n, min_periods=n).mean()
def rsi(c, n=14):
    d = c.diff(); g = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    rs = g / l.replace(0, np.nan)
    return 100 - 100 / (1 + rs)
def atr(df, n=14):
    pc = df['Close'].shift(1)
    tr = pd.concat([df['High'] - df['Low'], (df['High'] - pc).abs(), (df['Low'] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False).mean()

raw = yf.download(TICK, period='5y', interval='1d', auto_adjust=True, group_by='ticker', progress=False, threads=True)
data = {}
for t in TICK:
    try:
        df = raw[t].dropna(how='all') if isinstance(raw.columns, pd.MultiIndex) else raw.dropna(how='all')
        if len(df) >= 200:
            data[t] = df
    except Exception as e:
        P('skip', t, repr(e))
P('loaded:', {t: len(d) for t, d in data.items()})

def build(df):
    d = df.copy()
    d['sma20'] = sma(d['Close'], 20); d['sma50'] = sma(d['Close'], 50); d['sma100'] = sma(d['Close'], 100)
    d['rsi14'] = rsi(d['Close']); d['atr14'] = atr(d)
    h = d['High'].values; l = d['Low'].values
    n = len(d); fib382 = np.full(n, np.nan); fib50 = np.full(n, np.nan); fib618 = np.full(n, np.nan); h3m = np.full(n, np.nan)
    for i in range(62, n):
        hh = h[i-62:i+1].max(); ll = l[i-62:i+1].min()
        rng = hh - ll
        h3m[i] = hh; fib382[i] = hh - 0.382*rng; fib50[i] = hh - 0.5*rng; fib618[i] = hh - 0.618*rng
    d['h3m'] = h3m; d['fib382'] = fib382; d['fib50'] = fib50; d['fib618'] = fib618
    return d

# ---------- current bars / trigger evidence ----------
P('\n========== CURRENT BARS (latest session incl. today partial) ==========')
for t in ['GOOG', 'RDDT', 'GEV', 'MKSI', 'AMKR', 'ZS', 'AMZN']:
    d = data[t]
    v20 = d['Volume'].rolling(20, min_periods=15).mean().iloc[-2]
    for dt in d.index[-2:]:
        row = d.loc[dt]
        prev = d['Close'].iloc[d.index.get_loc(dt) - 1]
        P(f"{t} {dt.date()} O={row['Open']:.2f} H={row['High']:.2f} L={row['Low']:.2f} C={row['Close']:.2f} "
          f"chg={(row['Close']/prev-1)*100:+.2f}% vol={row['Volume']/v20:.2f}x20d "
          f"closePos={(row['Close']-row['Low'])/max(row['High']-row['Low'],1e-9)*100:.0f}%range")

# ---------- plan economics ----------
P('\n========== SIGNAL ECONOMICS (latest bar) ==========')
for t in ['GOOG', 'RDDT', 'GEV', 'MKSI', 'AMKR']:
    d = build(data[t]); last = d.iloc[-1]
    px = float(last['Close']); a14 = float(last['atr14'])
    s20 = float(last['sma20']); s50 = float(last['sma50']); s100 = float(last['sma100'])
    vr = float(data[t]['Volume'].iloc[-1]) / float(data[t]['Volume'].rolling(20, min_periods=15).mean().iloc[-2])
    f382 = float(last['fib382']); f50 = float(last['fib50']); f618 = float(last['fib618']); h3m = float(last['h3m'])
    P(f"{t}: close={px:.2f} ATR={a14:.2f} RSI={float(last['rsi14']):.1f} vol={vr:.2f}x | "
      f"SMA20={s20:.2f} SMA50={s50:.2f} SMA100={s100:.2f} | fib382={f382:.2f} fib50={f50:.2f} fib618={f618:.2f} h3m={h3m:.2f}")
    P(f"   vs SMA20 {px/s20-1:+.1%} / SMA50 {px/s50-1:+.1%} / SMA100 {px/s100-1:+.1%} | "
      f"SMA stack {'20>50>100' if s20>s50>s100 else ('20<50' if s20<s50 else 'mixed')}")

# MKSI plan economics (zone $255-274, SL fill-19.78, TP1 1.5R, TP2 2.5R, $25 risk)
mk = build(data['MKSI']); mkl = mk.iloc[-1]
e = float(mkl['Close']); sl = e - 19.78; tp1 = e + 1.5*19.78; tp2 = e + 2.5*19.78
shares = int(25 // 19.78)
P(f"MKSI plan: price {e:.2f} in $255-274 = {255 <= e <= 274} | SL {sl:.2f} | TP1 {tp1:.2f} (1.5R) TP2 {tp2:.2f} (2.5R) | "
  f"sizing {shares} sh = ${shares*e:,.0f} notional, risk ${shares*19.78:.2f} ({shares*19.78/2500*100:.2f}%)")
# GOOG/RDDT/GEV/AMKR R:R at current price vs monitor stops
for t, stop, tp in [('GOOG', 332.02, 381.81), ('RDDT', 155.88, 207.00), ('GEV', 937.75, 1140.99), ('AMKR', 48.12, 54.02)]:
    dd = build(data[t]); px = float(dd.iloc[-1]['Close']); a14 = float(dd.iloc[-1]['atr14'])
    r = px - stop; w = tp - px
    n_sh = int(25 // r) if r > 0 else 0
    P(f"{t}: px {px:.2f} stop {stop:.2f} risk {r:.2f} ({r/px*100:.1f}%) tp {tp:.2f} R:R {w/r if r else 0:.2f}:1 | "
      f"1% size = {n_sh} sh (${n_sh*px:,.0f}) risk ${n_sh*r:.2f} ({n_sh*r/2500*100:.2f}%)")

# ---------- Wyckoff ----------
def wyckoff(t):
    P(f'\n--- WYCKOFF / VOLUME PROFILE ({t} 1y) ---')
    m = data[t]; m1 = m.tail(252)
    px = float(m1['Close'].iloc[-1])
    lo = float(m1['Low'].min()); hi = float(m1['High'].max())
    m3 = m.tail(63)
    P(f"1y range {lo:.2f}-{hi:.2f} | 3m high {float(m3['High'].max()):.2f} | dist from 3m high {(px/float(m3['High'].max())-1)*100:+.1f}%")
    bins = 50
    lo_, hi_ = float(m1['Close'].min()), float(m1['Close'].max())
    edges = np.linspace(lo_, hi_, bins+1); centers = (edges[:-1]+edges[1:])/2
    vp = np.zeros(bins)
    for c_, v in zip(m1['Close'].values, m1['Volume'].values):
        k = min(bins-1, max(0, int((c_-lo_)/max(hi_-lo_, 1e-9)*(bins-1))))
        vp[k] += v
    vpoc = centers[int(np.argmax(vp))]
    order = np.argsort(vp)[::-1]; cum = 0; va_idx = []
    for k in order:
        va_idx.append(k); cum += vp[k]
        if cum >= 0.70*vp.sum(): break
    vah = centers[max(va_idx)]; val = centers[min(va_idx)]
    P(f"1y VPOC={vpoc:.2f} VAH={vah:.2f} VAL={val:.2f} | price vs VPOC {(px/vpoc-1)*100:+.1f}% | in VA: {val <= px <= vah}")
    lo3, hi3 = float(m3['Close'].min()), float(m3['Close'].max())
    e3 = np.linspace(lo3, hi3, 41); c3 = (e3[:-1]+e3[1:])/2
    vp3 = np.zeros(40)
    for c_, v in zip(m3['Close'].values, m3['Volume'].values):
        k = min(39, max(0, int((c_-lo3)/max(hi3-lo3, 1e-9)*39))); vp3[k] += v
    vpoc3 = c3[int(np.argmax(vp3))]
    P(f"3m VPOC={vpoc3:.2f} | price vs 3m VPOC {(px/vpoc3-1)*100:+.1f}%")
    tp_ = (m1['High'] + m1['Low'] + m1['Close']) / 3
    raw_mf = tp_ * m1['Volume']; dtp = tp_.diff()
    posf = raw_mf.where(dtp > 0, 0.0).rolling(14).sum(); negf = raw_mf.where(dtp < 0, 0.0).rolling(14).sum()
    mfi = 100 - 100 / (1 + posf / negf.replace(0, np.nan))
    P(f"MFI14={float(mfi.iloc[-1]):.1f}")
    mf = ((m1['Close'] - m1['Low']) - (m1['High'] - m1['Close'])) / (m1['High'] - m1['Low']).replace(0, np.nan)
    cmf = (mf * m1['Volume']).rolling(20).sum() / m1['Volume'].rolling(20).sum()
    P(f"CMF20={float(cmf.iloc[-1]):.3f} (5d avg {float(cmf.tail(5).mean()):+.3f})")
    obv = (np.sign(m1['Close'].diff()).fillna(0) * m1['Volume']).cumsum()
    x = np.arange(60); slope = np.polyfit(x, obv.values[-60:], 1)[0]
    P(f"OBV 60d slope: {slope:+,.0f}/day ({'RISING = accumulation' if slope > 0 else 'FALLING = distribution'})")
    upv = m1['Volume'].tail(30)[m1['Close'].diff().tail(30) > 0].sum()
    dnv = m1['Volume'].tail(30)[m1['Close'].diff().tail(30) < 0].sum()
    P(f"30d up/down volume: {upv/1e6:.0f}M vs {dnv/1e6:.0f}M (ratio {upv/max(dnv,1):.2f})")
    avgv = m1['Volume'].rolling(50).mean(); dd = 0
    for i in range(-25, 0):
        if m1['Close'].iloc[i] < m1['Close'].iloc[i-1] and m1['Volume'].iloc[i] > avgv.iloc[i-1]:
            dd += 1
    P(f"distribution days (last 25): {dd}")
    h1 = float(m1['High'].tail(10).max()); l1 = float(m1['Low'].tail(10).min())
    h0 = float(m1['High'].iloc[-20:-10].max()); l0 = float(m1['Low'].iloc[-20:-10].min())
    P(f"10d H={h1:.2f} L={l1:.2f} | prior 10d H={h0:.2f} L={l0:.2f} -> {'HH/HL (markup)' if h1>h0 and l1>l0 else 'LH/LL or mixed'}")
    dm = build(m); last = dm.iloc[-1]
    s20 = float(last['sma20']); s50 = float(last['sma50']); s100 = float(last['sma100'])
    P(f"price vs SMA20/50/100: {px/s20-1:+.1%} / {px/s50-1:+.1%} / {px/s100-1:+.1%} | stack {'20>50>100 bullish' if s20>s50>s100 else ('20<50 mixed' if s20<s50 else 'other')}")
    leg_hi = float(m1['High'].tail(30).max()); leg_lo = float(m1['Low'].tail(30).min())
    P(f"30d leg {leg_lo:.2f}->{leg_hi:.2f}, retrace = {(leg_hi-px)/(leg_hi-leg_lo)*100:.1f}%")
    lb = dm.iloc[-1]
    body = float(lb['Close'])-float(lb['Open']); rng_ = float(lb['High'])-float(lb['Low'])
    cpos = (float(lb['Close'])-float(lb['Low']))/max(rng_,1e-9)
    where_ = 'upper third' if cpos > 0.66 else ('lower third' if cpos < 0.33 else 'mid')
    P(f"last bar: body {body:+.2f} ({body/rng_*100 if rng_ else 0:.0f}% range), close {float(lb['Close']):.2f} ({where_})")

for t in ['GOOG', 'RDDT', 'GEV', 'MKSI', 'AMKR', 'ZS']:
    wyckoff(t)

# ---------- Medallion ----------
def medallion(t):
    P(f'\n--- MEDALLION SIGNAL QUALITY ({t}) ---')
    m = data[t]; dm = build(m); last = dm.iloc[-1]
    px = float(last['Close']); s20 = float(last['sma20']); s50 = float(last['sma50']); s100 = float(last['sma100'])
    r = float(last['rsi14'])
    vr = float(m['Volume'].iloc[-1]) / float(m['Volume'].rolling(20, min_periods=15).mean().iloc[-2])
    m1 = m.tail(252)
    lo_, hi_ = float(m1['Close'].min()), float(m1['Close'].max())
    bins = 50; edges = np.linspace(lo_, hi_, bins+1); centers = (edges[:-1]+edges[1:])/2
    vp = np.zeros(bins)
    for c_, v in zip(m1['Close'].values, m1['Volume'].values):
        k = min(bins-1, max(0, int((c_-lo_)/max(hi_-lo_, 1e-9)*(bins-1)))); vp[k] += v
    vpoc = centers[int(np.argmax(vp))]
    order = np.argsort(vp)[::-1]; cum = 0; va = []
    for k in order:
        va.append(k); cum += vp[k]
        if cum >= 0.70*vp.sum(): break
    vah = centers[max(va)]; val = centers[min(va)]
    chg5 = [(m['Close'].iloc[i]/m['Close'].iloc[i-1]-1) for i in range(len(m)-5, len(m))]
    red = sum(1 for x in chg5 if x < 0); green = 5 - red
    m60 = m.tail(63)
    posr = (px-float(m60['Low'].min()))/max(float(m60['High'].max())-float(m60['Low'].min()), 1e-9)*100
    leg_hi = float(m1['High'].tail(30).max()); leg_lo = float(m1['Low'].tail(30).min())
    retr = (leg_hi-px)/max(leg_hi-leg_lo, 1e-9)*100
    f = []
    f.append(('Regime (px>SMA20 & SMA50)', f'{px>s20 and px>s50}', +1 if (px > s20 and px > s50) else -1))
    f.append(('SMA stack 20>50', f'{s20:.1f}>{s50:.1f}', +1 if s20 > s50 else -1))
    f.append(('Price vs SMA100', f'{px/s100-1:+.1%}', +1 if px > s100 else -1))
    f.append(('RSI14', f'{r:.1f}', +0.5 if 45 <= r <= 65 else 0))
    f.append(('Vol vs 20d', f'{vr:.2f}x', -1 if vr < 0.7 else (0 if vr < 1.2 else 1)))
    f.append(('5d pattern', f'{red}R/{green}G', +0.5 if green > red else -0.5))
    f.append(('Price vs 1y VPOC', f'{(px/vpoc-1)*100:+.1f}%', +1 if px > vpoc else -1))
    f.append(('Price in value area', 'yes' if val <= px <= vah else 'no', 0))
    f.append(('60d range position', f'{posr:.0f}%', 0 if 20 <= posr <= 80 else (-1 if posr < 20 else +1)))
    f.append(('30d retrace depth', f'{retr:.0f}%', -0.5 if retr > 50 else 0))
    comp = sum(x[2] for x in f)
    for x in f: P('  ', x[0], '=', x[1], '->', x[2])
    tag = 'POSITIVE confluence' if comp >= 3 else ('NEGATIVE' if comp <= -3 else 'WEAK/NEUTRAL confluence')
    P(f'composite raw sum = {comp:+.1f} -> {tag}')

for t in ['GOOG', 'RDDT', 'GEV', 'MKSI', 'AMKR', 'ZS']:
    medallion(t)

# ---------- 11-factor gate ----------
P('\n========== 11-FACTOR GATE (confluence_score.py on daily bars, funding=neutral) ==========')
for t in ['GOOG', 'RDDT', 'GEV', 'MKSI', 'AMKR', 'ZS', 'AMZN']:
    m = data[t].tail(300)
    candles = [{'time': int(ts.timestamp()), 'open': float(r['Open']), 'high': float(r['High']),
                'low': float(r['Low']), 'close': float(r['Close']), 'volume': float(r['Volume'])}
               for ts, r in m.iterrows()]
    res = gate_score(t, candles=candles)
    top_pos = sorted([(k, v['contrib']) for k, v in res['factors'].items() if v['contrib'] > 0], key=lambda x: -x[1])[:3]
    top_neg = sorted([(k, v['contrib']) for k, v in res['factors'].items() if v['contrib'] < 0], key=lambda x: x[1])[:3]
    P(f"{t}: composite {res['composite']:+.2f} -> {'PASS' if res['passes'] else 'FAIL'} (need +/-0.50) | "
      f"pos: {', '.join(f'{k}{c:+.2f}' for k, c in top_pos) or '-'} | neg: {', '.join(f'{k}{c:+.2f}' for k, c in top_neg) or '-'}")

# ---------- ZS exit probe ----------
P('\n========== ZS EXIT PROBE (15 sh @ $150, trail 2xATR) ==========')
z = data['ZS']; dz = build(z); last = dz.iloc[-1]
px = float(last['Close']); a14 = float(last['atr14'])
vr = float(z['Volume'].iloc[-1]) / float(z['Volume'].rolling(20, min_periods=15).mean().iloc[-2])
h3 = float(z['High'].tail(63).max()); h3d = z['High'].tail(63).idxmax().date()
ema12 = z['Close'].ewm(span=12, adjust=False).mean(); ema26 = z['Close'].ewm(span=26, adjust=False).mean()
macd = ema12 - ema26; sig = macd.ewm(span=9, adjust=False).mean(); hist = macd - sig
ll14 = z['Low'].rolling(14).min(); hh14 = z['High'].rolling(14).max()
stoch = 100 * (z['Close'] - ll14) / (hh14 - ll14).replace(0, np.nan)
trail = px - 2*a14
pnl = (px - 150.0) * 15
P(f"last bar {dz.index[-1].date()}: C={px:.2f} vol={vr:.2f}x20d | RSI={float(last['rsi14']):.1f} StochK={float(stoch.iloc[-1]):.1f} "
  f"MACD hist={float(hist.iloc[-1]):.3f} ATR={a14:.2f}")
P(f"3m high {h3:.2f} ({h3d}) | dist {(px/h3-1)*100:+.1f}% | 2xATR trail = {trail:.2f} | P&L {pnl:+,.2f} ({(px/150-1)*100:+.1f}%)")
P(f"if trimmed 5 sh @ {px:.2f}: realize ${(px-150)*5:+,.2f}; remaining 10 sh trail {trail:.2f} = locked min ${(trail-150)*10:+,.2f}")

# ---------- AMZN position (no alert expected) ----------
P('\n========== AMZN POSITION STATUS ==========')
a_ = build(data['AMZN']); al = a_.iloc[-1]
apx = float(al['Close']); aa = float(al['atr14'])
P(f"AMZN close={apx:.2f} entry=259.55 P&L {(apx/259.55-1)*100:+.2f}% ({(apx-259.55)*10:+.2f} USD) | "
  f"SL 249.33 TP1 274.88 TP2 285.10 TP3 295.32 | ATR={aa:.2f} RSI={float(al['rsi14']):.1f} | "
  f"SMA20 {apx/float(al['sma20'])-1:+.1%} SMA50 {apx/float(al['sma50'])-1:+.1%}")

with open(OUT, 'w') as f:
    f.write('\n'.join(lines))
print('WROTE', OUT)
