#!/usr/bin/env python3
"""Probe last daily bar OHLC + volume ratio for monitor tickers (Oct 6 close)."""
import yfinance as yf
raw = yf.download(['GEV', 'GOOG', 'AMZN', 'NVDU', 'ZS'], period='12d', interval='1d',
                  auto_adjust=False, group_by='ticker', progress=False)
for t in ['GEV', 'GOOG', 'AMZN', 'NVDU', 'ZS']:
    df = raw[t].dropna(how='all')
    d = df.iloc[-1]
    prev = df['Close'].iloc[-2]
    o, h, l, c, v = float(d['Open']), float(d['High']), float(d['Low']), float(d['Close']), float(d['Volume'])
    rng = h - l
    pos = (c - l) / rng if rng > 0 else 0
    vol20 = float(df['Volume'].iloc[-21:-1].mean())
    print(f"{t}: {df.index[-1].date()} O={o:.2f} H={h:.2f} L={l:.2f} C={c:.2f} prev={prev:.2f} "
          f"chg={(c/prev-1)*100:+.2f}% close_pos={pos*100:.0f}% vol={v/1e6:.1f}M "
          f"ratio={v/vol20:.2f}x body={(c/o-1)*100:+.2f}%")
