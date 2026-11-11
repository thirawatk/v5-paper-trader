"""Daily OHLCV + indicator snapshot for the borderline watchlist names (12 Nov 2026)."""
import json
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, "/root/.hermes/profiles/trader/scripts")

from tvDatafeed import Interval
from tv_feed import get_client

TICKERS = {"GDDY": ["NYSE", "NASDAQ"], "FBK": ["NYSE", "NASDAQ"], "WTM": ["NYSE"]}
BARS = 260
SHOW = 12


def wilder_rsi(close, window=14):
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = np.zeros_like(close)
    avg_loss = np.zeros_like(close)
    avg_gain[window] = gain[1:window + 1].mean()
    avg_loss[window] = loss[1:window + 1].mean()
    for i in range(window + 1, len(close)):
        avg_gain[i] = (avg_gain[i - 1] * (window - 1) + gain[i]) / window
        avg_loss[i] = (avg_loss[i - 1] * (window - 1) + loss[i]) / window
    rs = np.divide(avg_gain, avg_loss, out=np.full_like(avg_gain, np.nan), where=avg_loss > 0)
    return 100 - 100 / (1 + rs)


def atr(high, low, close, window=14):
    prev_close = np.roll(close, 1)
    tr = np.maximum(high - low, np.maximum(abs(high - prev_close), abs(low - prev_close)))
    tr[0] = high[0] - low[0]
    return np.convolve(tr, np.ones(window) / window, mode="full")[:len(tr)]


def snapshot(ticker, frame):
    close = frame["close"].to_numpy(dtype=float)
    high = frame["high"].to_numpy(dtype=float)
    low = frame["low"].to_numpy(dtype=float)
    volume = frame["volume"].to_numpy(dtype=float)
    rsi = wilder_rsi(close)
    atr14 = atr(high, low, close)
    def sma(n):
        return round(float(close[-n:].mean()), 2) if len(close) >= n else None
    bars = []
    for ts, o, h, l, c, v in zip(frame.index[-SHOW:], frame["open"].to_numpy()[-SHOW:],
                                 high[-SHOW:], low[-SHOW:], close[-SHOW:], volume[-SHOW:]):
        bars.append(dict(date=str(ts)[:10], open=round(float(o), 2), high=round(float(h), 2),
                         low=round(float(l), 2), close=round(float(c), 2), vol=int(v)))
    return dict(ticker=ticker, last=round(float(close[-1]), 2),
                prev=round(float(close[-2]), 2),
                chg_pct=round((close[-1] / close[-2] - 1) * 100, 2),
                rsi14=round(float(rsi[-1]), 1),
                atr14=round(float(atr14[-1]), 2),
                sma20=sma(20), sma50=sma(50), sma100=sma(100), sma200=sma(200),
                high_52w=round(float(high[-252:].max()), 2),
                low_52w=round(float(low[-252:].min()), 2),
                avg_vol30=round(float(volume[-30:].mean())),
                bars=bars)


out = {}
for ticker, exchanges in TICKERS.items():
    for exchange in exchanges:
        try:
            frame = get_client().get_hist(symbol=ticker, exchange=exchange,
                                         interval=Interval.in_daily, n_bars=BARS)
        except Exception as exc:
            print(f"WARN {ticker}@{exchange}: {exc}", file=sys.stderr)
            continue
        if frame is None or frame.empty:
            continue
        frame = frame.dropna(subset=["close"])
        out[ticker] = snapshot(ticker, frame)
        out[ticker]["exchange"] = exchange
        break

json.dump(out, open("/root/.hermes/profiles/trader/cache/scratch/bars_1112.json", "w"), indent=1)
print(json.dumps(out, indent=1))
