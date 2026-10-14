import json, numpy as np, pandas as pd, yfinance as yf

t = yf.Ticker("VXUS")
h = t.history(period="2y", interval="1d").dropna()
c, v = h["Close"], h["Volume"]

d = c.diff()
up = d.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
dn = (-d.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
rsi = 100 - 100 / (1 + up / dn)

last = float(c.iloc[-1])
hi52 = float(c.iloc[-252:].max()) if len(c) >= 252 else float(c.max())
r = c.pct_change()
roll10 = r.rolling(10).sum()
z = (roll10.iloc[-1] - roll10.iloc[-252:-10].mean()) / roll10.iloc[-252:-10].std()

out = dict(
    price=round(last, 2),
    rsi=round(float(rsi.iloc[-1]), 1),
    rsi_pctile_1y=round(float((rsi.iloc[-252:] < rsi.iloc[-1]).mean()) * 100, 1),
    hi52=round(hi52, 2),
    dd_pct=round((last / hi52 - 1) * 100, 2),
    ret10=round(float(c.pct_change(10).iloc[-1]) * 100, 2),
    ret20=round(float(c.pct_change(20).iloc[-1]) * 100, 2),
    vol20_ann=round(float(r.rolling(20).std().iloc[-1] * np.sqrt(252)) * 100, 1),
    vol_ratio_5v60=round(float(v.iloc[-5:].mean() / v.iloc[-60:].mean()), 2),
    z10=round(float(z), 2),
    sma50=round(float(c.rolling(50).mean().iloc[-1]), 2),
    sma100=round(float(c.rolling(100).mean().iloc[-1]), 2),
    ema200=round(float(c.ewm(span=200).mean().iloc[-1]), 2),
    last5=[round(float(x), 2) for x in c.tail(5)],
    last5_vol=[int(x) for x in v.tail(5)],
    dates=[str(i.date()) for i in c.tail(5).index],
    dd_days=int(((c.cummax() - c) / c.cummax() > 0.0001).tail(60).sum()),
)
print(json.dumps(out, indent=1))
