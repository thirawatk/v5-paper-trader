#!/usr/bin/env python3
"""
Monitor GOOG, RDDT, GDDY, PTC, VOO, and VXUS entry points.
Runs via cronjob every 30-60 min. Only outputs when conditions trigger (watchdog mode).
"""
import json, urllib.request, sys
from datetime import datetime, timezone, timedelta

# Thailand timezone
BKK = timezone(timedelta(hours=7))

# ---- TradingView primary data source (Yahoo fallback) ----
try:
    from tvDatafeed import TvDatafeed, Interval as TVInterval
    _TV = None
    _TV_EXCH = {
        "GOOG": ["NASDAQ"], "RDDT": ["NYSE"], "GDDY": ["NYSE"],
        "PTC": ["NASDAQ"], "VOO": ["AMEX", "NASDAQ"], "VXUS": ["NASDAQ", "AMEX"],
        "NVDU": ["AMEX", "NASDAQ"], "ZS": ["NYSE", "NASDAQ"], "BCC": ["NYSE", "NASDAQ"], "FBK": ["NYSE", "NASDAQ"], "AMZN": ["NASDAQ"],
    }
    _TV_BARS = {"5d": 7, "1mo": 200, "3mo": 66, "6mo": 300, "1y": 300}
    _TV_INTERVAL = {"1d": TVInterval.in_daily, "1h": TVInterval.in_1_hour}

    def _tv():
        global _TV
        if _TV is None:
            _TV = TvDatafeed()
        return _TV

    def fetch_tv_chart(ticker, period="6mo", interval="1d"):
        """Fetch OHLCV from TradingView, return Yahoo-shaped dict or None."""
        try:
            iv = _TV_INTERVAL.get(interval)
            if iv is None:
                return None
            ex_list = _TV_EXCH.get(ticker, ["NASDAQ", "NYSE", "AMEX"])
            n = _TV_BARS.get(period, 130)
            df = None
            for ex in ex_list:
                try:
                    df = _tv().get_hist(symbol=ticker, exchange=ex, interval=iv, n_bars=n)
                except Exception:
                    df = None
                if df is not None and not df.empty:
                    break
            if df is None or df.empty:
                return None
            df = df.dropna(subset=["close", "high", "low", "volume"])
            if len(df) < 5:
                return None
            closes = [float(x) for x in df["close"]]
            highs = [float(x) for x in df["high"]]
            lows = [float(x) for x in df["low"]]
            volumes = [float(x) for x in df["volume"]]
            ts = [int(t.timestamp()) for t in df.index]
            # 52-week extremes: last ~252 daily bars (all bars for intraday)
            w = 252 if interval == "1d" else len(highs)
            meta = {
                "fiftyTwoWeekHigh": max(highs[-w:]),
                "fiftyTwoWeekLow": min(lows[-w:]),
            }
            return {"chart": {"result": [{
                "timestamp": ts,
                "indicators": {"quote": [{
                    "close": closes, "high": highs, "low": lows, "volume": volumes,
                }]},
                "meta": meta,
            }]}}
        except Exception:
            return None
except Exception:
    def fetch_tv_chart(ticker, period="6mo", interval="1d"):
        return None

TICKERS = {
    "GOOG": "GOOG",
    "RDDT": "RDDT",
    "GDDY": "GDDY",
    "VOO": "VOO",
    "VXUS": "VXUS",
    "NVDU": "NVDU",
    "ZS": "ZS",
    "BCC": "BCC",
    "FBK": "FBK",
    "AMZN": "AMZN",
}

# Live positions — update as trades are made
POSITIONS = {
    "NVDU": {"entry": 90.00, "cost": 2430.00, "currency": "USD"},
    "ZS": {"entry": 150.00, "cost": 2250.00, "currency": "USD"},
}

def _fetch_chart_yahoo(ticker, period="5d", interval="1d"):
    """Fetch daily chart from Yahoo Finance (fallback)"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={period}&interval={interval}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return None

def fetch_chart(ticker, period="5d", interval="1d"):
    """Fetch chart data — TradingView primary, Yahoo fallback."""
    d = fetch_tv_chart(ticker, period, interval)
    if d is not None:
        return d
    return _fetch_chart_yahoo(ticker, period, interval)

def fetch_1mo(ticker):
    """Fetch 1 month of hourly data for finer signals"""
    return fetch_chart(ticker, "1mo", "1h")

def fetch_range(ticker, range_str):
    """Fetch daily data for given range"""
    return fetch_chart(ticker, range_str, "1d")

def sma(data, period):
    if len(data) < period: return None
    return sum(data[-period:]) / period

def ema(data, period):
    if len(data) < period: return None
    m = 2 / (period + 1)
    r = sum(data[:period]) / period
    for v in data[period:]:
        r = (v - r) * m + r
    return r

def rsi(data, period=14):
    if len(data) < period + 1: return None
    gains, losses = [], []
    for i in range(len(data) - period, len(data)):
        ch = data[i] - data[i-1]
        gains.append(max(ch, 0))
        losses.append(abs(min(ch, 0)))
    avg_g = sum(gains) / period
    avg_l = sum(losses) / period
    if avg_l == 0: return 100
    return 100 - (100 / (1 + avg_g / avg_l))

def extract_series(data):
    """Extract price series from Yahoo Finance response"""
    try:
        r = data['chart']['result'][0]
        q = r['indicators']['quote'][0]
        ts = r.get('timestamp', [])
        closes = [q['close'][i] for i in range(len(ts)) if q['close'][i] is not None]
        highs = [q['high'][i] for i in range(len(ts)) if q['high'][i] is not None]
        lows = [q['low'][i] for i in range(len(ts)) if q['low'][i] is not None]
        volumes = [q['volume'][i] for i in range(len(ts)) if q['volume'][i] is not None]
        meta = r['meta']
        return closes, highs, lows, volumes, ts, meta
    except (KeyError, TypeError, IndexError):
        return None, None, None, None, None, None

def analyze_ticker(ticker):
    """Analyze a ticker and return entry assessment"""
    # Use 6mo range to get enough data for SMA 100
    data_6mo = fetch_range(ticker, "6mo")
    if not data_6mo:
        return None

    closes, highs, lows, volumes, ts, meta = extract_series(data_6mo)
    if not closes or len(closes) < 20:
        return None

    cur = closes[-1]
    prev_close = closes[-2] if len(closes) > 1 else cur
    chg_pct = round((cur / prev_close - 1) * 100, 2)

    # Compute indicators
    s20 = sma(closes, 20)
    s50 = sma(closes, 50) if len(closes) >= 50 else None
    s100 = sma(closes, 100) if len(closes) >= 100 else None
    rsi14 = rsi(closes, 14)
    avg_vol_20 = sma(volumes, 20)
    avg_vol_5 = sma(volumes, 5) if len(volumes) >= 5 else avg_vol_20
    last_vol = volumes[-1]
    vol_ratio_20 = round(last_vol / avg_vol_20, 2) if avg_vol_20 else 1.0

    # Check recent trend (last 5 days)
    last_5 = closes[-6:]
    red_days = sum(1 for i in range(1, len(last_5)) if last_5[i] < last_5[i-1])
    green_days = sum(1 for i in range(1, len(last_5)) if last_5[i] > last_5[i-1])

    # Check for higher low (potential reversal)
    higher_low = False
    if len(closes) >= 3:
        if closes[-2] > closes[-3] and cur >= closes[-1]:  # at least not a lower low today
            pass
        if cur > min(closes[-5:-1]):  # current > recent low
            pass

    # Check consecutive green days
    green_streak = 0
    for i in range(len(closes) - 1, len(closes) - 5, -1):
        if i < 1: break
        if closes[i] > closes[i-1]:
            green_streak += 1
        else:
            break

    # Recent candles (last 3)
    last_3_days = [round((closes[i] / closes[i-1] - 1) * 100, 2) for i in range(len(closes)-3, len(closes)) if i >= 1]

    # 52W levels
    wkl = meta.get('fiftyTwoWeekLow', 0)
    wkh = meta.get('fiftyTwoWeekHigh', 0)

    # --- Extended indicators for verdict ---
    s10 = sma(closes, 10) if len(closes) >= 10 else None

    # ATR(14)
    atr14 = None
    atr_pct = None
    if len(closes) >= 15:
        trs = []
        for i in range(len(closes)-14, len(closes)):
            tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
            trs.append(tr)
        atr14 = round(sum(trs)/14, 2)
        atr_pct = round(atr14 / cur * 100, 2)

    # 3-month range + Fib levels (~63 trading days)
    start_3m = max(0, len(closes)-63)
    high_3m = round(max(highs[start_3m:]), 2)
    low_3m = round(min(lows[start_3m:]), 2)
    fib_range = high_3m - low_3m
    fib_382 = round(high_3m - 0.382 * fib_range, 2)
    fib_50 = round(high_3m - 0.5 * fib_range, 2)
    fib_618 = round(high_3m - 0.618 * fib_range, 2)
    fib_786 = round(high_3m - 0.786 * fib_range, 2)

    # MACD (12,26,9)
    macd_val = macd_sig = macd_hist = None
    if len(closes) >= 35:
        ema12 = ema(closes, 12)
        ema26 = ema(closes, 26)
        if ema12 and ema26:
            # Approximate: compute MACD line via EMA series
            k12, k26 = 2/13, 2/27
            e12 = closes[0]; e26 = closes[0]
            macd_series = []
            for v in closes[1:]:
                e12 = v*k12 + e12*(1-k12)
                e26 = v*k26 + e26*(1-k26)
                macd_series.append(e12 - e26)
            if macd_series:
                macd_val = round(macd_series[-1], 2)
                # Signal line (9-period EMA of MACD)
                sig = macd_series[0]
                k_sig = 2/10
                for v in macd_series[1:]:
                    sig = v*k_sig + sig*(1-k_sig)
                macd_sig = round(sig, 2)
                macd_hist = round(macd_val - macd_sig, 2)

    # Stochastic (14,3)
    stoch_k = None
    if len(closes) >= 14:
        hh = max(highs[-14:])
        ll = min(lows[-14:])
        if hh != ll:
            stoch_k = round(((cur - ll) / (hh - ll)) * 100, 1)

    # Regime detection
    regime = "MIXED"
    if s20 and s50:
        if cur > s20 and cur > s50:
            regime = "UPTREND"
        elif cur < s20 and cur < s50:
            regime = "DOWNTREND"
        elif cur > s50 and cur < s20:
            regime = "PULLBACK"  # pullback in uptrend
        elif cur > s20 and cur < s50:
            regime = "BOUNCE"  # bounce in downtrend

    # Build assessment dict
    return {
        'ticker': ticker,
        'price': cur,
        'chg_pct': chg_pct,
        'sma10': round(s10, 2) if s10 else None,
        'sma20': round(s20, 2) if s20 else None,
        'sma50': round(s50, 2) if s50 else None,
        'sma100': round(s100, 2) if s100 else None,
        'rsi14': round(rsi14, 1) if rsi14 else None,
        'vol_ratio': vol_ratio_20,
        'red_days_5': red_days,
        'green_days_5': green_days,
        'green_streak': green_streak,
        'last_3_days': last_3_days,
        '52w_low': wkl,
        '52w_high': wkh,
        'below_sma20': cur < s20 if s20 else None,
        'below_sma50': cur < s50 if s50 else None,
        'below_sma100': cur < s100 if s100 else None,
        'avg_vol_20': int(avg_vol_20) if avg_vol_20 else 0,
        'last_vol': last_vol,
        # Extended indicators for verdict
        'regime': regime,
        'atr14': atr14,
        'atr_pct': atr_pct,
        'high_3m': high_3m,
        'low_3m': low_3m,
        'fib_382': fib_382,
        'fib_50': fib_50,
        'fib_618': fib_618,
        'fib_786': fib_786,
        'macd_val': macd_val,
        'macd_sig': macd_sig,
        'macd_hist': macd_hist,
        'stoch_k': stoch_k,
    }

def check_entry_goog(a):
    """Check GOOG entry conditions. Returns alert message or None.
    Only alerts on actionable setups — suppresses noise in downtrends."""
    alerts = []
    price = a['price']
    r = a['rsi14']
    below_sma100 = a['below_sma100']
    regime = a['regime']

    # In DOWNTREND: only alert on capitulation (structural tests are noise)
    if regime == 'DOWNTREND':
        if a['vol_ratio'] > 1.5 and a['chg_pct'] < -3:
            alerts.append(f"🔥 Capitulation sell-off ({a['chg_pct']:+.2f}%, {a['vol_ratio']}x vol)")
        if not alerts:
            return None
    else:
        # Condition 1: RSI oversold (<30)
        if r is not None and r < 30:
            alerts.append(f"🔴 RSI Oversold at {r}")

        # Condition 2: Approaching oversold + volume easing (near entry)
        if r is not None and r < 35 and a['vol_ratio'] < 1.3:
            if a['green_streak'] >= 1 and a['green_streak'] <= 2:
                alerts.append(f"🟢 RSI near oversold ({r}) + volume normalizing + green candle")

        # Condition 3: First green after RSI bouncing from <32
        if r is not None and r > 30 and r < 45:
            if a['green_streak'] >= 1:
                alerts.append(f"🟡 RSI recovering ({r}) + green streak ({a['green_streak']}d)")

        # Condition 4: Testing round-number support
        for level in [300, 290, 280]:
            if abs(price - level) / price < 0.02:
                alerts.append(f"🧱 Testing psychological support at ${level}")

        # Condition 5: SMA 100 test (structural support)
        if a['sma100'] and abs(price - a['sma100']) / a['sma100'] < 0.03:
            alerts.append(f"📏 Testing SMA 100 support at ${a['sma100']:.2f}")

    if not alerts:
        return None

    summary = f"📡 **GOOG Entry Monitor**\n"
    summary += f"Price: ${price:.2f} ({a['chg_pct']:+.2f}%) | RSI: {r} | Vol: {a['vol_ratio']}x\n"
    summary += f"SMA 20: ${a['sma20']} | SMA 50: ${a['sma50']} | SMA 100: ${a['sma100']}\n"
    summary += f"5d: {a['red_days_5']}🔴/{a['green_days_5']}🟢\n"
    for alert in alerts:
        summary += f"• {alert}\n"
    summary += f"\n{get_verdict(a)}\n"
    return summary

def check_entry_rddt(a):
    """Check RDDT entry conditions. Returns alert message or None.
    Only alerts on actionable setups — suppresses noise in downtrends."""
    alerts = []
    price = a['price']
    r = a['rsi14']
    regime = a['regime']

    # In DOWNTREND: only alert on capitulation (structural tests are noise)
    if regime == 'DOWNTREND':
        if a['vol_ratio'] > 1.8 and a['chg_pct'] < -5:
            alerts.append(f"🔥 Capitulation sell-off ({a['chg_pct']:+.2f}%, {a['vol_ratio']}x vol)")
        if not alerts:
            return None
    else:
        # Condition 1: RSI oversold (<30)
        if r is not None and r < 30:
            alerts.append(f"🔴 RSI Oversold at {r}")

        # Condition 2: Testing SMA 100 / Fib 61.8% zone ($160-$165)
        sma100 = a['sma100']
        if sma100 and price >= sma100 * 0.97 and price <= sma100 * 1.03:
            alerts.append(f"📏 Testing SMA 100 support at ${sma100:.2f}")

        if price >= 160 and price <= 166:
            alerts.append(f"🎯 In Fib 61.8% zone ($160-$165)")

        # Condition 3: RSI <35 + normal volume + first green (entry trigger)
        if r is not None and r < 35 and a['vol_ratio'] < 1.2:
            if a['green_streak'] >= 1:
                alerts.append(f"🟢 Entry setup: RSI {r}, volume normalizing, green candle")

        # Condition 4: Reclaiming SMA 50 ($173)
        sma50 = a['sma50']
        if sma50 and price > sma50 and a['below_sma50'] == False:
            if a['green_streak'] >= 1:
                alerts.append(f"🚀 Reclaimed SMA 50 at ${sma50:.2f}")

        # Condition 5: Volume spike + big red day (capitulation)
        if a['vol_ratio'] > 1.8 and a['chg_pct'] < -5:
            alerts.append(f"🔥 Capitulation sell-off ({a['chg_pct']:+.2f}%, {a['vol_ratio']}x vol)")

    if not alerts:
        return None

    summary = f"📡 **RDDT Entry Monitor**\n"
    summary += f"Price: ${price:.2f} ({a['chg_pct']:+.2f}%) | RSI: {r} | Vol: {a['vol_ratio']}x\n"
    if a['sma20']: summary += f"SMA 20: ${a['sma20']} | SMA 50: ${a['sma50']} | SMA 100: ${a['sma100']}\n"
    summary += f"5d: {a['red_days_5']}🔴/{a['green_days_5']}🟢\n"
    for alert in alerts:
        summary += f"• {alert}\n"
    summary += f"\n{get_verdict(a)}\n"
    return summary

def check_entry_gddy(a):
    """Check GDDY entry conditions. Returns alert message or None.
    Only alerts on actionable setups — suppresses noise in downtrends."""
    alerts = []
    price = a['price']
    r = a['rsi14']
    regime = a['regime']

    # In DOWNTREND: only alert on structural support or capitulation
    if regime == 'DOWNTREND':
        sma50 = a['sma50']
        if sma50 and price >= sma50 * 0.97 and price <= sma50 * 1.03:
            alerts.append(f"📏 Testing SMA 50 support at ${sma50:.2f}")
        if a['vol_ratio'] > 1.5 and a['chg_pct'] < -3:
            alerts.append(f"🔥 Capitulation sell-off ({a['chg_pct']:+.2f}%, {a['vol_ratio']}x vol)")
        if not alerts:
            return None
    else:
        # Condition 1: Pullback to SMA 20 zone
        sma20 = a['sma20']
        if sma20 and price >= sma20 * 0.97 and price <= sma20 * 1.03:
            if a['below_sma20']:
                alerts.append(f"📏 Testing SMA 20 support at ${sma20:.2f}")

        # Condition 2: Pullback to SMA 50 zone (deeper pullback)
        sma50 = a['sma50']
        if sma50 and price >= sma50 * 0.97 and price <= sma50 * 1.03:
            if a['below_sma50']:
                alerts.append(f"📏 Testing SMA 50 support at ${sma50:.2f}")

        # Condition 3: RSI oversold in uptrend (rare — shakeout opportunity)
        if r is not None and r < 35 and not a['below_sma50']:
            alerts.append(f"🟢 RSI cooled to {r} in uptrend — potential entry")

        # Condition 4: Green streak after SMA 20 bounce (momentum continuation)
        if not a['below_sma20'] and a['green_streak'] >= 2 and r is not None and r > 55:
            alerts.append(f"🚀 Bounce from SMA 20 — {a['green_streak']}d green streak, RSI {r}")

        # Condition 5: Volume spike + big red day to SMA 20 (shakeout)
        if a['vol_ratio'] > 1.5 and a['chg_pct'] < -3 and sma20 and price > sma20 * 0.97:
            alerts.append(f"🔥 Shakeout to SMA 20 ({a['chg_pct']:+.2f}%, {a['vol_ratio']}x vol)")

    if not alerts:
        return None

    summary = f"📡 **GDDY Entry Monitor**\n"
    summary += f"Price: ${price:.2f} ({a['chg_pct']:+.2f}%) | RSI: {r} | Vol: {a['vol_ratio']}x\n"
    if a['sma20']: summary += f"SMA 20: ${a['sma20']} | SMA 50: ${a['sma50']} | SMA 100: ${a['sma100']}\n"
    summary += f"5d: {a['red_days_5']}🔴/{a['green_days_5']}🟢\n"
    for alert in alerts:
        summary += f"• {alert}\n"
    summary += f"\n{get_verdict(a)}\n"
    return summary

def check_entry_ptc(a):
    """Check PTC entry conditions. Returns alert message or None.
    Only alerts on actionable setups — suppresses noise in downtrends."""
    alerts = []
    price = a['price']
    r = a['rsi14']
    sma20 = a['sma20']
    sma50 = a['sma50']
    sma100 = a['sma100']
    vol_ratio = a['vol_ratio']
    regime = a['regime']

    # In DOWNTREND: only alert on structural support or capitulation
    if regime == 'DOWNTREND':
        if sma100 and abs(price - sma100) / sma100 < 0.05:
            alerts.append(f"📏 Approaching SMA100 at ${sma100:.2f} — major structural test")
        if vol_ratio > 1.5 and a['chg_pct'] < -5:
            alerts.append(f"🔥 Capitulation event ({a['chg_pct']:+.2f}%, {vol_ratio}x vol)")
        if not alerts:
            return None
    else:
        # Condition 1: Testing SMA50 resistance (key level for BOUNCE regime)
        if sma50 and price >= sma50 * 0.97 and price <= sma50 * 1.03:
            if a['green_streak'] >= 1:
                alerts.append(f"📏 Testing SMA50 resistance at ${sma50:.2f} — reclaim = momentum shift")

        # Condition 2: SMA20 reclaimed — bounce confirmation
        if not a['below_sma20'] and a['green_streak'] >= 2 and r is not None and r > 45:
            alerts.append(f"🟢 SMA20 reclaimed (${sma20:.2f}) + {a['green_streak']}d green streak — bounce confirmed")

        # Condition 3: Shakeout recovery pattern
        if vol_ratio < 0.8 and r is not None and r > 45 and r < 65 and not a['below_sma20']:
            alerts.append(f"🔄 Shakeout recovery: low vol bounce ({vol_ratio}x), RSI {r} — healthy")

        # Condition 4: Approaching SMA100 (structural test)
        if sma100 and abs(price - sma100) / sma100 < 0.05:
            alerts.append(f"📏 Approaching SMA100 at ${sma100:.2f} — major structural test")

        # Condition 5: Stoch overbought + pullback setup (entry after cool-off)
        stoch = a.get('stoch_k')
        if stoch and stoch > 80 and not a['below_sma20']:
            alerts.append(f"🟡 Stoch overbought ({stoch}) — wait for pullback to SMA20 (${sma20:.2f})")

        # Condition 6: Big red day shakeout (recent capitulation event)
        if vol_ratio > 1.5 and a['chg_pct'] < -5:
            alerts.append(f"🔥 Capitulation event ({a['chg_pct']:+.2f}%, {vol_ratio}x vol)")

    if not alerts:
        return None

    summary = f"📡 **PTC Entry Monitor**\n"
    summary += f"Price: ${price:.2f} ({a['chg_pct']:+.2f}%) | RSI: {r} | Vol: {vol_ratio}x\n"
    if sma20: summary += f"SMA 20: ${sma20} | SMA 50: ${sma50} | SMA 100: ${sma100}\n"
    summary += f"5d: {a['red_days_5']}🔴/{a['green_days_5']}🟢\n"
    for alert in alerts:
        summary += f"• {alert}\n"
    summary += f"\n{get_verdict(a)}\n"
    return summary

def check_entry_bcc(a):
    """Check BCC (Boise Cascade) entry conditions. Pullback entries in uptrend.
    Only alerts on actionable setups — suppresses noise in downtrends."""
    alerts = []
    price = a['price']
    r = a['rsi14']
    sma20 = a['sma20']
    sma50 = a['sma50']
    sma100 = a['sma100']
    vol_ratio = a['vol_ratio']
    regime = a['regime']

    # In DOWNTREND: only alert on capitulation
    if regime == 'DOWNTREND':
        if vol_ratio > 1.5 and a['chg_pct'] < -1.5:
            alerts.append(f"🔥 Sell-off ({a['chg_pct']:+.2f}%, {vol_ratio}x vol) — watch for reversal")
        if not alerts:
            return None

    # Condition 1: RSI cooled to pullback zone in uptrend
    if r is not None and r < 40 and regime in ('UPTREND', 'PULLBACK'):
        alerts.append(f"🟢 RSI pullback to {r} in {regime} — entry zone")

    # Condition 2: Testing SMA 20 support
    if sma20 and price >= sma20 * 0.98 and price <= sma20 * 1.02:
        if a['below_sma20']:
            alerts.append(f"📏 Testing SMA 20 support at ${sma20:.2f}")

    # Condition 3: Testing SMA 50 support (deeper pullback)
    if sma50 and price >= sma50 * 0.98 and price <= sma50 * 1.02:
        alerts.append(f"📏 Testing SMA 50 support at ${sma50:.2f} — stronger entry")

    # Condition 4: Fib 38.2%-50% pullback zone
    fib382 = a.get('fib_382', 0)
    fib50 = a.get('fib_50', 0)
    if fib382 and fib50 and price >= fib50 * 0.99 and price <= fib382 * 1.01:
        alerts.append(f"🎯 In Fib pullback zone (${fib50:.2f}–${fib382:.2f})")

    # Condition 5: Green streak after pullback (bounce confirmation)
    if a['green_streak'] >= 2 and r is not None and r > 40 and r < 60:
        alerts.append(f"🟢 {a['green_streak']}d green streak, RSI {r} — bounce confirmed")

    # Condition 6: Volume spike + red day (capitulation buy opportunity)
    if vol_ratio > 1.5 and a['chg_pct'] < -1.5:
        alerts.append(f"🔥 Sell-off ({a['chg_pct']:+.2f}%, {vol_ratio}x vol) — watch for reversal")

    if not alerts:
        return None

    summary = f"📡 **BCC Entry Monitor**\n"
    summary += f"Price: ${price:.2f} ({a['chg_pct']:+.2f}%) | RSI: {r} | Vol: {vol_ratio}x\n"
    if sma20: summary += f"SMA 20: ${sma20} | SMA 50: ${sma50} | SMA 100: ${sma100}\n"
    summary += f"5d: {a['red_days_5']}🔴/{a['green_days_5']}🟢\n"
    for alert in alerts:
        summary += f"• {alert}\n"
    summary += f"\n{get_verdict(a)}\n"
    return summary

def check_entry_fbk(a):
    """Check FBK (FirstBank PR) entry conditions. Pullback entries in uptrend.
    Only alerts on actionable setups — suppresses noise in downtrends."""
    alerts = []
    price = a['price']
    r = a['rsi14']
    sma20 = a['sma20']
    sma50 = a['sma50']
    sma100 = a['sma100']
    vol_ratio = a['vol_ratio']
    regime = a['regime']

    # In DOWNTREND: only alert on capitulation
    if regime == 'DOWNTREND':
        if vol_ratio > 1.5 and a['chg_pct'] < -1.5:
            alerts.append(f"🔥 Sell-off ({a['chg_pct']:+.2f}%, {vol_ratio}x vol) — watch for reversal")
        if not alerts:
            return None

    # Condition 1: RSI cooled to pullback zone in uptrend
    if r is not None and r < 40 and regime in ('UPTREND', 'PULLBACK'):
        alerts.append(f"🟢 RSI pullback to {r} in {regime} — entry zone")

    # Condition 2: Testing SMA 20 support
    if sma20 and price >= sma20 * 0.98 and price <= sma20 * 1.02:
        if a['below_sma20']:
            alerts.append(f"📏 Testing SMA 20 support at ${sma20:.2f}")

    # Condition 3: Testing SMA 50 support (deeper pullback)
    if sma50 and price >= sma50 * 0.98 and price <= sma50 * 1.02:
        alerts.append(f"📏 Testing SMA 50 support at ${sma50:.2f} — stronger entry")

    # Condition 4: Fib 38.2%-50% pullback zone
    fib382 = a.get('fib_382', 0)
    fib50 = a.get('fib_50', 0)
    if fib382 and fib50 and price >= fib50 * 0.99 and price <= fib382 * 1.01:
        alerts.append(f"🎯 In Fib pullback zone (${fib50:.2f}–${fib382:.2f})")

    # Condition 5: Green streak after pullback (bounce confirmation)
    if a['green_streak'] >= 2 and r is not None and r > 40 and r < 60:
        alerts.append(f"🟢 {a['green_streak']}d green streak, RSI {r} — bounce confirmed")

    # Condition 6: Volume spike + red day (capitulation buy opportunity)
    if vol_ratio > 1.5 and a['chg_pct'] < -1.5:
        alerts.append(f"🔥 Sell-off ({a['chg_pct']:+.2f}%, {vol_ratio}x vol) — watch for reversal")

    if not alerts:
        return None

    summary = f"📡 **FBK Entry Monitor**\n"
    summary += f"Price: ${price:.2f} ({a['chg_pct']:+.2f}%) | RSI: {r} | Vol: {vol_ratio}x\n"
    if sma20: summary += f"SMA 20: ${sma20} | SMA 50: ${sma50} | SMA 100: ${sma100}\n"
    summary += f"5d: {a['red_days_5']}🔴/{a['green_days_5']}🟢\n"
    for alert in alerts:
        summary += f"• {alert}\n"
    summary += f"\n{get_verdict(a)}\n"
    return summary

def check_entry_amzn(a):
    """Check AMZN entry conditions. Pullback entries in uptrend.
    Expert-approved trigger: close >$263 (SMA20 reclaim) or MACD hist >0.
    Only alerts on actionable setups — suppresses noise in downtrends."""
    alerts = []
    price = a['price']
    r = a['rsi14']
    sma20 = a['sma20']
    sma50 = a['sma50']
    sma100 = a['sma100']
    vol_ratio = a['vol_ratio']
    regime = a['regime']

    # In DOWNTREND: only alert on capitulation
    if regime == 'DOWNTREND':
        if vol_ratio > 1.5 and a['chg_pct'] < -1.5:
            alerts.append(f"🔥 Sell-off ({a['chg_pct']:+.2f}%, {vol_ratio}x vol) — watch for reversal")
        if not alerts:
            return None

    # Condition 1: RSI cooled to pullback zone in uptrend
    if r is not None and r < 40 and regime in ('UPTREND', 'PULLBACK'):
        alerts.append(f"🟢 RSI pullback to {r} in {regime} — entry zone")

    # Condition 2: Testing SMA 20 support
    if sma20 and price >= sma20 * 0.98 and price <= sma20 * 1.02:
        if a['below_sma20']:
            alerts.append(f"📏 Testing SMA 20 support at ${sma20:.2f}")

    # Condition 3: Testing SMA 50 support (deeper pullback)
    if sma50 and price >= sma50 * 0.98 and price <= sma50 * 1.02:
        alerts.append(f"📏 Testing SMA 50 support at ${sma50:.2f} — stronger entry")

    # Condition 4: Fib 38.2%-50% pullback zone
    fib382 = a.get('fib_382', 0)
    fib50 = a.get('fib_50', 0)
    if fib382 and fib50 and price >= fib50 * 0.99 and price <= fib382 * 1.01:
        alerts.append(f"🎯 In Fib pullback zone (${fib50:.2f}–${fib382:.2f})")

    # Condition 5: Expert-approved confirmation trigger — close > SMA20 (≈$263) or MACD hist > 0
    macd_hist = a.get('macd_hist')
    if not a['below_sma20'] and a['green_streak'] >= 1:
        alerts.append(f"🟢 CLOSE > SMA20 (${sma20:.2f}) — entry confirmation per approved plan")
    elif macd_hist is not None and macd_hist > 0:
        alerts.append(f"📈 MACD hist turned positive ({macd_hist:.2f}) — entry confirmation per approved plan")

    # Condition 6: Green streak after pullback (bounce confirmation)
    if a['green_streak'] >= 2 and r is not None and r > 40 and r < 60:
        alerts.append(f"🟢 {a['green_streak']}d green streak, RSI {r} — bounce confirmed")

    # Condition 7: Volume spike + red day (capitulation buy opportunity)
    if vol_ratio > 1.5 and a['chg_pct'] < -1.5:
        alerts.append(f"🔥 Sell-off ({a['chg_pct']:+.2f}%, {vol_ratio}x vol) — watch for reversal")

    if not alerts:
        return None

    summary = f"📡 **AMZN Entry Monitor**\n"
    summary += f"Price: ${price:.2f} ({a['chg_pct']:+.2f}%) | RSI: {r} | Vol: {vol_ratio}x\n"
    if sma20: summary += f"SMA 20: ${sma20} | SMA 50: ${sma50} | SMA 100: ${sma100}\n"
    summary += f"5d: {a['red_days_5']}🔴/{a['green_days_5']}🟢\n"
    for alert in alerts:
        summary += f"• {alert}\n"
    summary += f"\n{get_verdict(a)}\n"
    return summary

def check_entry_voo(a):
    """Check VOO (S&P 500 ETF) entry conditions. Pullback entries in uptrend.
    Only alerts on actionable setups — suppresses noise in downtrends."""
    alerts = []
    price = a['price']
    r = a['rsi14']
    sma20 = a['sma20']
    sma50 = a['sma50']
    sma100 = a['sma100']
    vol_ratio = a['vol_ratio']
    regime = a['regime']

    # In DOWNTREND: only alert on capitulation
    if regime == 'DOWNTREND':
        if vol_ratio > 1.5 and a['chg_pct'] < -1.5:
            alerts.append(f"🔥 Sell-off ({a['chg_pct']:+.2f}%, {vol_ratio}x vol) — watch for reversal")
        if not alerts:
            return None

    # Condition 1: RSI cooled to pullback zone in uptrend
    if r is not None and r < 40 and regime in ('UPTREND', 'PULLBACK'):
        alerts.append(f"🟢 RSI pullback to {r} in {regime} — entry zone")

    # Condition 2: Testing SMA 20 support
    if sma20 and price >= sma20 * 0.98 and price <= sma20 * 1.02:
        if a['below_sma20']:
            alerts.append(f"📏 Testing SMA 20 support at ${sma20:.2f}")

    # Condition 3: Testing SMA 50 support (deeper pullback)
    if sma50 and price >= sma50 * 0.98 and price <= sma50 * 1.02:
        alerts.append(f"📏 Testing SMA 50 support at ${sma50:.2f} — stronger entry")

    # Condition 4: Fib 38.2%-50% pullback zone
    fib382 = a.get('fib_382', 0)
    fib50 = a.get('fib_50', 0)
    if fib382 and fib50 and price >= fib50 * 0.99 and price <= fib382 * 1.01:
        alerts.append(f"🎯 In Fib pullback zone (${fib50:.2f}–${fib382:.2f})")

    # Condition 5: Green streak after pullback (bounce confirmation)
    if a['green_streak'] >= 2 and r is not None and r > 40 and r < 60:
        alerts.append(f"🟢 {a['green_streak']}d green streak, RSI {r} — bounce confirmed")

    # Condition 6: Volume spike + red day (capitulation buy opportunity)
    if vol_ratio > 1.5 and a['chg_pct'] < -1.5:
        alerts.append(f"🔥 Sell-off ({a['chg_pct']:+.2f}%, {vol_ratio}x vol) — watch for reversal")

    if not alerts:
        return None

    summary = f"📡 **VOO Entry Monitor**\n"
    summary += f"Price: ${price:.2f} ({a['chg_pct']:+.2f}%) | RSI: {r} | Vol: {vol_ratio}x\n"
    if sma20: summary += f"SMA 20: ${sma20} | SMA 50: ${sma50} | SMA 100: ${sma100}\n"
    summary += f"5d: {a['red_days_5']}🔴/{a['green_days_5']}🟢\n"
    for alert in alerts:
        summary += f"• {alert}\n"
    summary += f"\n{get_verdict(a)}\n"
    return summary

def check_entry_vxus(a):
    """Check VXUS (International Stocks ETF) entry conditions.
    Only alerts on actionable setups — suppresses noise in downtrends."""
    alerts = []
    price = a['price']
    r = a['rsi14']
    sma20 = a['sma20']
    sma50 = a['sma50']
    sma100 = a['sma100']
    vol_ratio = a['vol_ratio']
    regime = a['regime']

    # In DOWNTREND: only alert on capitulation or structural support
    if regime == 'DOWNTREND':
        if sma100 and price >= sma100 * 0.98 and price <= sma100 * 1.02:
            alerts.append(f"📏 Testing SMA 100 support at ${sma100:.2f} — strong entry")
        if vol_ratio > 1.5 and a['chg_pct'] < -2:
            alerts.append(f"🔥 Sell-off ({a['chg_pct']:+.2f}%, {vol_ratio}x vol) — watch for reversal")
        if not alerts:
            return None

    # Condition 1: RSI oversold or cooled
    if r is not None and r < 35:
        alerts.append(f"🔴 RSI oversold at {r} — potential entry")
    elif r is not None and r < 45 and regime in ('UPTREND', 'PULLBACK'):
        alerts.append(f"🟢 RSI cooled to {r} in {regime} — entry zone")

    # Condition 2: Testing SMA 50 support
    if sma50 and price >= sma50 * 0.98 and price <= sma50 * 1.02:
        alerts.append(f"📏 Testing SMA 50 support at ${sma50:.2f}")

    # Condition 3: Testing SMA 100 support (deep pullback)
    if sma100 and price >= sma100 * 0.98 and price <= sma100 * 1.02:
        alerts.append(f"📏 Testing SMA 100 support at ${sma100:.2f} — strong entry")

    # Condition 4: Fib 50%-61.8% pullback zone
    fib50 = a.get('fib_50', 0)
    fib618 = a.get('fib_618', 0)
    if fib50 and fib618 and price >= fib618 * 0.99 and price <= fib50 * 1.01:
        alerts.append(f"🎯 In Fib deep pullback zone (${fib618:.2f}–${fib50:.2f})")

    # Condition 5: Green streak after pullback
    if a['green_streak'] >= 2 and r is not None and r > 35 and r < 60:
        alerts.append(f"🟢 {a['green_streak']}d green streak, RSI {r} — bounce confirmed")

    # Condition 6: Volume spike + red day
    if vol_ratio > 1.5 and a['chg_pct'] < -2:
        alerts.append(f"🔥 Sell-off ({a['chg_pct']:+.2f}%, {vol_ratio}x vol) — watch for reversal")

    if not alerts:
        return None

    summary = f"📡 **VXUS Entry Monitor**\n"
    summary += f"Price: ${price:.2f} ({a['chg_pct']:+.2f}%) | RSI: {r} | Vol: {vol_ratio}x\n"
    if sma20: summary += f"SMA 20: ${sma20} | SMA 50: ${sma50} | SMA 100: ${sma100}\n"
    summary += f"5d: {a['red_days_5']}🔴/{a['green_days_5']}🟢\n"
    for alert in alerts:
        summary += f"• {alert}\n"
    summary += f"\n{get_verdict(a)}\n"
    return summary

def get_verdict(a):
    """Generate entry verdict line for a ticker based on regime + indicators."""
    t = a['ticker']
    p = a['price']
    r = a['regime']
    atr = a.get('atr14') or 0
    rsi = a.get('rsi14')
    fib382 = a.get('fib_382', p)
    fib50 = a.get('fib_50', p)
    fib618 = a.get('fib_618', p)
    fib786 = a.get('fib_786', p)
    h3m = a.get('high_3m', p)
    l3m = a.get('low_3m', p)
    s10 = a.get('sma10')
    s20 = a.get('sma20')
    s50 = a.get('sma50')
    s100 = a.get('sma100')
    stoch = a.get('stoch_k')

    if t == 'GOOG':
        if r == 'DOWNTREND':
            if rsi and rsi < 30 and a.get('green_streak', 0) >= 1:
                return f"📍 **VERDICT: 🟢 ENTRY READY** | Zone: ${fib618}–${fib786} | Stop: ${round(l3m-atr,2)} | TP: ${s50}"
            else:
                return f"📍 **VERDICT: 🔴 WAIT** | {r} | Entry: ${fib618}–${fib786} | Needs RSI<30 (now {rsi}) | Stop: ${round(l3m-atr,2)}"
        elif r == 'PULLBACK':
            return f"📍 **VERDICT: 🟡 PULLBACK** | Entry: ${s50} (SMA50) | Stop: ${round(s50-1.5*atr,2)} | TP1: ${s20}"
        elif r == 'UPTREND':
            return f"📍 **VERDICT: 🟢 UPTREND** | Entry on dip: ${fib382}–${fib50} | Stop: ${round(fib618-atr,2)} | TP: ${h3m}"
        else:
            return f"📍 **VERDICT: ⏳ MONITOR** | Regime: {r} | Entry unclear"

    elif t == 'RDDT':
        if r == 'PULLBACK':
            entry = s50 if s50 else fib50
            return f"📍 **VERDICT: 🟡 NEAR ENTRY** | {r} | Entry: ${entry} (SMA50/Fib.5) | Stop: ${round(entry-1.5*atr,2)} | TP1: ${s20} | TP2: ${s10}"
        elif r == 'UPTREND':
            return f"📍 **VERDICT: 🟢 UPTREND** | Entry on dip: ${fib382}–${fib50} | Stop: ${round(fib618-atr,2)} | TP: ${h3m}"
        elif r == 'DOWNTREND':
            return f"📍 **VERDICT: 🔴 WAIT** | {r} | Entry: ${fib618}–${fib786} | Needs RSI<35 + green candle"
        elif r == 'BOUNCE':
            return f"📍 **VERDICT: ⚠️ BOUNCE** | Risky | Wait for SMA50 reclaim (>${s50}) | Entry then: ${s50}"
        else:
            return f"📍 **VERDICT: ⏳ MONITOR** | Regime: {r}"

    elif t == 'GDDY':
        if r == 'UPTREND':
            if stoch and stoch > 80:
                return f"📍 **VERDICT: 🟡 OVERBOUGHT** | {r} | Wait for pullback: ${fib382}–${fib50} | Stop: ${round(fib618-atr,2)} | TP: ${h3m}"
            else:
                return f"📍 **VERDICT: 🟢 UPTREND** | {r} | Entry on dip: ${fib382}–${fib50} | Stop: ${round(fib618-atr,2)} | TP: ${h3m}"
        elif r == 'PULLBACK':
            return f"📍 **VERDICT: 🟡 PULLBACK** | Entry: ${s20} (SMA20) | Stop: ${round(s50-atr,2) if s50 else 'N/A'} | TP: ${s10 or h3m}"
        elif r == 'DOWNTREND':
            return f"📍 **VERDICT: 🔴 WAIT** | {r} | Below SMA50 structurally broken"
        else:
            return f"📍 **VERDICT: ⏳ MONITOR** | Regime: {r}"

    elif t == 'PTC':
        if r == 'BOUNCE':
            if stoch and stoch > 80:
                return f"📍 **VERDICT: 🟡 OVERBOUGHT BOUNCE** | Entry on pullback: ${s20} (SMA20) | Stop: ${round(s20-atr,2)} | TP: ${s50} (SMA50)"
            else:
                return f"📍 **VERDICT: 🟡 BOUNCE** | {r} | Needs SMA50 reclaim (>${s50}) | Entry: ${s20} | Stop: ${round(l3m,2)} | TP1: ${s50} TP2: ${s100}"
        elif r == 'UPTREND':
            # If price is below Fib38.2% (recovery from deep shakeout), use SMA support
            if p < fib382:
                if stoch and stoch > 80:
                    return f"📍 **VERDICT: 🟢 UPTREND** | Overbought recovery — wait for pullback to SMA20 (${s20}) | Stop: ${round(s20-atr,2)} | TP: ${s50}"
                else:
                    return f"📍 **VERDICT: 🟢 UPTREND** | Entry on pullback: ${s20} (SMA20) | Stop: ${round(s20-atr,2)} | TP1: ${s50} TP2: ${s100}"
            else:
                return f"📍 **VERDICT: 🟢 UPTREND** | Entry on dip: ${fib382}–${fib50} | Stop: ${round(fib618-atr,2)} | TP: ${h3m}"
        elif r == 'DOWNTREND':
            return f"📍 **VERDICT: 🔴 WAIT** | {r} | Entry: ${fib618}–${fib786} | Watch for shakeout exhaustion"
        elif r == 'PULLBACK':
            return f"📍 **VERDICT: 🟡 PULLBACK** | Entry: ${s50} (SMA50) | Stop: ${round(s50-1.5*atr,2)} | TP: ${s20}"
        else:
            return f"📍 **VERDICT: ⏳ MONITOR** | Regime: {r}"

    elif t == 'VOO':
        if r == 'UPTREND':
            return f"📍 **VERDICT: 🟢 UPTREND** | Entry on dip: ${fib382}–${fib50} | Stop: ${round(fib618-atr,2)} | TP: ${h3m}"
        elif r == 'PULLBACK':
            return f"📍 **VERDICT: 🟢 PULLBACK ENTRY** | Entry: ${s50} (SMA50) | Stop: ${round(s50-1.5*atr,2)} | TP: ${h3m}"
        elif r == 'DOWNTREND':
            return f"📍 **VERDICT: 🔴 WAIT** | {r} | Entry: ${fib618}–${fib786} | Needs RSI<35 + green candle"
        elif r == 'BOUNCE':
            return f"📍 **VERDICT: ⚠️ BOUNCE** | Risky | Wait for SMA20 reclaim (>${s20}) | Entry then: ${s20}"
        else:
            return f"📍 **VERDICT: ⏳ MONITOR** | Regime: {r}"

    elif t == 'VXUS':
        if r == 'UPTREND':
            return f"📍 **VERDICT: 🟢 UPTREND** | Entry on dip: ${fib382}–${fib50} | Stop: ${round(fib618-atr,2)} | TP: ${h3m}"
        elif r == 'PULLBACK':
            return f"📍 **VERDICT: 🟢 PULLBACK ENTRY** | Entry: ${s50} (SMA50) | Stop: ${round(s50-1.5*atr,2)} | TP: ${h3m}"
        elif r == 'DOWNTREND':
            return f"📍 **VERDICT: 🔴 WAIT** | {r} | Entry: ${fib618}–${fib786} | Needs RSI<35 + green candle"
        elif r == 'BOUNCE':
            return f"📍 **VERDICT: ⚠️ BOUNCE** | Risky | Wait for SMA50 reclaim (>${s50})"
        else:
            return f"📍 **VERDICT: ⏳ MONITOR** | Regime: {r}"

    elif t == 'BCC':
        if r == 'PULLBACK':
            entry = s50 if s50 else fib50
            return f"📍 **VERDICT: 🟡 NEAR ENTRY** | {r} | Entry: ${entry} (SMA50) | Stop: ${round(entry-1.5*atr,2)} | TP1: ${s20} | TP2: ${s10}"
        elif r == 'UPTREND':
            return f"📍 **VERDICT: 🟢 UPTREND** | Entry on dip: ${fib382}–${fib50} | Stop: ${round(fib618-atr,2)} | TP: ${h3m}"
        elif r == 'DOWNTREND':
            return f"📍 **VERDICT: 🔴 WAIT** | {r} | Entry: ${fib618}–${fib786} | Needs RSI<30 + green candle"
        elif r == 'BOUNCE':
            return f"📍 **VERDICT: ⚠️ BOUNCE** | Risky | Wait for SMA50 reclaim (>${s50}) | Entry then: ${s50}"
        else:
            return f"📍 **VERDICT: ⏳ MONITOR** | Regime: {r}"

    elif t == 'FBK':
        if r == 'PULLBACK':
            entry = s50 if s50 else fib50
            return f"📍 **VERDICT: 🟡 NEAR ENTRY** | {r} | Entry: ${entry} (SMA50) | Stop: ${round(entry-1.5*atr,2)} | TP1: ${s20} | TP2: ${s10}"
        elif r == 'UPTREND':
            return f"📍 **VERDICT: 🟢 UPTREND** | Entry on dip: ${fib382}–${fib50} | Stop: ${round(fib618-atr,2)} | TP: ${h3m}"
        elif r == 'DOWNTREND':
            return f"📍 **VERDICT: 🔴 WAIT** | {r} | Entry: ${fib618}–${fib786} | Needs RSI<30 + green candle"
        elif r == 'BOUNCE':
            return f"📍 **VERDICT: ⚠️ BOUNCE** | Risky | Wait for SMA50 reclaim (>${s50}) | Entry then: ${s50}"
        else:
            return f"📍 **VERDICT: ⏳ MONITOR** | Regime: {r}"

    elif t == 'AMZN':
        if r == 'PULLBACK':
            entry = s50 if s50 else fib50
            return f"📍 **VERDICT: 🟡 NEAR ENTRY** | {r} | Entry: ${entry} (SMA50) | Stop: ${round(entry-1.5*atr,2)} | TP1: ${s20} | Confirmation: close >${round(s20,2)} or MACD hist >0"
        elif r == 'UPTREND':
            return f"📍 **VERDICT: 🟢 UPTREND** | Entry on dip: ${fib382}–${fib50} | Stop: ${round(fib618-atr,2)} | TP: ${h3m}"
        elif r == 'DOWNTREND':
            return f"📍 **VERDICT: 🔴 WAIT** | {r} | Entry: ${fib618}–${fib786} | Needs RSI<30 + green candle"
        elif r == 'BOUNCE':
            return f"📍 **VERDICT: ⚠️ BOUNCE** | Risky | Wait for SMA50 reclaim (>${s50}) | Entry then: ${s50}"
        else:
            return f"📍 **VERDICT: ⏳ MONITOR** | Regime: {r}"

    return f"📍 **VERDICT: ⏳** | {r}"


def calculate_dynamic_exits(a, pos):
    """Combine indicators with R-multiples to calculate adaptive exit levels.
    Returns dict with dynamic stop_loss, tp1, tp2, tp3, and signal tags."""
    price = a['price']
    entry = pos['entry']
    atr = a['atr14'] or 0
    rsi = a['rsi14']
    stoch = a.get('stoch_k')
    macd_hist = a.get('macd_hist')
    macd_val = a.get('macd_val')
    macd_sig = a.get('macd_sig')
    sma20 = a['sma20']
    sma50 = a['sma50']
    regime = a['regime']
    h3m = a.get('high_3m', price)
    fib382 = a.get('fib_382', price)
    fib50 = a.get('fib_50', price)

    R = atr  # 1R = 1 ATR from entry

    # === DYNAMIC STOP LOSS ===
    # Base: 2× ATR below entry
    sl_atr_mult = 2.0

    # Tighten if overbought (protect gains, higher reversal risk)
    if rsi and rsi > 85:
        sl_atr_mult = 1.5
    if stoch and stoch > 90:
        sl_atr_mult = min(sl_atr_mult, 1.5)

    stop_loss = round(entry - sl_atr_mult * R, 2)

    # Trail stop if in profit
    if price > entry + 2.5 * R:
        # Past TP2 → trail to TP1 level (lock 1.5R)
        stop_loss = max(stop_loss, round(entry + 1.5 * R, 2))
    elif price > entry + 1.5 * R:
        # Past TP1 → trail to breakeven
        stop_loss = max(stop_loss, round(entry + 0.5 * R, 2))

    # === DYNAMIC TAKE PROFIT ===
    # TP1: 1.5R (base partial exit)
    tp1_r = 1.5

    # TP2: Adjust based on momentum
    momentum_score = 0

    # MACD: bullish histogram = +1, bearish = -1
    if macd_hist is not None:
        if macd_hist > 0:
            momentum_score += 1
        else:
            momentum_score -= 1

    # MACD line above signal = +1
    if macd_val is not None and macd_sig is not None:
        if macd_val > macd_sig:
            momentum_score += 1
        else:
            momentum_score -= 1

    # RSI sweet spot (50-70 = healthy uptrend) = +1
    if rsi and 50 <= rsi <= 70:
        momentum_score += 1
    elif rsi and rsi > 80:
        momentum_score -= 1  # overbought = less upside

    # Stoch not overbought = +1
    if stoch and stoch < 80:
        momentum_score += 1
    elif stoch and stoch > 90:
        momentum_score -= 1

    # Regime: UPTREND = +1, DOWNTREND = -2
    if regime == 'UPTREND':
        momentum_score += 1
    elif regime == 'DOWNTREND':
        momentum_score -= 2

    # Price above SMA20 = +1
    if sma20 and price > sma20:
        momentum_score += 1

    # TP2 scales with momentum: weak=2R, neutral=2.5R, strong=3R
    if momentum_score >= 3:
        tp2_r = 3.0
        momentum_tag = "STRONG"
    elif momentum_score >= 1:
        tp2_r = 2.5
        momentum_tag = "NEUTRAL"
    else:
        tp2_r = 2.0
        momentum_tag = "WEAK"

    # TP3: extended target if momentum is strong + no resistance nearby
    tp3_r = None
    tp3_note = ""
    if momentum_score >= 3 and rsi and rsi < 75:
        tp3_r = 3.5
        tp3_note = "strong momentum"
    # Cap TP3 at 3M high resistance if nearby
    if tp3_r:
        tp3_price = round(entry + tp3_r * R, 2)
        if tp3_price > h3m * 1.02:
            tp3_price = round(h3m * 0.99, 2)
            tp3_note = f"capped at 3M high ${h3m:.2f}"
    else:
        tp3_price = None

    tp1 = round(entry + tp1_r * R, 2)
    tp2 = round(entry + tp2_r * R, 2)

    # === TRAILING STOP FOR WINNERS ===
    # If past TP3 with strong momentum, trail below current price and let it run
    trailing_active = False
    trail_stop = None
    if tp3_price and price > tp3_price and momentum_score >= 3:
        trailing_active = True
        # Trail at 2× ATR below current price
        trail_stop = round(price - 2 * R, 2)
        stop_loss = max(stop_loss, trail_stop)
        # Remove TP cap — let it run
        tp3_price = None
        tp3_note = "trailing — let profits run"

    # === SIGNAL-BASED EXIT TRIGGERS ===
    signals = []

    # Bearish MACD crossover
    if macd_hist is not None and macd_hist < 0:
        signals.append("MACD_BEARISH")

    # RSI rolling over from overbought
    if rsi and rsi < 70 and a.get('rsi14') and stoch and stoch < 80:
        # Check if was recently overbought (stoch was > 80 → now < 80)
        pass  # This needs historical data — skip for now

    # Stoch bearish crossover from overbought
    if stoch and stoch < 80:
        signals.append("STOCH_COOLING")

    # Below SMA20 in profit
    if sma20 and price < sma20 and price > entry:
        signals.append("BELOW_SMA20")

    return {
        'stop_loss': stop_loss,
        'sl_mult': sl_atr_mult,
        'tp1': tp1,
        'tp2': tp2,
        'tp3': tp3_price,
        'tp2_r': tp2_r,
        'tp3_r': tp3_r,
        'tp3_note': tp3_note,
        'momentum_score': momentum_score,
        'momentum_tag': momentum_tag,
        'trailing_active': trailing_active,
        'trail_stop': trail_stop,
        'signals': signals,
        'R': R,
    }


def check_exit_signals(a, pos):
    """Check exit signals for an open position. Returns alert message or None.
    Uses indicator-weighted R-multiples for dynamic exits."""
    ticker = a['ticker']
    price = a['price']
    entry = pos['entry']
    cost = pos['cost']
    pnl_pct = ((price / entry) - 1) * 100
    pnl_usd = round(cost * (pnl_pct / 100), 2)
    r = a['rsi14']
    atr = a['atr14'] or 0
    regime = a['regime']
    stoch = a.get('stoch_k')
    sma20 = a['sma20']
    sma50 = a['sma50']
    macd_hist = a.get('macd_hist')
    h3m = a.get('high_3m', price)

    # Calculate dynamic exits
    dx = calculate_dynamic_exits(a, pos)
    stop_loss = dx['stop_loss']
    tp1 = dx['tp1']
    tp2 = dx['tp2']
    tp3 = dx['tp3']

    alerts = []

    # === CRITICAL EXITS ===

    # 1. Stop Loss hit
    if price <= stop_loss:
        alerts.append(f"🛑 **STOP LOSS** @ ${price:.2f} (SL: ${stop_loss}, {dx['sl_mult']}×ATR) | P&L: {pnl_pct:+.1f}% (${pnl_usd:+.2f})")

    # 2. Regime breakdown while profitable
    if regime == 'DOWNTREND' and pnl_pct > 0:
        alerts.append(f"⚠️ **REGIME → DOWNTREND** | P&L: {pnl_pct:+.1f}% — exit before gains erode")

    # 3. Trailing stop triggered (was in profit, now pulling back)
    if price < entry + 0.5 * dx['R'] and pnl_pct > 5:
        alerts.append(f"📉 **PULLBACK** from profit | P&L: {pnl_pct:+.1f}% — trailing stop at ${stop_loss}")

    # === TAKE PROFIT SIGNALS ===

    # 4. RSI overbought + Stoch overbought (exhaustion)
    if r and r > 80 and stoch and stoch > 85:
        alerts.append(f"🔥 **OVERBOUGHT** RSI {r} + Stoch {stoch} — take partial | P&L: {pnl_pct:+.1f}%")

    # 5. TP1 hit
    if price >= tp1 and price < tp2:
        alerts.append(f"🎯 **TP1 HIT** ${tp1} (1.5R) | P&L: {pnl_pct:+.1f}% — partial exit, trail stop to breakeven")

    # 6. TP2 hit (only if not already trailing)
    if price >= tp2 and not dx['trailing_active']:
        alerts.append(f"🎯 **TP2 HIT** ${tp2} ({dx['tp2_r']}R) | P&L: {pnl_pct:+.1f}% — take profits, momentum: {dx['momentum_tag']}")

    # 7. Trailing stop active (letting profits run)
    if dx['trailing_active']:
        alerts.append(f"📈 **TRAILING** @ ${price:.2f} | Trail stop: ${stop_loss} (2×ATR below price) | P&L: {pnl_pct:+.1f}% — let profits run")

    # 8. TP3 hit (only if trailing didn't activate — i.e. momentum weakened)
    if tp3 and price >= tp3 and not dx['trailing_active']:
        tp3_label = f"{dx['tp3_r']}R" if dx['tp3_r'] else "extended"
        tp3_suffix = f" ({dx['tp3_note']})" if dx['tp3_note'] else ""
        alerts.append(f"🎯 **TP3 HIT** ${tp3} ({tp3_label}) | P&L: {pnl_pct:+.1f}% — full exit{tp3_suffix}")

    # 8. Near 3M high resistance (if no TP3 or price approaching it)
    if price >= h3m * 0.97 and not (tp3 and price >= tp3):
        alerts.append(f"📏 **Near 3M High** ${h3m:.2f} | P&L: {pnl_pct:+.1f}% — resistance zone")

    # 9. MACD bearish crossover while in profit
    if macd_hist is not None and macd_hist < 0 and pnl_pct > 5:
        alerts.append(f"📊 **MACD Bearish** | Hist: {macd_hist} | P&L: {pnl_pct:+.1f}% — momentum fading")

    # 10. Below SMA20 while profitable (trend weakening)
    if sma20 and price < sma20 and pnl_pct > 5:
        alerts.append(f"📉 **Below SMA20** (${sma20:.2f}) | P&L: {pnl_pct:+.1f}% — trend weakening")

    if not alerts:
        return None

    summary = f"🚨 **{ticker} EXIT SIGNAL**\n"
    summary += f"Price: ${price:.2f} | Entry: ${entry:.2f} | P&L: {pnl_pct:+.1f}% (${pnl_usd:+.2f})\n"
    summary += f"Regime: {regime} | RSI: {r} | Stoch: {stoch} | ATR: ${atr:.2f}\n"
    summary += f"Momentum: {dx['momentum_tag']} ({dx['momentum_score']:+d}) | R: ${dx['R']:.2f}\n"
    if dx['trailing_active']:
        summary += f"SL: ${stop_loss} (TRAILING 2×ATR) | TP1: ${tp1} | TP2: ${tp2} | TP3: ∞ (letting run)\n"
    else:
        tp3_str = f" | TP3: ${tp3}" if tp3 else ""
        summary += f"SL: ${stop_loss} ({dx['sl_mult']}×ATR) | TP1: ${tp1} (1.5R) | TP2: ${tp2} ({dx['tp2_r']}R){tp3_str}\n"
    for alert in alerts:
        summary += f"• {alert}\n"
    return summary


def main():
    now = datetime.now(BKK)
    now_str = now.strftime("%a %d %b %Y %H:%M ICT")

    # Skip weekends — market closed, data is stale
    if now.weekday() >= 5:
        return

    # US market hours in ICT: pre-market starts 16:00, market closes 04:00
    # Monitor 16:00-04:59 ICT (pre-market through after-hours)
    hour = now.hour
    if not (hour >= 16 or hour < 5):
        return  # market closed (05:00-15:59 ICT)

    results = []

    for ticker in ["GOOG", "RDDT", "GDDY", "VOO", "VXUS", "NVDU", "ZS", "BCC", "FBK", "AMZN"]:
        a = analyze_ticker(ticker)
        if not a:
            continue
        results.append(a)

    if not results:
        print(f"[{now_str}] No data available")
        return

    # Check each ticker for entry signals
    triggered = []
    for a in results:
        msg = None
        if a['ticker'] == 'GOOG':
            msg = check_entry_goog(a)
        elif a['ticker'] == 'RDDT':
            msg = check_entry_rddt(a)
        elif a['ticker'] == 'GDDY':
            msg = check_entry_gddy(a)
        elif a['ticker'] == 'PTC':
            msg = check_entry_ptc(a)
        elif a['ticker'] == 'VOO':
            msg = check_entry_voo(a)
        elif a['ticker'] == 'VXUS':
            msg = check_entry_vxus(a)
        elif a['ticker'] == 'BCC':
            msg = check_entry_bcc(a)
        elif a['ticker'] == 'FBK':
            msg = check_entry_fbk(a)
        elif a['ticker'] == 'AMZN':
            msg = check_entry_amzn(a)
        if msg and a['ticker'] not in POSITIONS:
            triggered.append(msg)

        # Check exit signals for open positions
        if a['ticker'] in POSITIONS:
            exit_msg = check_exit_signals(a, POSITIONS[a['ticker']])
            if exit_msg:
                triggered.append(exit_msg)

    if triggered:
        output = f"**📡 Entry Monitor — {now_str}**\n\n"
        output += "\n".join(triggered)
        print(output)
    # else: silent — no entry signals, no output

if __name__ == "__main__":
    main()
