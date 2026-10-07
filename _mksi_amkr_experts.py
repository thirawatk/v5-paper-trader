#!/usr/bin/env python3
"""3-Expert analysis for MKSI + AMKR + ZS exit + 11-factor gates (entry monitor Thu 08 Oct 2026 03:00 ICT):
1) Thorp: fib-dip signal pooled (9 base tickers) + MKSI/AMKR own-name stats, plan economics
2) Wyckoff: structure + volume profile per ticker
3) Medallion: confluence factors + 11-factor gate (confluence_score on daily bars)
4) ZS exit probe (trailing stop position)
"""
import math, sys
import numpy as np
import pandas as pd
import yfinance as yf

sys.path.insert(0, '/root/.hermes/profiles/trader/scripts')
import confluence_score as cs
cs.fetch_funding = lambda c: (0.0, 'neutral')   # equities: no funding -> neutral (0)
gate_score = cs.score

BASE = ['GOOG', 'RDDT', 'GDDY', 'ZS', 'BCC', 'FBK', 'AMZN', 'MRVL', 'GEV', 'SPY']
EXTRA = ['MKSI', 'AMKR']
TICKERS = BASE + EXTRA
OUT = '/root/.hermes/profiles/trader/scripts/_mksi_amkr_expert_out.txt'
lines = []
def P(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    lines.append(s)

# ---------- helpers ----------
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

# ---------- data ----------
raw = yf.download(TICKERS, period='5y', interval='1d', auto_adjust=True, group_by='ticker', progress=False, threads=True)
data = {}
for t in TICKERS:
    try:
        df = raw[t].dropna(how='all') if isinstance(raw.columns, pd.MultiIndex) else raw.dropna(how='all')
        if len(df) >= 200:
            data[t] = df
    except Exception as e:
        P('skip', t, repr(e))
P('loaded:', {t: len(d) for t, d in data.items()})

# ---------- current bars (trigger evidence) ----------
P('\n========== CURRENT BARS (last 2 sessions) ==========')
for t in ['AMZN', 'GOOG', 'GEV', 'MKSI', 'AMKR', 'ZS']:
    d = data[t]
    v20 = d['Volume'].rolling(20, min_periods=15).mean().iloc[-2]
    for dt in d.index[-2:]:
        row = d.loc[dt]
        P(f"{t} {dt.date()} O={row['Open']:.2f} H={row['High']:.2f} L={row['Low']:.2f} C={row['Close']:.2f} "
          f"chg={(row['Close']/d.loc[d.index[d.index.get_loc(dt)-1], 'Close']-1)*100:+.2f}% "
          f"vol={row['Volume']/v20:.2f}x20d closePos={(row['Close']-row['Low'])/max(row['High']-row['Low'],1e-9)*100:.0f}%range")

# ---------- Thorp: fib-dip signal (identical definition to _goog_experts.py) ----------
COST_SIDE = 0.0005   # 5bp per side: commission+spread+slippage (paper estimate)

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

def run_ticker(t, d):
    d = build(d)
    h = d['High'].values; l = d['Low'].values; o = d['Open'].values; c = d['Close'].values
    idx = d.index
    sma20 = d['sma20'].values; sma50 = d['sma50'].values; atr14 = d['atr14'].values
    f382 = d['fib382'].values; f50 = d['fib50'].values; f618 = d['fib618'].values; hh = d['h3m'].values
    trades = []; in_pos = False
    for i in range(100, len(d) - 1):
        if np.isnan(sma20[i]) or np.isnan(sma50[i]) or np.isnan(f382[i]): continue
        uptrend = (c[i] > sma20[i]) and (c[i] > sma50[i])
        in_band = (c[i] >= f50[i]*0.98) and (c[i] <= f382[i]*1.02)
        if not (uptrend and in_band): continue
        if in_pos: continue
        entry = c[i]
        stop = f618[i] - atr14[i]
        tp = hh[i]
        if not (stop > 0) or entry <= stop or tp <= entry: continue
        exit_px = None; exit_i = None; reason = None
        for j in range(i+1, min(i+1+63, len(d))):
            if l[j] <= stop:
                exit_px = o[j] if o[j] < stop else stop; exit_i = j; reason = 'STOP'; break
            if h[j] >= tp:
                exit_px = o[j] if o[j] > tp else tp; exit_i = j; reason = 'TP'; break
        if exit_px is None:
            j = min(i+1+63-1, len(d)-1); exit_px = c[j]; exit_i = j; reason = 'TIME'
        in_pos = True
        gross_r = (exit_px - entry) / (entry - stop)
        net_ret = (exit_px * (1 - COST_SIDE) / (entry * (1 + COST_SIDE))) - 1
        cost_r = (2*COST_SIDE) / ((entry - stop)/entry)
        trades.append(dict(ticker=t, entry_date=str(idx[i].date()), exit_date=str(idx[exit_i].date()),
                           entry=round(entry,2), stop=round(stop,2), tp=round(tp,2),
                           exit=round(exit_px,2), reason=reason,
                           gross_r=round(gross_r,3), net_r=round(gross_r - cost_r,3),
                           net_pct=round(net_ret*100,3), days=exit_i - i))
        in_pos = False
    return trades

def stats(trs, label):
    if not trs:
        P(label, 'no trades'); return None
    n = len(trs)
    wins = [x for x in trs if x['net_r'] > 0]; losses = [x for x in trs if x['net_r'] <= 0]
    wr = len(wins)/n
    aw = np.mean([x['net_r'] for x in wins]) if wins else 0.0
    al = abs(np.mean([x['net_r'] for x in losses])) if losses else 0.01
    exp = np.mean([x['net_r'] for x in trs])
    sd = np.std([x['net_r'] for x in trs], ddof=1) if n > 1 else 0
    tstat = exp / (sd/math.sqrt(n)) if sd > 0 else 0
    pf = sum(x['net_r'] for x in wins) / abs(sum(x['net_r'] for x in losses)) if losses and sum(x['net_r'] for x in losses) != 0 else float('inf')
    mc = cur = 0
    for x in trs:
        if x['net_r'] <= 0: cur += 1; mc = max(mc, cur)
        else: cur = 0
    kelly = max(0.0, wr - (1-wr)/(aw/al if al > 0 else 1))
    P(f'--- {label} ---')
    P(f'n={n} WR={wr*100:.1f}% avgWin={aw:.3f}R avgLoss={al:.3f}R payoff={aw/al if al else 0:.2f}')
    P(f'expectancy={exp:.3f}R ({np.mean([x["net_pct"] for x in trs]):.2f}%/trade) t={tstat:.2f} PF={pf:.2f} maxConsecLoss={mc} kelly={kelly*100:.1f}%')
    return dict(n=n, wr=round(wr*100,1), exp=round(exp,3), t=round(tstat,2), pf=round(pf,2), kelly=round(kelly*100,1), mc=mc)

P('\n========== THORP: fib-dip pullback signal (5y, net 10bp RT) ==========')
all_tr = {}
for t, d in data.items():
    if t == 'SPY': continue
    all_tr[t] = run_ticker(t, d)
    P(f'{t}: {len(all_tr[t])} trades')

pool9 = [x for t in BASE if t != 'SPY' for x in all_tr.get(t, [])]
pool9.sort(key=lambda x: x['entry_date'])
stats(pool9, 'BASE-9 POOLED (comparability vs prior runs)')
pool11 = [x for v in all_tr.values() for x in v]
pool11.sort(key=lambda x: x['entry_date'])
s11 = stats(pool11, 'POOL-11 POOLED (base9 + MKSI + AMKR)')

for t in ['MKSI', 'AMKR']:
    tr = sorted(all_tr.get(t, []), key=lambda x: x['entry_date'])
    stats(tr, f'{t} only (same setup class: uptrend + fib 38.2-50% pullback)')
    if len(tr) >= 8:
        mid = len(tr)//2
        stats(tr[:mid], f'{t} H1 (older)')
        stats(tr[mid:], f'{t} H2 (recent)')
        by = {}
        for x in tr: by.setdefault(x['entry_date'][:4], []).append(x)
        for y in sorted(by): stats(by[y], f'{t} year {y}')

# ---------- plan economics: current bars ----------
P('\n========== PLAN ECONOMICS (current bars) ==========')
for t in ['MKSI', 'AMKR']:
    d = data[t]; dm = build(d)
    last = dm.iloc[-1]
    px = float(last['Close']); a14 = float(last['atr14'])
    s20 = float(last['sma20']); s50 = float(last['sma50']); s100 = float(last['sma100'])
    vr = float(d['Volume'].iloc[-1]) / float(d['Volume'].rolling(20, min_periods=15).mean().iloc[-2])
    P(f'{t}: close={px:.2f} O={float(last["Open"]):.2f} H={float(last["High"]):.2f} L={float(last["Low"]):.2f} '
      f'ATR={a14:.2f} RSI={float(last["rsi14"]):.1f} vol={vr:.2f}x | SMA20={s20:.2f} SMA50={s50:.2f} SMA100={s100:.2f}')

# MKSI swing plan: entry 255-274, SL = fill - 19.78 (2xATR), TP1 1.5R, TP2 2.5R, 1% of 2500 = $25 risk
mk = data['MKSI']; mklast = build(mk).iloc[-1]
e = float(mklast['Close'])
in_zone = 255 <= e <= 274
sl = e - 19.78
tp1 = e + 1.5*19.78; tp2 = e + 2.5*19.78
shares = int(25 // 19.78)
P(f'MKSI plan: price {e:.2f} in $255-274 = {in_zone} | SL {sl:.2f} (fill-19.78) | TP1 {tp1:.2f} (1.5R) TP2 {tp2:.2f} (2.5R)')
P(f'MKSI sizing @ $25 risk (1% of $2,500): {shares} sh = ${shares*e:,.0f} notional, risk ${shares*19.78:.2f} = {shares*19.78/2500*100:.2f}% of budget')
P(f'MKSI breakeven WR at 1.5R = 40.0%, at 2.5R = 28.6% | fibs: 78.6%={float(mklast["fib618"]):.2f} 50%={float(mklast["fib50"]):.2f} 38.2%={float(mklast["fib382"]):.2f} 3mHigh={float(mklast["h3m"]):.2f}')

# AMKR plan (Oct 7 panel): buy-stop 52.60 aggressive / 56.60 structural, vol >=1x, stop 51.00 / 49.00
am = data['AMKR']; amlast = build(am).iloc[-1]
e2 = float(amlast['Close']); h2 = float(amlast['High'])
vr2 = float(am['Volume'].iloc[-1]) / float(am['Volume'].rolling(20, min_periods=15).mean().iloc[-2])
P(f'AMKR: close {e2:.2f} high {h2:.2f} vs trigger 52.60 -> intraday fill {h2 >= 52.60}, close-confirmation {e2 >= 52.60}, vol {vr2:.2f}x (need >=1.0x)')
for name, st, tp_ in [('tight (51.00 candle low)', 51.00, 54.02), ('wide (49.00 fib786)', 49.00, 54.02), ('wide->TP2', 49.00, 57.53)]:
    risk = e2 - st; rew = tp_ - e2
    n_sh = int(25 // risk) if risk > 0 else 0
    P(f'AMKR entry {e2:.2f} stop {st:.2f} ({name}): risk={risk:.2f} reward={tp_:.2f} R:R={rew/risk:.2f}:1 '
      f'breakevenWR={1/(1+rew/risk)*100:.1f}% | 1% size = {n_sh} sh (${n_sh*e2:,.0f})')

# ---------- Wyckoff per ticker ----------
def wyckoff(t):
    P(f'\n--- WYCKOFF / VOLUME PROFILE ({t} 1y) ---')
    m = data[t]
    m1 = m.tail(252)
    px = float(m1['Close'].iloc[-1])
    lo = float(m1['Low'].min()); hi = float(m1['High'].max())
    P(f'1y range: {lo:.2f} ({m1["Low"].idxmin().date()}) - {hi:.2f} ({m1["High"].idxmax().date()})')
    m3 = m.tail(63)
    P(f'3m high: {float(m3["High"].max()):.2f} on {m3["High"].idxmax().date()} | 3m low: {float(m3["Low"].min()):.2f} on {m3["Low"].idxmin().date()}')
    P(f'current: {px:.2f} | dist from 3m high: {(px/float(m3["High"].max())-1)*100:.1f}% | off 3m low: {(px/float(m3["Low"].min())-1)*100:.1f}%')
    m60 = m.tail(63)
    P(f'60d range: {float(m60["Low"].min()):.2f} - {float(m60["High"].max()):.2f}; position in range = {(px-float(m60["Low"].min()))/(float(m60["High"].max())-float(m60["Low"].min()))*100:.0f}%')
    bins = 50
    lo_, hi_ = float(m1['Close'].min()), float(m1['Close'].max())
    edges = np.linspace(lo_, hi_, bins+1); centers = (edges[:-1]+edges[1:])/2
    vp = np.zeros(bins)
    for c_, v in zip(m1['Close'].values, m1['Volume'].values):
        k = min(bins-1, max(0, int((c_-lo_)/max(hi_-lo_, 1e-9)*(bins-1))))
        vp[k] += v
    vpoc = centers[int(np.argmax(vp))]
    order = np.argsort(vp)[::-1]; cum = 0; total = vp.sum(); va_idx = []
    for k in order:
        va_idx.append(k); cum += vp[k]
        if cum >= 0.70*total: break
    vah = centers[max(va_idx)]; val = centers[min(va_idx)]
    P(f'1y VPOC={vpoc:.2f} VAH={vah:.2f} VAL={val:.2f} | price vs VPOC: {(px/vpoc-1)*100:+.1f}% | in value area: {val <= px <= vah}')
    lo3, hi3 = float(m3['Close'].min()), float(m3['Close'].max())
    e3 = np.linspace(lo3, hi3, 41); c3 = (e3[:-1]+e3[1:])/2
    vp3 = np.zeros(40)
    for c_, v in zip(m3['Close'].values, m3['Volume'].values):
        k = min(39, max(0, int((c_-lo3)/max(hi3-lo3, 1e-9)*39)))
        vp3[k] += v
    vpoc3 = c3[int(np.argmax(vp3))]
    o3 = np.argsort(vp3)[::-1]; cum = 0; va3 = []
    for k in o3:
        va3.append(k); cum += vp3[k]
        if cum >= 0.70*vp3.sum(): break
    P(f'3m VPOC={vpoc3:.2f} | 3m VAH={c3[max(va3)]:.2f} VAL={c3[min(va3)]:.2f} | price vs 3m VPOC: {(px/vpoc3-1)*100:+.1f}%')
    tp_ = (m1['High'] + m1['Low'] + m1['Close']) / 3
    raw_mf = tp_ * m1['Volume']; dtp = tp_.diff()
    posf = raw_mf.where(dtp > 0, 0.0).rolling(14).sum(); negf = raw_mf.where(dtp < 0, 0.0).rolling(14).sum()
    mfi = 100 - 100 / (1 + posf / negf.replace(0, np.nan))
    P(f'MFI14={float(mfi.iloc[-1]):.1f}')
    mf = ((m1['Close'] - m1['Low']) - (m1['High'] - m1['Close'])) / (m1['High'] - m1['Low']).replace(0, np.nan)
    cmf = (mf * m1['Volume']).rolling(20).sum() / m1['Volume'].rolling(20).sum()
    P(f'CMF20={float(cmf.iloc[-1]):.3f} (5d avg {float(cmf.tail(5).mean()):+.3f})')
    obv = (np.sign(m1['Close'].diff()).fillna(0) * m1['Volume']).cumsum()
    x = np.arange(60); slope = np.polyfit(x, obv.values[-60:], 1)[0]
    P(f'OBV 60d slope: {slope:+,.0f}/day ({"RISING = accumulation" if slope > 0 else "FALLING = distribution"})')
    upv = m1['Volume'].tail(30)[m1['Close'].diff().tail(30) > 0].sum()
    dnv = m1['Volume'].tail(30)[m1['Close'].diff().tail(30) < 0].sum()
    P(f'30d up-volume vs down-volume: {upv/1e6:.0f}M vs {dnv/1e6:.0f}M (ratio {upv/max(dnv,1):.2f})')
    avgv = m1['Volume'].rolling(50).mean()
    dd = 0
    for i in range(-25, 0):
        if m1['Close'].iloc[i] < m1['Close'].iloc[i-1] and m1['Volume'].iloc[i] > avgv.iloc[i-1]:
            dd += 1
    P(f'distribution days (last 25): {dd}')
    h1 = float(m1['High'].tail(10).max()); l1 = float(m1['Low'].tail(10).min())
    h0 = float(m1['High'].iloc[-20:-10].max()); l0 = float(m1['Low'].iloc[-20:-10].min())
    P(f'10d: H={h1:.2f} L={l1:.2f} | prior 10d: H={h0:.2f} L={l0:.2f} -> {"HH/HL (markup)" if h1>h0 and l1>l0 else "LH/LL or mixed"}')
    dm = build(m); last = dm.iloc[-1]
    s20 = float(last['sma20']); s50 = float(last['sma50']); s100 = float(last['sma100'])
    P(f'price vs SMA20/50/100: {px/s20-1:+.1%} / {px/s50-1:+.1%} / {px/s100-1:+.1%}')
    P(f'SMA stack: {"20>50>100 bullish" if s20>s50>s100 else ("20<50 mixed" if s20<s50 else "other")} | SMA20={s20:.2f} SMA50={s50:.2f} SMA100={s100:.2f}')
    leg_hi = float(m1['High'].tail(30).max()); leg_lo = float(m1['Low'].tail(30).min())
    P(f'30d leg {leg_lo:.2f}->{leg_hi:.2f}, current retrace = {(leg_hi-px)/(leg_hi-leg_lo)*100:.1f}%')
    # last candle pattern
    lb = dm.iloc[-1]
    body = float(lb['Close'])-float(lb['Open']); rng_ = float(lb['High'])-float(lb['Low'])
    cpos = (float(lb['Close'])-float(lb['Low']))/max(rng_,1e-9)
    where_ = 'upper third' if cpos > 0.66 else ('lower third' if cpos < 0.33 else 'mid')
    P(f'last bar: body {body:+.2f} ({body/rng_*100 if rng_ else 0:.0f}% of range), close {float(lb["Close"]):.2f}, close in {where_}')
    return vpoc, vah, val

for t in ['MKSI', 'AMKR', 'ZS']:
    wyckoff(t)

# ---------- Medallion factors ----------
def medallion(t):
    P(f'\n--- MEDALLION SIGNAL QUALITY ({t}) ---')
    m = data[t]; dm = build(m)
    last = dm.iloc[-1]
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
    f.append(('Regime (px>SMA20 & SMA50)', f'{px>s20 and px>s50}', +1 if (px > s20 and px > s50) else -1, 'uptrend aligned' if (px > s20 and px > s50) else 'not fully aligned'))
    f.append(('SMA stack 20>50', f'{s20:.1f}>{s50:.1f}', +1 if s20 > s50 else -1, 'fast above slow' if s20 > s50 else 'fast below slow'))
    f.append(('Price vs SMA100', f'{px/s100-1:+.1%}', +1 if px > s100 else -1, 'above 100d structure' if px > s100 else 'below 100d'))
    f.append(('RSI14', f'{r:.1f}', +0.5 if 45 <= r <= 65 else 0, 'neutral-cool' if 45 <= r <= 65 else 'out of band'))
    f.append(('Vol vs 20d', f'{vr:.2f}x', -1 if vr < 0.7 else (0 if vr < 1.2 else 1), 'no initiative volume' if vr < 1.2 else 'initiative volume'))
    f.append((f'5d pattern', f'{red}R/{green}G', +0.5 if green > red else -0.5, 'net green week' if green > red else 'net red week'))
    f.append(('Price vs 1y VPOC', f'{(px/vpoc-1)*100:+.1f}%', +1 if px > vpoc else -1, 'above VPOC = acceptance' if px > vpoc else 'below VPOC = rejection'))
    f.append(('Price in value area', 'yes' if val <= px <= vah else 'no', 0, 'inside 1y value area' if val <= px <= vah else 'outside'))
    f.append(('60d range position', f'{posr:.0f}%', 0 if 20 <= posr <= 80 else (-1 if posr < 20 else +1), 'mid-range balance' if 20 <= posr <= 80 else 'range extreme'))
    f.append(('30d retrace depth', f'{retr:.0f}%', -0.5 if retr > 50 else 0, 'deep pullback >50%' if retr > 50 else 'shallow/mid pullback'))
    comp = sum(x[2] for x in f)
    for x in f: P('  ', x[0], '=', x[1], '->', x[2], '|', x[3])
    P(f'composite raw sum = {comp:+.1f} (scale roughly -10..+10) -> ' + ('POSITIVE confluence' if comp >= 3 else ('NEGATIVE' if comp <= -3 else 'WEAK/NEUTRAL confluence')))

for t in ['MKSI', 'AMKR', 'ZS']:
    medallion(t)

# ---------- 11-factor gate (daily bars) ----------
P('\n========== 11-FACTOR GATE (confluence_score.py on daily bars, funding=neutral) ==========')
for t in ['MKSI', 'AMKR', 'AMZN', 'GOOG', 'GEV', 'ZS']:
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
z = data['ZS']; dz = build(z)
last = dz.iloc[-1]
px = float(last['Close']); a14 = float(last['atr14'])
vr = float(z['Volume'].iloc[-1]) / float(z['Volume'].rolling(20, min_periods=15).mean().iloc[-2])
h3 = float(z['High'].tail(63).max()); h3d = z['High'].tail(63).idxmax().date()
h1y = float(z['High'].tail(252).max()); h1yd = z['High'].tail(252).idxmax().date()
m3 = z.tail(63)
lo3, hi3 = float(m3['Close'].min()), float(m3['Close'].max())
e3 = np.linspace(lo3, hi3, 41); c3 = (e3[:-1]+e3[1:])/2
vp3 = np.zeros(40)
for c_, v in zip(m3['Close'].values, m3['Volume'].values):
    k = min(39, max(0, int((c_-lo3)/max(hi3-lo3, 1e-9)*39))); vp3[k] += v
vpoc3 = c3[int(np.argmax(vp3))]
# MACD + stoch
ema12 = z['Close'].ewm(span=12, adjust=False).mean(); ema26 = z['Close'].ewm(span=26, adjust=False).mean()
macd = ema12 - ema26; sig = macd.ewm(span=9, adjust=False).mean(); hist = macd - sig
ll14 = z['Low'].rolling(14).min(); hh14 = z['High'].rolling(14).max()
stoch = 100 * (z['Close'] - ll14) / (hh14 - ll14).replace(0, np.nan)
trail = px - 2*a14
pnl = (px - 150.0) * 15
P(f'last bar {dz.index[-1].date()}: O={float(last["Open"]):.2f} H={float(last["High"]):.2f} L={float(last["Low"]):.2f} C={px:.2f} vol={vr:.2f}x20d')
P(f'RSI={float(last["rsi14"]):.1f} StochK={float(stoch.iloc[-1]):.1f} MACD hist={float(hist.iloc[-1]):.3f} ATR={a14:.2f}')
P(f'3m high {h3:.2f} ({h3d}) | 1y high {h1y:.2f} ({h1yd}) | dist to 3m high {(px/h3-1)*100:+.1f}% | 3m VPOC {vpoc3:.2f} (price {(px/vpoc3-1)*100:+.1f}%)')
P(f'2xATR trail = {trail:.2f} | position P&L {pnl:+,.2f} ({(px/150-1)*100:+.1f}%) on 15 sh cost $2,250')
P(f'if trimmed 5 sh @ {px:.2f}: realize ${(px-150)*5:+,.2f}; remaining 10 sh, trail {trail:.2f} = locked min ${(trail-150)*10:+,.2f}')
last5 = dz.tail(5)
for dt, row in last5.iterrows():
    P(f'ZS {dt.date()} O={row["Open"]:.2f} H={row["High"]:.2f} L={row["Low"]:.2f} C={row["Close"]:.2f}')

with open(OUT, 'w') as f:
    f.write('\n'.join(lines))
print('WROTE', OUT)
