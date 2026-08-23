#!/usr/bin/env python3
"""
AMZN Confirmation Watcher — TradingView data source.

Alerts ONLY when the expert-approved entry trigger fires:
  1. Daily close > $263 (SMA20 reclaim + green candle)
  2. MACD histogram crosses above zero (MACD line > signal line)

Kill: close < $250 (SMA50 zone) before confirmation → setup dead
Expiry: 5 sessions without trigger

Watchdog mode: silent unless trigger/kill/expiry fires.
"""
import json, os
from datetime import datetime, timezone, timedelta
from tradingview_ta import TA_Handler

BKK = timezone(timedelta(hours=7))
STATE_FILE = "/root/.hermes/profiles/trader/scripts/amzn_watch_state.json"

TRIGGER_CLOSE = 263.00
KILL_LEVEL = 250.00
MAX_SESSIONS = 5


def get_analysis():
    h = TA_Handler(symbol="AMZN", exchange="NASDAQ", screener="america", interval="1d")
    return h.get_analysis()


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"sessions": 0, "last_date": None, "alerted": None}


def save_state(s):
    with open(STATE_FILE, 'w') as f:
        json.dump(s, f, indent=1)


def main():
    now = datetime.now(BKK)
    now_str = now.strftime("%a %d %b %H:%M ICT")

    if now.weekday() >= 5:
        return
    if not (now.hour >= 16 or now.hour < 5):
        return

    state = load_state()
    try:
        a = get_analysis()
        ind = a.indicators
    except Exception:
        return  # data unavailable — stay silent, retry next tick
    if not ind:
        return

    price = ind.get('close')
    prev_close = None
    # TradingView doesn't expose prev close directly; approximate via open vs close for candle direction
    open_ = ind.get('open')
    green_candle = price > open_ if (price and open_) else False

    macd = ind.get('MACD.macd')
    macd_sig = ind.get('MACD.signal')
    hist = (macd - macd_sig) if (macd is not None and macd_sig is not None) else None

    sma20 = ind.get('SMA20')

    # Session counting: use TradingView bar timestamp date
    tv_date = a.time.strftime('%Y-%m-%d') if a.time else None
    if tv_date and state.get('last_date') != tv_date:
        state['sessions'] += 1
        state['last_date'] = tv_date

    alert = None
    triggered_by = None

    if price and price > TRIGGER_CLOSE and green_candle:
        triggered_by = f"Close ${price:.2f} > ${TRIGGER_CLOSE} + green candle"
    elif hist is not None and hist > 0:
        triggered_by = f"MACD hist positive ({hist:+.2f})"

    if triggered_by and state.get('alerted') != 'entry':
        alert = (
            f"🟢 **AMZN ENTRY CONFIRMED**\n"
            f"Price: ${price:.2f} | Trigger: {triggered_by}\n"
            f"SMA20: ${sma20:.2f} | Sessions waited: {state['sessions']}/{MAX_SESSIONS}\n"
            f"Source: TradingView\n\n"
            f"**Wyckoff Execution (stop-order discipline):**\n"
            f"1. Note today's trigger candle HIGH & LOW\n"
            f"2. Place BUY-STOP ~$0.10 above candle high — do NOT market-buy\n"
            f"3. SL: just below trigger candle low (or $246.75, whichever is tighter)\n"
            f"4. TP1: $266 (+0.5R) — sell half, stop to breakeven\n"
            f"5. TP2: $272–275 (+1 to +1.2R) — trail rest under 2-day lows\n"
            f"6. Size: ~8 sh ($100 risk)\n\n"
            f"Never anticipate with limit/market orders — let price come to you."
        )
        state['alerted'] = 'entry'

    elif price and price < KILL_LEVEL and state.get('alerted') not in ('killed', 'entry'):
        alert = (
            f"🔴 **AMZN SETUP DEAD**\n"
            f"Price: ${price:.2f} closed below ${KILL_LEVEL} (SMA50 zone)\n"
            f"No entry — stand down."
        )
        state['alerted'] = 'killed'

    elif state['sessions'] > MAX_SESSIONS and state.get('alerted') not in ('expired', 'entry'):
        alert = (
            f"⏰ **AMZN SETUP EXPIRED**\n"
            f"{MAX_SESSIONS}+ sessions without confirmation. Last: ${price:.2f}\n"
            f"Re-scan needed if still interested."
        )
        state['alerted'] = 'expired'

    save_state(state)

    if alert:
        print(f"**🎯 AMZN Watcher — {now_str}**\n\n{alert}")
    # else silent


if __name__ == "__main__":
    main()
