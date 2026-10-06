#!/usr/bin/env python3
"""3-Expert analysis for AMZN entry signal (entry monitor Tue 06 Oct 2026 22:00 ICT):
1) Thorp: backtest the monitor's exact SMA50-reclaim trigger, 5y, 9 monitor tickers (2 variants: with/without volume confirmation)
2) Wyckoff: structure + volume profile on AMZN
3) Medallion: confluence scoring + statistical significance
"""
import math
import numpy as np
import pandas as pd
import yfinance as yf

TICKERS = ['GOOG', 'RDDT', 'GDDY', 'ZS', 'BCC', 'FBK', 'AMZN', 'MRVL', 'GEV', 'SPY']
OUT = '/root/.hermes/profiles/trader/scripts/_amzn_expert_out.txt'
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

# ---------- Thorp backtest: AMZN SMA50-reclaim trigger ----------
COST_SIDE = 0.0005   # 5bp per side: commission+spread+slippage (paper estimate)

def build(df):
    d = df.copy()
    d['sma20'] = sma(d['Close'], 20); d['sma50'] = sma(d['Close'], 50); d['sma100'] = sma(d['Close'], 100)
    d['rsi14'] = rsi(d['Close']); d['atr14'] = atr(d)
    d['vol20'] = d['Volume'].rolling(20, min_periods=15).mean().shift(1)
    return d

def run_ticker(t, d, vol_confirm):
    d = build(d)
    h = d['High'].values; l = d['Low'].values; o = d['Open'].values; c = d['Close'].values
    v = d['Volume'].values
    idx = d.index
    sma50 = d['sma50'].values; sma100 = d['sma100'].values; atr14 = d['atr14'].values
    vol20 = d['vol20'].values
    trades = []
    in_pos = False
    for i in range(100, len(d) - 1):
        if np.isnan(sma50[i]) or np.isnan(sma100[i]) or np.isnan(vol20[i]) or np.isnan(atr14[i]): continue
        # trigger: close crosses above SMA50, structure intact (close > SMA100)
        if not (c[i-1] <= sma50[i-1] and c[i] > sma50[i] and c[i] > sma100[i]): continue
        if vol_confirm and not (v[i] > 1.0 * vol20[i]): continue
        if in_pos: continue
        entry = c[i]
        stop = float(min(l[i-10:i]))                 # below prior 10-bar swing low (Wyckoff candle-low rule)
        if stop >= entry - 0.2 * atr14[i]: stop = entry - 1.0 * atr14[i]
        if entry - stop > 2.0 * atr14[i]: stop = entry - 2.0 * atr14[i]   # cap risk at 2x ATR
        tp = entry + 2.0 * (entry - stop)            # fixed 2R target
        if not (stop > 0) or entry <= stop: continue
        exit_px = None; exit_i = None; reason = None
        for j in range(i+1, min(i+1+63, len(d))):
            if l[j] <= stop:
                exit_px = o[j] if o[j] < stop else stop
                exit_i = j; reason = 'STOP'; break
            if h[j] >= tp:
                exit_px = o[j] if o[j] > tp else tp
                exit_i = j; reason = 'TP'; break
        if exit_px is None:
            j = min(i+1+63-1, len(d)-1)
            exit_px = c[j]; exit_i = j; reason = 'TIME'
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
    exp_pct = np.mean([x['net_pct'] for x in trs])
    mc = cur = 0
    for x in trs:
        if x['net_r'] <= 0: cur += 1; mc = max(mc, cur)
        else: cur = 0
    kelly = max(0.0, wr - (1-wr)/(aw/al if al > 0 else 1))
    P(f'--- {label} ---')
    P(f'n={n} WR={wr*100:.1f}% avgWin={aw:.3f}R avgLoss={al:.3f}R payoff={aw/al if al else 0:.2f}')
    P(f'expectancy={exp:.3f}R ({exp_pct:.2f}%/trade) t={tstat:.2f} PF={pf:.2f} maxConsecLoss={mc} kelly={kelly*100:.1f}%')
    P(f'trades by reason: TP={sum(1 for x in trs if x["reason"]=="TP")} STOP={sum(1 for x in trs if x["reason"]=="STOP")} TIME={sum(1 for x in trs if x["reason"]=="TIME")}')
    P(f'avg days in trade: {np.mean([x["days"] for x in trs]):.1f}')
    return dict(n=n, wr=round(wr*100,1), exp=round(exp,3), t=round(tstat,2), pf=round(pf,2), kelly=round(kelly*100,1), mc=mc)

def portfolio_sim(all_tr, label):
    P(f'--- portfolio sim {label} (1% equity risk/trade, chronological, stop-sized) ---')
    if not all_tr: return
    eq = 1.0; curve = []
    for x in all_tr:
        notional_frac = min(0.01 / ((x['entry'] - x['stop'])/x['entry']), 1.0)
        pnl_frac = notional_frac * ((x['exit'] - x['entry'])/x['entry'])
        eq *= (1 + pnl_frac); curve.append(eq)
    mdd = 0.0; run_peak = curve[0]
    for v in curve:
        run_peak = max(run_peak, v); mdd = max(mdd, (run_peak - v)/run_peak)
    years = (pd.Timestamp(all_tr[-1]['entry_date']) - pd.Timestamp(all_tr[0]['entry_date'])).days / 365.25
    P(f'final equity multiple = {eq:.3f} over {len(all_tr)} trades; maxDD={mdd*100:.1f}%; CAGR={(eq**(1/max(years,0.01))-1)*100:.1f}% ({years:.2f}y)')
    spy = data['SPY']
    w0 = spy.index.searchsorted(pd.Timestamp(all_tr[0]['entry_date']))
    w1 = len(spy) - 1
    P(f'SPY buy&hold same window: {(spy["Close"].iloc[w1]/spy["Close"].iloc[w0]-1)*100:.1f}%')

def full_backtest(vol_confirm, label):
    P(f'\n========== THORP BACKTEST — {label} ==========')
    all_tr = []
    for t, d in data.items():
        if t == 'SPY': continue
        tr = run_ticker(t, d, vol_confirm)
        all_tr.extend(tr)
    all_tr.sort(key=lambda x: x['entry_date'])
    s_all = stats(all_tr, 'ALL trades (net of 10bp RT costs)')
    mid = len(all_tr)//2
    stats(all_tr[:mid], 'H1 (older half)'); stats(all_tr[mid:], 'H2 (recent half)')
    by_year = {}
    for x in all_tr: by_year.setdefault(x['entry_date'][:4], []).append(x)
    for y in sorted(by_year): stats(by_year[y], f'year {y}')
    by_t = {}
    for x in all_tr: by_t.setdefault(x['ticker'], []).append(x)
    for t in sorted(by_t): stats(by_t[t], t)
    stats(by_t.get('AMZN', []), 'AMZN only')
    am = by_t.get('AMZN', [])
    aby = {}
    for x in am: aby.setdefault(x['entry_date'][:4], []).append(x)
    for y in sorted(aby): stats(aby[y], f'AMZN year {y}')
    if len(am) >= 4:
        amid = len(am)//2
        stats(am[:amid], 'AMZN H1 (older)'); stats(am[amid:], 'AMZN H2 (recent)')
    portfolio_sim(all_tr, label)
    return all_tr, s_all, by_t

trA, sA, by_tA = full_backtest(False, 'VARIANT A: SMA50 reclaim + close>SMA100 (no volume filter)')
trB, sB, by_tB = full_backtest(True, 'VARIANT B: + volume > 1.0x 20d avg (monitor confirmation)')

# ---------- current AMZN signal economics ----------
P('\n========== CURRENT AMZN SIGNAL ECONOMICS ==========')
m = data['AMZN']; dm = build(m)
last = dm.iloc[-1]
px = float(last['Close']); s20 = float(last['sma20']); s50 = float(last['sma50']); s100 = float(last['sma100'])
a14 = float(last['atr14'])
P(f'last bar: {dm.index[-1].date()} close={px:.2f} SMA20={s20:.2f} SMA50={s50:.2f} SMA100={s100:.2f} ATR={a14:.2f} RSI={float(last["rsi14"]):.1f}')
vr = float(m['Volume'].iloc[-1]) / float(last['vol20']) if not np.isnan(float(last['vol20'])) else float('nan')
P(f'volume vs 20d avg: {vr:.2f}x | price vs SMA50: {(px/s50-1)*100:+.2f}% -> ' + ('ABOVE = reclaim printed' if px > s50 else 'BELOW = reclaim NOT printed'))
prior10low = float(m['Low'].tail(11).iloc[:10].min())
stop_lvl = max(prior10low, s50 - 2*a14)
if stop_lvl >= s50 - 0.2*a14: stop_lvl = s50 - 1.0*a14
h30 = float(m['High'].tail(30).max())
tp1 = h30
entry = s50
r1 = entry - stop_lvl
P(f'monitor plan: entry {entry:.2f} (SMA50 reclaim), stop {stop_lvl:.2f} (prior swing low / 2xATR cap), risk {r1:.2f} ({r1/entry*100:.1f}%)')
for name, tp_ in [('TP1 30d high', tp1), ('TP2 2.1R', entry + 2.1*r1), ('backtest TP 2R', entry + 2*r1)]:
    rew = tp_ - entry
    if rew > 0:
        P(f'{name} ${tp_:.2f}: reward={rew:.2f} ({rew/entry*100:.1f}%) R:R={rew/r1:.2f}:1 breakevenWR={1/(1+rew/r1)*100:.1f}%')

# ---------- WYCKOFF: AMZN 1y structure + volume profile ----------
P('\n========== WYCKOFF / VOLUME PROFILE (AMZN 1y) ==========')
m1 = m.tail(252).copy()
lo = float(m1['Low'].min()); hi = float(m1['High'].max())
P(f'1y range: {lo:.2f} ({m1["Low"].idxmin().date()}) - {hi:.2f} ({m1["High"].idxmax().date()})')
m3 = m.tail(63)
P(f'3m high: {float(m3["High"].max()):.2f} on {m3["High"].idxmax().date()} | 3m low: {float(m3["Low"].min()):.2f} on {m3["Low"].idxmin().date()}')
P(f'current: {px:.2f} | dist from 3m high: {(px/float(m3["High"].max())-1)*100:.1f}% | off 3m low: {(px/float(m3["Low"].min())-1)*100:.1f}%')
m60 = m.tail(63)
P(f'60d range: {float(m60["Low"].min()):.2f} - {float(m60["High"].max()):.2f}; position in range = {(px-float(m60["Low"].min()))/(float(m60["High"].max())-float(m60["Low"].min()))*100:.0f}%')

bins = 50
lo_, hi_ = float(m1['Close'].min()), float(m1['Close'].max())
edges = np.linspace(lo_, hi_, bins+1)
centers = (edges[:-1]+edges[1:])/2
vp = np.zeros(bins)
for c_, v in zip(m1['Close'].values, m1['Volume'].values):
    k = min(bins-1, max(0, int((c_-lo_)/(hi_-lo_)*(bins-1))))
    vp[k] += v
vpoc = centers[int(np.argmax(vp))]
order = np.argsort(vp)[::-1]; cum = 0; total = vp.sum(); va_idx = []
for k in order:
    va_idx.append(k); cum += vp[k]
    if cum >= 0.70*total: break
vah = centers[max(va_idx)]; val = centers[min(va_idx)]
P(f'VPOC={vpoc:.2f} VAH={vah:.2f} VAL={val:.2f} (70% value area)')
P(f'price vs VPOC: {(px/vpoc-1)*100:+.1f}% | price in value area: {val <= px <= vah}')
zone_bins = [(centers[k], vp[k]/1e6) for k in range(bins) if entry*0.96 <= centers[k] <= entry*1.04]
P('volume profile around entry $257 (price, vol M): ' + ', '.join(f'{c:.0f}:{v:.0f}' for c, v in zone_bins))

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
raw_mf = tp_ * m1['Volume']
dtp = tp_.diff()
posf = raw_mf.where(dtp > 0, 0.0).rolling(14).sum()
negf = raw_mf.where(dtp < 0, 0.0).rolling(14).sum()
mfi = 100 - 100 / (1 + posf / negf.replace(0, np.nan))
P(f'MFI14={float(mfi.iloc[-1]):.1f}')
mf = ((m1['Close'] - m1['Low']) - (m1['High'] - m1['Close'])) / (m1['High'] - m1['Low']).replace(0, np.nan)
mfv = mf * m1['Volume']
cmf = mfv.rolling(20).sum() / m1['Volume'].rolling(20).sum()
P(f'CMF20={float(cmf.iloc[-1]):.3f} (5d avg {float(cmf.tail(5).mean()):+.3f})')
obv = (np.sign(m1['Close'].diff()).fillna(0) * m1['Volume']).cumsum()
x = np.arange(60); y = obv.values[-60:]
slope = np.polyfit(x, y, 1)[0]
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
P(f'price vs SMA20/50/100: {px/s20-1:+.1%} / {px/s50-1:+.1%} / {px/s100-1:+.1%}')
P(f'SMA stack: {"20>50>100 bullish" if s20>s50>s100 else ("50>20 or mixed" if s50>s100 else "below SMA100 = damaged")}')
leg_hi = float(m1['High'].tail(30).max()); leg_lo = float(m1['Low'].tail(30).min())
P(f'30d leg {leg_lo:.2f}->{leg_hi:.2f}, current retrace = {(leg_hi-px)/(leg_hi-leg_lo)*100:.1f}%')

# ---------- MEDALLION: confluence score ----------
P('\n========== MEDALLION SIGNAL QUALITY ==========')
factors = []
def fac(name, val, score, note): factors.append((name, val, score, note))
fac('Regime (close>SMA50)', 'ABOVE' if px > s50 else 'BELOW', +1 if px > s50 else -1, 'reclaim printed' if px > s50 else 'reclaim NOT printed')
fac('SMA stack 20>50', f'{s20:.0f}>{s50:.0f}', +1 if s20 > s50 else -1, 'fast above slow')
fac('Price vs SMA100', f'{px/s100-1:+.1%}', +1 if px > s100 else -1, 'above 100d structure' if px > s100 else 'below 100d = damaged')
fac('RSI14', f'{float(last["rsi14"]):.1f}', +0.5 if 45 <= float(last['rsi14']) <= 65 else 0, 'neutral-cool' if 45 <= float(last['rsi14']) <= 65 else 'out of band')
fac('Vol vs 20d', f'{vr:.2f}x', -1 if vr < 0.7 else (0 if vr < 1.2 else 1), 'no initiative volume' if vr < 1.2 else 'initiative volume')
fac('5d pattern', '2R/3G', +0.5, 'mild pullback then bounce')
fac('Price vs 1y VPOC', f'{(px/vpoc-1)*100:+.1f}%', +1 if px > vpoc else -1, 'above VPOC = acceptance' if px > vpoc else 'below VPOC = rejection')
fac('Price in value area', 'yes' if val <= px <= vah else 'no', 0, 'inside 1y value area' if val <= px <= vah else 'outside 1y value area')
fac('60d range position', f'{(px-float(m60["Low"].min()))/(float(m60["High"].max())-float(m60["Low"].min()))*100:.0f}%', 0, 'mid-range = balance, not trend')
composite = sum(f[2] for f in factors)
P('factors:')
for f in factors: P('  ', f[0], '=', f[1], '->', f[2], '|', f[3])
P(f'composite raw sum = {composite:+.1f} (scale roughly -10..+10) -> ' + ('POSITIVE confluence' if composite >= 3 else 'WEAK/NEUTRAL confluence'))
P(f'sample size: variantB n={sB["n"] if sB else 0} trades, t={sB["t"] if sB else 0} (Renaissance bar: t>3.0); variantA n={sA["n"] if sA else 0}, t={sA["t"] if sA else 0}')
P(f'cross-market variantB: ' + ', '.join(f'{t}:{len(v)}' for t, v in sorted(by_tB.items())))
if trB:
    mid = len(trB)//2
    P(f'cross-time variantB: WR H1={np.mean([x["net_r"]>0 for x in trB[:mid]])*100:.0f}% vs H2={np.mean([x["net_r"]>0 for x in trB[mid:]])*100:.0f}%')

with open(OUT, 'w') as f:
    f.write('\n'.join(lines))
print('WROTE', OUT)
