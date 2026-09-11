#!/usr/bin/env python3
"""
11-Factor Confluence Scorer — reusable module for all crypto entries.
Import from watch_hype.py or run standalone: python3 confluence_score.py HYPE

Factors: Trend, VWAP, OBV, CMF, MFI, Funding, VPQ, Candle, Momentum(ROC-10), Wyckoff, VPOC
Scale: -10 to +10 (composite = weighted average of individual -1..+1 scores)
Entry threshold: ±0.50 (system minimum)
"""
import json, urllib.request, time
import numpy as np


def fetch_hyperliquid_4h(coin='HYPE', n=300):
    """Fetch 4H candles from Hyperliquid. Returns list of dicts."""
    now = int(time.time() * 1000)
    payload = {
        'type': 'candleSnapshot',
        'req': {
            'coin': coin, 'interval': '4h',
            'startTime': now - n * 4 * 3600 * 1000,
            'endTime': now,
            'limit': min(n, 500)
        }
    }
    req = urllib.request.Request(
        'https://api.hyperliquid.xyz/info',
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    return [{'time': c['t'], 'open': float(c['o']), 'high': float(c['h']),
             'low': float(c['l']), 'close': float(c['c']), 'volume': float(c['v'])} for c in data]


def fetch_funding(coin='HYPE'):
    """Fetch funding rate from Hyperliquid."""
    try:
        req = urllib.request.Request(
            'https://api.hyperliquid.xyz/info',
            data=json.dumps({'type': 'metaAndAssetCtxs'}).encode(),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        meta, ctxs = data[0], data[1]
        for i, asset in enumerate(meta['universe']):
            if asset['name'] == coin:
                fr = float(ctxs[i]['funding'])
                if fr > 0.001: return fr, 'extremely_bullish'
                elif fr > 0.0001: return fr, 'bullish'
                elif fr < -0.001: return fr, 'extremely_bearish'
                elif fr < -0.0001: return fr, 'bearish'
                return fr, 'neutral'
    except Exception:
        pass
    return 0.0, 'neutral'


# ── Indicator helpers ──
def _ema(data, p):
    if len(data) < p: return data[-1] if data else 0
    m = 2/(p+1); r = sum(data[:p])/p
    for v in data[p:]: r = (v-r)*m + r
    return r

def _sma(data, p):
    if len(data) < p: return sum(data)/len(data) if data else 0
    return sum(data[-p:])/p

def _rsi(closes, p=14):
    if len(closes) < p+1: return 50
    g = l = 0.0
    for i in range(len(closes)-p, len(closes)):
        ch = closes[i] - closes[i-1]
        g += max(ch, 0); l += abs(min(ch, 0))
    return 100 - 100/(1 + g/l) if l else 100

def _atr(candles, p=14):
    if len(candles) < p+1: return 1.0
    return sum(max(candles[i]['high']-candles[i]['low'],
                   abs(candles[i]['high']-candles[i-1]['close']),
                   abs(candles[i]['low']-candles[i-1]['close']))
               for i in range(len(candles)-p, len(candles))) / p

def _obv_trend(closes, volumes, lookback=20):
    if len(closes) < lookback+1: return 'neutral'
    obv = [0.0]
    for i in range(1, len(closes)):
        obv.append(obv[-1] + (volumes[i] if closes[i]>closes[i-1] else -volumes[i] if closes[i]<closes[i-1] else 0))
    s = _sma(obv, lookback)
    if obv[-1] > s*1.02: return 'bullish'
    elif obv[-1] < s*0.98: return 'bearish'
    return 'neutral'

def _cmf(candles, p=20):
    if len(candles) < p: return 0
    mf = []
    for c in candles[-p:]:
        hl = c['high'] - c['low']
        mf.append(((c['close']-c['low'])-(c['high']-c['close']))/hl * c['volume'] if hl else 0)
    vs = sum(c['volume'] for c in candles[-p:])
    return sum(mf)/vs if vs else 0

def _mfi(candles, p=14):
    if len(candles) < p+1: return 50
    pos = neg = 0.0
    for i in range(len(candles)-p, len(candles)):
        tp = (candles[i]['high']+candles[i]['low']+candles[i]['close'])/3
        tp_p = (candles[i-1]['high']+candles[i-1]['low']+candles[i-1]['close'])/3
        if tp > tp_p: pos += tp * candles[i]['volume']
        elif tp < tp_p: neg += tp * candles[i]['volume']
    return 100 - 100/(1+pos/neg) if neg else 100

def _vwap(candles, p=20):
    if len(candles) < p: p = len(candles)
    prices = [(c['high']+c['low']+c['close'])/3 for c in candles[-p:]]
    vols = [c['volume'] for c in candles[-p:]]
    cpv = cv = 0
    for pv, v in zip(prices, vols): cpv += pv*v; cv += v
    v = cpv/cv if cv else prices[-1]
    std = np.std(prices) if len(prices)>1 else 1
    return v, v+std, v-std

def _vp_quality(candles, p=50):
    if len(candles) < p: p = len(candles)
    prices = []
    for c in candles[-p:]: prices.extend([c['low'], c['high']])
    if not prices: return 0
    hist, _ = np.histogram(prices, bins=20)
    return max(hist)/sum(hist) if sum(hist) else 0

def _candle_pattern(c):
    body = abs(c['close']-c['open']); rng = c['high']-c['low']
    if rng == 0: return 'neutral'
    br = body/rng
    if c['close'] > c['open']:
        return 'bullish_engulfing' if br > 0.7 else 'doji' if br < 0.2 else 'neutral'
    else:
        return 'bearish_engulfing' if br > 0.7 else 'doji' if br < 0.2 else 'neutral'

def _trend(closes, e50, e200):
    if len(closes) < 50: return 'neutral', 0.0
    p = closes[-1]; a50 = p > e50; a200 = p > e200 if e200 else a50
    s = (e50 - closes[-5])/closes[-5]*100 if len(closes)>5 else 0
    if a50 and a200 and s > 0: return 'bullish', min(1.0, s*5)
    elif not a50 and not a200 and s < 0: return 'bearish', min(1.0, abs(s)*5)
    return 'neutral', 0.0


# ═══ MAIN SCORING FUNCTION ═══

def score(coin='HYPE', candles=None):
    """
    Compute 11-factor confluence score for a Hyperliquid perp.
    Returns dict with: composite, direction, factors dict, raw data.
    """
    if candles is None:
        candles = fetch_hyperliquid_4h(coin, 300)

    closes = [c['close'] for c in candles]
    volumes = [c['volume'] for c in candles]
    price = closes[-1]

    e50 = _ema(closes, 50)
    e200 = _ema(closes, 200) if len(closes) >= 200 else e50
    r = _rsi(closes)
    a = _atr(candles)
    vol_avg = _sma(volumes, 20)
    vol_ratio = volumes[-1]/vol_avg if vol_avg else 1
    obv_t = _obv_trend(closes, volumes)
    cmf_val = _cmf(candles)
    mfi_val = _mfi(candles)
    vwap_val, _, _ = _vwap(candles)
    price_vs_vwap = (price - vwap_val) / vwap_val
    vpq = _vp_quality(candles)
    cp = _candle_pattern(candles[-1])
    trend, trend_str = _trend(closes, e50, e200)
    roc10 = (closes[-1]/closes[-11]-1)*100 if len(closes)>10 else 0
    fund_rate, fund_sent = fetch_funding(coin)

    # ── Score each factor (-1 to +1) ──
    scores = {}

    # 1. Trend (w=2.0)
    scores['TREND'] = trend_str if trend=='bullish' else -trend_str if trend=='bearish' else 0

    # 2. VWAP (w=1.5)
    if price_vs_vwap < -0.002: scores['VWAP'] = min(1.0, abs(price_vs_vwap)*100)
    elif price_vs_vwap > 0.002: scores['VWAP'] = -min(1.0, abs(price_vs_vwap)*100)
    else: scores['VWAP'] = 0

    # 3. OBV (w=1.0)
    scores['OBV'] = 0.7 if obv_t=='bullish' else -0.7 if obv_t=='bearish' else 0

    # 4. CMF (w=1.0)
    scores['CMF'] = max(-1, min(1, cmf_val*2))

    # 5. MFI (w=1.0)
    if mfi_val > 80: scores['MFI'] = -0.5
    elif mfi_val < 20: scores['MFI'] = 0.5
    elif mfi_val > 60: scores['MFI'] = 0.3
    elif mfi_val < 40: scores['MFI'] = -0.3
    else: scores['MFI'] = 0

    # 6. Funding (w=1.5) — contrarian
    if fund_sent == 'extremely_bullish': scores['FUNDING'] = -0.5
    elif fund_sent == 'bullish': scores['FUNDING'] = 0.2
    elif fund_sent == 'extremely_bearish': scores['FUNDING'] = 0.5
    elif fund_sent == 'bearish': scores['FUNDING'] = -0.2
    else: scores['FUNDING'] = 0

    # 7. VP Quality (w=2.0)
    if vpq > 0.15: scores['VPQ'] = min(1.0, vpq*5)
    elif vpq > 0.10: scores['VPQ'] = 0.5
    else: scores['VPQ'] = 0

    # 8. Candle (w=1.5)
    if 'bullish' in cp: scores['CANDLE'] = 0.8
    elif 'bearish' in cp: scores['CANDLE'] = -0.8
    else: scores['CANDLE'] = 0

    # 9. Momentum ROC-10 (w=1.0)
    scores['MOM'] = max(-1, min(1, roc10/2))

    # 10. Wyckoff (w=2.5)
    wyckoff = 0
    if r < 30 and cmf_val < -0.05 and vol_ratio > 1.5:
        wyckoff = 0.8  # Capitulation
    elif r < 30 and cmf_val < 0:
        wyckoff = 0.3  # Mild oversold
    scores['WYCKOFF'] = wyckoff

    # 11. VPOC (w=1.5)
    scores['VPOC'] = 0.5 if vpq > 0.10 and abs(price_vs_vwap) < 0.02 else 0

    # ── Weighted composite ──
    weights = {'TREND':2.0,'VWAP':1.5,'OBV':1.0,'CMF':1.0,'MFI':1.0,
               'FUNDING':1.5,'VPQ':2.0,'CANDLE':1.5,'MOM':1.0,'WYCKOFF':2.5,'VPOC':1.5}
    total_w = sum(weights.values())
    weighted = sum(scores[k]*weights[k] for k in scores)
    composite = weighted / total_w

    direction = 'long' if composite >= 0.5 else 'short' if composite <= -0.5 else 'none'

    return {
        'composite': round(composite, 2),
        'direction': direction,
        'threshold': 0.5,
        'passes': abs(composite) >= 0.5,
        'factors': {k: {'score': scores[k], 'weight': weights[k], 'contrib': round(scores[k]*weights[k], 2)} for k in scores},
        'raw': {
            'price': price, 'rsi': r, 'atr': a, 'ema50': e50, 'ema200': e200,
            'trend': trend, 'cmf': cmf_val, 'mfi': mfi_val, 'obv': obv_t,
            'vol_ratio': vol_ratio, 'vpq': vpq, 'candle': cp, 'roc10': roc10,
            'funding': fund_rate, 'funding_sent': fund_sent, 'vwap': vwap_val,
            'price_vs_vwap': price_vs_vwap
        }
    }


def format_alert(result, coin='HYPE'):
    """Format confluence score as a Telegram-ready alert snippet."""
    r = result
    d = r['raw']
    lines = []
    lines.append(f"📊 **{coin} 11-Factor Confluence: {r['composite']:+.2f}**")
    lines.append(f"Direction: {r['direction'].upper()} | Passes gate: {'✅' if r['passes'] else '❌'} (need ±{r['threshold']})")
    lines.append("")

    # Top contributors
    bullish = sorted([(k,v) for k,v in r['factors'].items() if v['contrib']>0], key=lambda x: -x[1]['contrib'])
    bearish = sorted([(k,v) for k,v in r['factors'].items() if v['contrib']<0], key=lambda x: x[1]['contrib'])
    if bullish:
        lines.append("🟢 " + " | ".join(f"{k} {v['contrib']:+.2f}" for k,v in bullish[:3]))
    if bearish:
        lines.append("🔴 " + " | ".join(f"{k} {v['contrib']:+.2f}" for k,v in bearish[:3]))
    lines.append("")
    lines.append(f"Price: ${d['price']:.2f} | RSI: {d['rsi']:.1f} | CMF: {d['cmf']:.3f} | MFI: {d['mfi']:.1f}")
    lines.append(f"OBV: {d['obv']} | Mom ROC-10: {d['roc10']:+.2f}% | Funding: {d['funding_sent']}")

    if not r['passes']:
        lines.append(f"\n⚠️ Score {r['composite']:+.2f} below threshold ±{r['threshold']} — no entry")
    else:
        lines.append(f"\n✅ Score {r['composite']:+.2f} passes gate — entry valid")

    return "\n".join(lines)


if __name__ == '__main__':
    import sys
    coin = sys.argv[1] if len(sys.argv) > 1 else 'HYPE'
    result = score(coin)
    print(format_alert(result, coin))
    print(f"\n--- Raw factors ---")
    for k, v in result['factors'].items():
        bar = '█' * int(abs(v['contrib'])*5) if v['contrib'] != 0 else '·'
        print(f"  {k:<12} {v['score']:>+5.2f}  {v['weight']:>5.1f}x  {v['contrib']:>+6.2f}  {bar}")
