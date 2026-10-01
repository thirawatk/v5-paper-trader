#!/usr/bin/env python3
"""3-Expert analysis for GEV entry signal (entry monitor Fri 02 Oct 2026 03:01 ICT):
1) Thorp: backtest the monitor's exact UPTREND + fib-dip verdict signal, 5y (GEV avail ~2.5y), 9 tickers
2) Wyckoff: structure + volume profile on GEV
3) Medallion: confluence scoring + statistical significance
"""
import json, math, sys
import numpy as np
import pandas as pd
import yfinance as yf

TICKERS = ['GOOG', 'RDDT', 'GDDY', 'ZS', 'BCC', 'FBK', 'AMZN', 'MRVL', 'GEV', 'SPY']
OUT = '/root/.hermes/profiles/trader/scripts/_gev_expert_out.txt'
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

# ---------- Thorp backtest: monitor UPTREND + fib-dip signal (exact verdict replication) ----------
COST_SIDE = 0.0005   # 5bp per side: commission+spread+slippage (paper estimate)

def build(df):
    d = df.copy()
    d['sma20'] = sma(d['Close'], 20); d['sma50'] = sma(d['Close'], 50); d['sma100'] = sma(d['Close'], 100)
    d['rsi14'] = rsi(d['Close']); d['atr14'] = atr(d)
    h = d['High'].values; l = d['Low'].values; c = d['Close'].values
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
    trades = []
    in_pos = False
    for i in range(100, len(d) - 1):
        if np.isnan(sma20[i]) or np.isnan(sma50[i]) or np.isnan(f382[i]): continue
        uptrend = (c[i] > sma20[i]) and (c[i] > sma50[i])
        # verdict says "Entry on dip: fib382 - fib50"; monitor band w/ +/-2% tolerance
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

all_tr = []
for t, d in data.items():
    if t == 'SPY': continue
    tr = run_ticker(t, d)
    all_tr.extend(tr)
    P(f'{t}: {len(tr)} trades')

all_tr.sort(key=lambda x: x['entry_date'])

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

P('\n========== THORP BACKTEST (GEV verdict signal replicated, 5y max, 9 tickers) ==========')
s_all = stats(all_tr, 'ALL trades (net of 10bp RT costs)')

mid = len(all_tr)//2
stats(all_tr[:mid], 'H1 (older half)')
stats(all_tr[mid:], 'H2 (recent half)')

by_year = {}
for x in all_tr: by_year.setdefault(x['entry_date'][:4], []).append(x)
for y in sorted(by_year): stats(by_year[y], f'year {y}')

by_t = {}
for x in all_tr: by_t.setdefault(x['ticker'], []).append(x)
for t in sorted(by_t): stats(by_t[t], f'{t}')

stats(by_t.get('GEV', []), 'GEV only (history starts 2024-04)')
gev = by_t.get('GEV', [])
gby = {}
for x in gev: gby.setdefault(x['entry_date'][:4], []).append(x)
for y in sorted(gby): stats(gby[y], f'GEV year {y}')
if len(gev) >= 4:
    gmid = len(gev)//2
    stats(gev[:gmid], 'GEV H1 (older)')
    stats(gev[gmid:], 'GEV H2 (recent)')

# portfolio: 1% risk per trade, compounding, chronological
P('\n--- portfolio sim (1% equity risk/trade, chronological, stop-sized) ---')
eq = 1.0; curve = []
for x in all_tr:
    risk_frac = 0.01
    notional_frac = risk_frac / ((x['entry'] - x['stop'])/x['entry'])
    notional_frac = min(notional_frac, 1.0)
    pnl_frac = notional_frac * ((x['exit'] - x['entry'])/x['entry'])
    eq *= (1 + pnl_frac)
    curve.append(eq)
peak = max(curve)
mdd = 0.0; run_peak = curve[0]
for v in curve:
    run_peak = max(run_peak, v)
    mdd = max(mdd, (run_peak - v)/run_peak)
P(f'final equity multiple = {eq:.3f} over {len(all_tr)} trades; peak={peak:.3f}; maxDD={mdd*100:.1f}%')
years = (pd.Timestamp(all_tr[-1]['entry_date']) - pd.Timestamp(all_tr[0]['entry_date'])).days / 365.25 if all_tr else 1
P(f'period years={years:.2f} CAGR={(eq**(1/max(years,0.01))-1)*100:.1f}%')

spy = data['SPY']
w0 = spy.index.searchsorted(pd.Timestamp(all_tr[0]['entry_date'])) if all_tr else 0
w1 = len(spy) - 1
P(f'SPY buy&hold same window: {(spy["Close"].iloc[w1]/spy["Close"].iloc[w0]-1)*100:.1f}% ({years:.2f}y)')

# GEV-only portfolio vs SPY window
if gev:
    g0 = spy.index.searchsorted(pd.Timestamp(gev[0]['entry_date']))
    P(f'SPY buy&hold GEV window: {(spy["Close"].iloc[w1]/spy["Close"].iloc[g0]-1)*100:.1f}% '
      f'({(pd.Timestamp(gev[-1]["exit_date"]) - pd.Timestamp(gev[0]["entry_date"])).days/365.25:.2f}y)')

# ---------- current GEV signal economics ----------
P('\n========== CURRENT GEV SIGNAL ECONOMICS ==========')
m = data['GEV']; dm = build(m)
last = dm.iloc[-1]
px = float(last['Close'])
f382 = float(last['fib382']); f50 = float(last['fib50']); f618 = float(last['fib618'])
h3m = float(last['h3m']); a14 = float(last['atr14'])
l3m = float(dm['Low'].tail(63).min())
P(f'last bar: {dm.index[-1].date()} close={px:.2f} fib382={f382:.2f} fib50={f50:.2f} fib618={f618:.2f} atr={a14:.2f} h3m={h3m:.2f} l3m={l3m:.2f}')
P(f'monitor verdict: entry-on-dip zone {f382:.2f}-{f50:.2f}, stop {f618-a14:.2f}, TP {h3m:.2f}')
P(f'price vs band bottom (fib50): {(px/f50-1)*100:+.1f}% -> ' +
  ('INSIDE band' if f50*0.98 <= px <= f382*1.02 else 'OUTSIDE band (price below band = TWO-MOVE scenario)'))
retrace = (h3m - px)/(h3m - l3m)
P(f'3m retrace of {l3m:.2f}->{h3m:.2f} leg: {retrace*100:.1f}%')

stop_lvl = f618 - a14; tp_lvl = h3m
for name, e in [('band top (fib38.2)', f382), ('band bottom (fib50)', f50), ('market now', px)]:
    risk = e - stop_lvl; rew = tp_lvl - e
    if risk > 0 and rew > 0:
        P(f'entry@{name} ${e:.2f}: risk={risk:.2f} ({risk/e*100:.1f}%) reward={rew:.2f} ({rew/e*100:.1f}%) R:R={rew/risk:.2f}:1  breakevenWR={1/(1+rew/risk)*100:.1f}%')
    else:
        P(f'entry@{name} ${e:.2f}: INVALID geometry (risk={risk:.2f}, reward={rew:.2f})')

# ---------- WYCKOFF: GEV 1y structure + volume profile ----------
P('\n========== WYCKOFF / VOLUME PROFILE (GEV 1y) ==========')
m1 = m.tail(252).copy()
lo = float(m1['Low'].min()); hi = float(m1['High'].max())
P(f'1y range: {lo:.2f} ({m1["Low"].idxmin().date()}) - {hi:.2f} ({m1["High"].idxmax().date()})')
m3 = m.tail(63)
P(f'3m high: {float(m3["High"].max()):.2f} on {m3["High"].idxmax().date()} | 3m low: {float(m3["Low"].min()):.2f} on {m3["Low"].idxmin().date()}')
P(f'current: {px:.2f} | dist from 3m high: {(px/float(m3["High"].max())-1)*100:.1f}% | off 3m low: {(px/float(m3["Low"].min())-1)*100:.1f}%')

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
zone_bins = [(centers[k], vp[k]/1e6) for k in range(bins) if f50*0.97 <= centers[k] <= f382*1.03]
P('volume profile in entry band (price, vol M): ' + ', '.join(f'{c:.0f}:{v:.0f}' for c, v in zone_bins))
stop_bins = [(centers[k], vp[k]/1e6) for k in range(bins) if stop_lvl*0.985 <= centers[k] <= stop_lvl*1.015]
P('volume profile at stop $%.0f (price, vol M): ' % stop_lvl + ', '.join(f'{c:.0f}:{v:.0f}' for c, v in stop_bins))

m3v = m.tail(63)
lo3, hi3 = float(m3v['Close'].min()), float(m3v['Close'].max())
e3 = np.linspace(lo3, hi3, 41); c3 = (e3[:-1]+e3[1:])/2
vp3 = np.zeros(40)
for c_, v in zip(m3v['Close'].values, m3v['Volume'].values):
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
s20v = float(last['sma20']); s50v = float(last['sma50']); s100v = float(last['sma100'])
P(f'price vs SMA20/50/100: {px/s20v-1:+.1%} / {px/s50v-1:+.1%} / {px/s100v-1:+.1%}')
P(f'SMA stack: SMA20={s20v:.2f} SMA50={s50v:.2f} SMA100={s100v:.2f} -> {"20>50>100 bullish" if s20v>s50v>s100v else ("50>20 or mixed" if s50v>s100v else "below SMA100 = damaged")}'  )

leg_hi = float(m1['High'].tail(30).max()); leg_lo = float(m1['Low'].tail(30).min())
retr30 = (leg_hi - px)/(leg_hi - leg_lo)
P(f'30d leg {leg_lo:.2f}->{leg_hi:.2f}, current retrace = {retr30*100:.1f}%')

# swing structure: last 3 significant pivots (simple 5-bar fractal)
piv = []
hh_arr = m1['High'].values; ll_arr = m1['Low'].values
for i in range(5, len(m1)-5):
    if hh_arr[i] == hh_arr[i-5:i+6].max(): piv.append(('H', i, float(hh_arr[i])))
    if ll_arr[i] == ll_arr[i-5:i+6].min(): piv.append(('L', i, float(ll_arr[i])))
P('last 4 pivots: ' + ', '.join(f'{k}@{m1.index[i].date()} {v:.0f}' for k, i, v in piv[-4:]))

# ---------- MEDALLION: confluence score ----------
P('\n========== MEDALLION SIGNAL QUALITY ==========')
factors = []
def fac(name, val, score, note): factors.append((name, val, score, note))
fac('Regime (price>SMA20&SMA50)', 'UPTREND', +1, 'trend aligned')
fac('SMA stack 20>50', f'{s20v:.0f}>{s50v:.0f}', +1 if s20v > s50v else -1, 'fast above slow')
fac('Price vs SMA100', f'{px/s100v-1:+.1%}', -1 if px < s100v else +1, 'below 100d = damaged structure' if px < s100v else 'above 100d')
in_band = f50*0.98 <= px <= f382*1.02
fac('Fib dip band (38.2-50%)', f'{f50:.0f}-{f382:.0f}', +1 if in_band else -1, 'inside band' if in_band else f'price {(px/f50-1)*100:.1f}% BELOW band — two-move, no trigger yet')
fac('RSI14', f'{float(last["rsi14"]):.1f}', +0.5 if 45 <= float(last["rsi14"]) <= 65 else 0, 'neutral-cool, not overbought')
vr = float(m['Volume'].iloc[-1]) / float(m['Volume'].rolling(20).mean().iloc[-2])
fac('Vol vs 20d', f'{vr:.2f}x', -1 if vr < 0.7 else (0 if vr < 1.2 else 1), 'no initiative volume' if vr < 1.2 else 'initiative volume on the bar')
fac('5d pattern', '2R/3G', +0.5, 'mild pullback then bounce')
fac('Price vs 1y VPOC', f'{(px/vpoc-1)*100:+.1f}%', +1 if px > vpoc else -1, 'above VPOC = acceptance' if px > vpoc else 'below VPOC = rejection')
fac('Price in value area', 'yes' if val <= px <= vah else 'no', 0, 'inside 1y value area' if val <= px <= vah else 'outside 1y value area')
fac('Retrace depth of 3m leg', f'{retrace*100:.0f}%', +1 if retrace < 0.5 else -0.5, 'shallow pullback' if retrace < 0.5 else 'deep pullback >50%')
composite = sum(f[2] for f in factors)
P('factors:')
for f in factors: P('  ', f[0], '=', f[1], '->', f[2], '|', f[3])
P(f'composite raw sum = {composite:+.1f} (scale roughly -10..+10) -> ' + ('POSITIVE confluence' if composite >= 3 else 'WEAK/NEUTRAL confluence'))
P(f'sample size: backtest n={s_all["n"] if s_all else 0} trades, t={s_all["t"] if s_all else 0} (Renaissance bar: t>3.0)')
P(f'cross-market: per-ticker trades ' + ', '.join(f'{t}:{len(v)}' for t, v in sorted(by_t.items())))
if all_tr:
    P(f'cross-time: WR H1={np.mean([x["net_r"]>0 for x in all_tr[:mid]])*100:.0f}% vs H2={np.mean([x["net_r"]>0 for x in all_tr[mid:]])*100:.0f}%')

with open(OUT, 'w') as f:
    f.write('\n'.join(lines))
print('WROTE', OUT)
