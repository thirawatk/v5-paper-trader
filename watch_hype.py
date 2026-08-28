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

# ── PARTIALLY CLOSED POSITION (entered 2026-08-25 @ $80.80) ──
# TP1 (50% of 3.93 = 1.965) @ $84.82 + TP2 (50% of remainder = 0.9825) @ $85.55
# Runner: 0.9825 HYPE (~25%) still open — profit run mode
POSITION = {
    "active": True,         # still tracking the runner (TP3 / SL)
    "entry": 80.80,
    "atr": 2.68,           # ATR(14) at entry
    "sl": 75.44,           # entry - 2×ATR
    "tp1": 84.82,          # entry + 1.5R
    "tp2": 87.50,          # entry + 2.5R (original plan: 85.55 — user executed there)
    "tp3": 90.18,          # entry + 3.5R
    "entry_date": "2026-08-25",
    "remaining_qty": 0.9825,   # 25% runner after TP1+TP2 tranches
}

# ── RE-ENTRY OBSERVATION (runs while position held) ──
REENTRY = {
    "enabled": True,
    "ema_period": 50,       # pullback zone = EMA50
    "zone_pct": 0.03,       # within +3% / -6% of EMA50
    "rsi_max": 40,          # RSI must be < 40 for pullback zone
    "breakout_level": 86.73,  # 4h close above = breakout re-entry (prior rejection high)
    "breakout_retreat_pct": 0.05,  # re-arm breakout alert when price retreats 5% below level
}


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


def rsi_4h(candles, p=14):
    closes = [c['close'] for c in candles]
    if len(closes) < p + 1:
        return None
    gains = losses = 0.0
    for i in range(len(closes) - p, len(closes)):
        ch = closes[i] - closes[i - 1]
        gains += max(ch, 0)
        losses += abs(min(ch, 0))
    if losses == 0:
        return 100
    return 100 - 100 / (1 + gains / losses)


def ema_4h(candles, p=50):
    closes = [c['close'] for c in candles]
    if len(closes) < p:
        return None
    m = 2 / (p + 1)
    r = sum(closes[:p]) / p
    for v in closes[p:]:
        r = (v - r) * m + r
    return r


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

    # ═══ POSITION TRACKING MODE (entry confirmed) ═══
    if POSITION.get("active"):
        pos = POSITION
        entry = pos["entry"]
        pnl = (price - entry) / entry * 100
        pnl_usd_per_coin = price - entry

        # TP checks (from high of bar to catch wicks)
        bar_high = candles[-1]['high']

        if price <= pos["sl"] or candles[-1]['low'] <= pos["sl"]:
            alert = (
                f"🔴 **HYPE STOP LOSS HIT**\n"
                f"Price: ${price:.2f} | SL: ${pos['sl']:.2f}\n"
                f"P&L: {pnl:+.2f}% (${pnl_usd_per_coin:+.2f}/coin)\n"
                f"Exited — risk managed. {pos['entry_date']} entry."
            )
        elif bar_high >= pos["tp3"] and state.get('alerted') != 'tp3':
            alert = (
                f"🎯 **HYPE TP3 HIT** ${pos['tp3']:.2f}\n"
                f"Price: ${price:.2f} | P&L: {pnl:+.2f}% (${pnl_usd_per_coin:+.2f}/coin)\n"
                f"+3.5R — full exit or trail with 2×ATR below price"
            )
            state['alerted'] = 'tp3'
        elif bar_high >= pos["tp2"] and state.get('alerted') not in ('tp3', 'tp2'):
            alert = (
                f"🎯 **HYPE TP2 HIT** ${pos['tp2']:.2f}\n"
                f"Price: ${price:.2f} | P&L: {pnl:+.2f}% (${pnl_usd_per_coin:+.2f}/coin)\n"
                f"+2.5R — sell rest or move stop to breakeven"
            )
            state['alerted'] = 'tp2'
        elif bar_high >= pos["tp1"] and state.get('alerted') not in ('tp3', 'tp2', 'tp1'):
            alert = (
                f"🎯 **HYPE TP1 HIT** ${pos['tp1']:.2f}\n"
                f"Price: ${price:.2f} | P&L: {pnl:+.2f}% (${pnl_usd_per_coin:+.2f}/coin)\n"
                f"+1.5R — sell half, move stop to breakeven"
            )
            state['alerted'] = 'tp1'

        if alert is None and state.get('alerted') in ('tp1', 'tp2', 'tp3'):
            # After partial exits, also alert on SL hit (breakeven move)
            if price <= entry:
                alert = (
                    f"⚠️ **HYPE back to breakeven** ${price:.2f}\n"
                    f"Entry ${entry:.2f} | Stop moved to BE after TP1 — protect gains"
                )
                state['alerted'] = 'be'

        if alert:
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=1)
            print(f"**📡 HYPE Position Monitor — {now_str}**\n\n{alert}")
            return

        # ═══ RE-ENTRY OBSERVATION (position held — watch for next entry) ═══
        if REENTRY.get("enabled"):
            r4 = rsi_4h(candles)
            e50 = ema_4h(candles, REENTRY["ema_period"])
            if e50 and r4 is not None:
                in_zone = (r4 < REENTRY["rsi_max"]
                           and price <= e50 * (1 + REENTRY["zone_pct"])
                           and price >= e50 * (1 - REENTRY["zone_pct"] * 2))
                if in_zone:
                    if not state.get('reentry_zone'):
                        alert = (
                            f"📍 **HYPE RE-ENTRY ZONE**\n"
                            f"Price: ${price:.2f} | RSI: {r4:.1f} | EMA50: ${e50:.2f}\n"
                            f"Pullback to EMA50 — watch for green 4h close to confirm\n"
                            f"Plan: entry EMA50 zone | SL below zone low (2×ATR ≈ ${atr:.2f}) | TPs 1.5R/2.5R from fill"
                        )
                        state['reentry_zone'] = True
                    elif green and not state.get('reentry_confirmed'):
                        alert = (
                            f"🟢 **HYPE RE-ENTRY CONFIRMED**\n"
                            f"Price: ${price:.2f} | RSI: {r4:.1f} | EMA50: ${e50:.2f} | Green 4h close\n"
                            f"**Execution (Wyckoff):** BUY-STOP above trigger candle high | SL below candle low | TPs 1.5R/2.5R from fill"
                        )
                        state['reentry_confirmed'] = True
                else:
                    state['reentry_zone'] = False
                    state['reentry_confirmed'] = False  # re-arm after leaving zone

            # Breakout re-entry (prior rejection high)
            if price > REENTRY["breakout_level"] and not state.get('reentry_breakout'):
                alert = (
                    f"🚀 **HYPE BREAKOUT RE-ENTRY**\n"
                    f"Price: ${price:.2f} > ${REENTRY['breakout_level']} (prior rejection high)\n"
                    f"**Execution:** BUY-STOP above breakout candle high | SL below breakout candle low | TP: prior TP3 $90.18 → extension"
                )
                state['reentry_breakout'] = True
            elif price < REENTRY["breakout_level"] * (1 - REENTRY["breakout_retreat_pct"]):
                state['reentry_breakout'] = False  # re-arm after retreat

            if alert:
                with open(STATE_FILE, 'w') as f:
                    json.dump(state, f, indent=1)
                print(f"**📡 HYPE Re-Entry Watch — {now_str}**\n\n{alert}")
                return

        return  # silent while position healthy

    # ═══ ENTRY CONFIRMATION MODE (no position yet) ═══
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
            f"4. TPs: 1.5R / 2.5R / 3.5R from ACTUAL entry (recalculated at fill — do NOT reuse old levels)\n"
            f"5. Size: 1% risk (2×ATR stop = $2.68/coin)\n"
            f"6. TP1 hit → sell half, stop to breakeven; TP2 → sell rest or trail"
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
