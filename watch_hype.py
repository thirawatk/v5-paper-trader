#!/usr/bin/env python3
"""
HYPE Entry Confirmation Watcher — Hyperliquid perps data, 4h candles.

Triggers (either):
  1. 4h close > $80.20 (previous swing high) + green candle
  2. CMF > 0.15 AND ROC-10 turns positive

Kill: 4h close < $73.47 (2×ATR stop level) → setup dead
Watchdog: silent unless trigger/kill fires.
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, "/root/.hermes/profiles/trader/skills/hyperliquid/scripts")
sys.path.insert(0, "/root/.hermes/profiles/trader/scripts")
from hyperliquid_client import _post_info, _normalize_candles, _hours_ago_ms

BKK = timezone(timedelta(hours=7))
STATE_FILE = "/root/.hermes/profiles/trader/scripts/hype_watch_state.json"

TRIGGER_CLOSE = 80.20
CMF_TRIGGER = 0.15
KILL_LEVEL = 73.47
MAX_BARS = 30   # ~5 days of 4h bars


def fetch_4h(hours=24 * 14):
    c = _normalize_candles(_post_info({
        "type": "candleSnapshot",
        "req": {"coin": "HYPE", "interval": "4h", "startTime": _hours_ago_ms(hours), "endTime": None},
    }))
    for row in c:
        for k in ('open', 'high', 'low', 'close', 'volume'):
            row[k] = float(row[k])
    return c


def cmf_4h(candles, p=20):
    """Chaikin Money Flow over last p candles."""
    if len(candles) < p:
        return None
    mfm_sum, vol_sum = 0.0, 0.0
    for c in candles[-p:]:
        h, l, cl, v = c['high'], c['low'], c['close'], c['volume']
        if h == l or v == 0:
            continue
        mfm = ((cl - l) - (h - cl)) / (h - l)
        mfm_sum += mfm * v
        vol_sum += v
    return mfm_sum / vol_sum if vol_sum else None


def roc_10(candles):
    if len(candles) < 11:
        return None
    return (candles[-1]['close'] / candles[-11]['close'] - 1) * 100


def main():
    now = datetime.now(BKK)
    now_str = now.strftime("%a %d %b %H:%M ICT")

    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)

    try:
        candles = fetch_4h()
    except Exception:
        return  # data unavailable — silent, retry next tick
    if len(candles) < 30:
        return

    price = candles[-1]['close']
    prev = candles[-2]['close']
    green = price > prev
    cmf = cmf_4h(candles)
    roc = roc_10(candles)
    atr = sum(max(c['high'] - c['low'], abs(c['high'] - candles[i-1]['close']), abs(c['low'] - candles[i-1]['close']))
              for i, c in enumerate(candles[-14:], len(candles) - 14)) / 14

    # Session counting on 4h bars
    bar_id = candles[-1]['time']
    if state.get('last_bar') != bar_id:
        state['bars'] = state.get('bars', 0) + 1
        state['last_bar'] = bar_id

    alert = None
    triggered_by = None

    if price > TRIGGER_CLOSE and green:
        triggered_by = f"4h close ${price:.2f} > ${TRIGGER_CLOSE} + green candle"
    elif cmf is not None and cmf > CMF_TRIGGER and roc is not None and roc > 0:
        triggered_by = f"CMF {cmf:.3f} > {CMF_TRIGGER} AND ROC {roc:+.2f}% turned positive"

    if triggered_by and state.get('alerted') != 'entry':
        alert = (
            f"🟢 **HYPE ENTRY CONFIRMED**\n"
            f"Price: ${price:.2f} | Trigger: {triggered_by}\n"
            f"CMF: {cmf:.3f} | ROC-10: {roc:+.2f}% | Bars waited: {state.get('bars', 0)}\n\n"
            f"**Execution (Wyckoff stop-order discipline):**\n"
            f"1. Note trigger candle HIGH & LOW\n"
            f"2. Place BUY-STOP ~0.1% above candle high\n"
            f"3. SL: below trigger candle low (or $73.47, whichever is tighter)\n"
            f"4. TP1: $82.86 — sell half, stop to breakeven\n"
            f"5. TP2: $85.55 | TP3: $88.23 — trail rest\n"
            f"6. Size: 1% risk (2×ATR stop = $2.68/coin)"
        )
        state['alerted'] = 'entry'

    elif price < KILL_LEVEL and state.get('alerted') not in ('killed', 'entry'):
        alert = (
            f"🔴 **HYPE SETUP DEAD**\n"
            f"Price: ${price:.2f} below ${KILL_LEVEL} (2×ATR stop zone)\n"
            f"No entry — stand down."
        )
        state['alerted'] = 'killed'

    elif state.get('bars', 0) > MAX_BARS and state.get('alerted') not in ('expired', 'entry'):
        alert = (
            f"⏰ **HYPE SETUP EXPIRED**\n"
            f"{MAX_BARS}+ 4h bars without confirmation. Last: ${price:.2f}\n"
            f"Re-scan needed if still interested."
        )
        state['alerted'] = 'expired'

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=1)

    if alert:
        print(f"**🎯 HYPE Watcher — {now_str}**\n\n{alert}")
    # else silent


if __name__ == "__main__":
    main()
