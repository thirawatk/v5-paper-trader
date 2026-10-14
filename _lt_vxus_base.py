import json, numpy as np, pandas as pd, yfinance as yf

h = yf.Ticker("VXUS").history(period="10y", interval="1d").dropna()
c = h["Close"]
dd = (c / c.cummax() - 1) * 100
r = c.pct_change()

sig = dd <= -3.0          # drawdown trigger
fwd20 = c.shift(-20) / c - 1
fwd60 = c.shift(-60) / c - 1

base20 = float(fwd20.dropna().mean()) * 100
base60 = float(fwd60.dropna().mean()) * 100
cond20 = float(fwd20[sig].dropna().mean()) * 100
cond60 = float(fwd60[sig].dropna().mean()) * 100
n_sig = int(sig.sum())
n = int(len(c))
win20 = float((fwd20[sig].dropna() > 0).mean()) * 100
base_win20 = float((fwd20.dropna() > 0).mean()) * 100

# RSI<35 alternative trigger
d = c.diff()
up = d.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
dn = (-d.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
rsi = 100 - 100 / (1 + up / dn)
rsi_sig = rsi < 35

out = dict(
    days=n,
    pct_days_at_dd3=round(n_sig / n * 100, 1),
    fwd20_base=round(base20, 2), fwd20_cond=round(cond20, 2),
    fwd60_base=round(base60, 2), fwd60_cond=round(cond60, 2),
    win20_cond=round(win20, 1), win20_base=round(base_win20, 1),
    n_sig=n_sig,
    rsi35_days=int(rsi_sig.sum()),
    rsi35_freq=round(float(rsi_sig.sum()) / n * 100, 1),
    years=round(n / 252, 1),
)
print(json.dumps(out, indent=1))
