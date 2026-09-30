#!/usr/bin/env python3
"""
Stock MACD Monitor — CM_Ult_MacD_MTF Crossover Alerts
=====================================================
Monitors stocks for 2-stage signal:
  Stage 1 (Entry): MACD bullish divergence + Heikin Ashi green + VIX fear
  Stage 2 (Confirm): EMA 50 golden cross above EMA 200 (within 30 days of entry)

Stage 1 fires immediately when conditions align. Stage 2 fires when EMA confirms the trend.

Default: fast=12, slow=26, signal=9 (standard MACD params)

Sends alerts via Trader Telegram bot when crossover detected.
Designed to run as a Hermes cron job.

Usage: python3 stock_macd_monitor.py [--check] [--force]
  --check: Only check and alert (default)
  --force: Force alert even if already alerted today
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

# ── Configuration ──
WATCHLIST = ["VOO", "VXUS"]
FAST_LENGTH = 12
SLOW_LENGTH = 26
SIGNAL_LENGTH = 9
MACD_DEPTH_THRESH = -0.5  # MACD must be below this (deep negative)
VIX_FEAR_THRESH = 20.0    # VIX must be above this (elevated fear)
EMA_FAST_LEN = 50         # EMA fast for golden cross
EMA_SLOW_LEN = 200        # EMA slow for golden cross
CONFIRM_WINDOW = 30       # Days after entry to watch for golden cross

# State file to track last alert per symbol
STATE_FILE = "/root/.hermes/profiles/trader/scripts/macd_monitor_state.json"

# Trader bot token
ENV_FILE = "/root/.hermes/profiles/trader/.env"

# ── Helpers ──

def load_env():
    """Load TELEGRAM_BOT_TOKEN from .env file."""
    token = None
    chat_id = None
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("TELEGRAM_HOME_CHANNEL="):
                    chat_id = line.split("=", 1)[1].strip().strip('"').strip("'")
    # Fallback to Trading Team
    if not chat_id:
        chat_id = "-5195094488"
    return token, chat_id


def load_state():
    """Load monitor state (last alert timestamps)."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    """Save monitor state."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_ohlcv(symbol, period="6mo"):
    """Fetch daily OHLCV data from Yahoo Finance."""
    import yfinance as yf
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    if df.empty:
        raise ValueError(f"No data for {symbol}")
    return df


def compute_macd(close_prices, fast=12, slow=26, signal=9):
    """
    Compute MACD, Signal, and Histogram.
    Matches TradingView CM_Ult_MacD_MTF calculation:
      MACD = EMA(fast) - EMA(slow)
      Signal = SMA(MACD, signal)
      Histogram = MACD - Signal
    """
    import pandas as pd

    # EMA calculations
    ema_fast = close_prices.ewm(span=fast, adjust=False).mean()
    ema_slow = close_prices.ewm(span=slow, adjust=False).mean()

    # MACD line
    macd = ema_fast - ema_slow

    # Signal line (SMA of MACD)
    signal_line = macd.rolling(window=signal).mean()

    # Histogram
    histogram = macd - signal_line

    return macd, signal_line, histogram


def compute_heikin_ashi(df):
    """
    Compute Heikin Ashi candles from OHLCV data.
    HA Close = (Open + High + Low + Close) / 4
    HA Open  = (prev HA Open + prev HA Close) / 2
    HA High  = max(High, HA Open, HA Close)
    HA Low   = min(Low, HA Open, HA Close)
    """
    import pandas as pd
    ha_close = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4

    # HA Open: start with first candle's midpoint, then recursive
    ha_open = df["Open"].copy()
    ha_open.iloc[0] = (df["Open"].iloc[0] + df["Close"].iloc[0]) / 2
    for i in range(1, len(ha_open)):
        ha_open.iloc[i] = (ha_open.iloc[i - 1] + ha_close.iloc[i - 1]) / 2

    ha_high = pd.concat([df["High"], ha_open, ha_close], axis=1).max(axis=1)
    ha_low = pd.concat([df["Low"], ha_open, ha_close], axis=1).min(axis=1)

    return ha_open, ha_high, ha_low, ha_close


def detect_crossover(histogram):
    """
    Detect bullish crossover: histogram goes from negative to positive.
    Returns True if the latest bar shows a crossover.
    """
    if len(histogram) < 2:
        return False

    prev = histogram.iloc[-2]
    curr = histogram.iloc[-1]

    # Bullish crossover: was negative, now positive (or zero)
    return prev < 0 and curr >= 0


def detect_ha_green(ha_open, ha_close):
    """
    Detect Heikin Ashi green candle: HA Close > HA Open.
    Returns True if the latest bar is green (bullish).
    """
    return ha_close.iloc[-1] > ha_open.iloc[-1]


def detect_ema_golden_cross(close, ema_fast_len=50, ema_slow_len=200):
    """
    Detect EMA golden cross: EMA 50 crosses above EMA 200.
    Returns (crossed_today, ema_fast_val, ema_slow_val).
    """
    import pandas as pd
    ema_fast = close.ewm(span=ema_fast_len, adjust=False).mean()
    ema_slow = close.ewm(span=ema_slow_len, adjust=False).mean()

    if len(ema_fast) < 2:
        return False, None, None

    crossed = (ema_fast.iloc[-1] > ema_slow.iloc[-1] and
               ema_fast.iloc[-2] <= ema_slow.iloc[-2])

    return crossed, ema_fast.iloc[-1], ema_slow.iloc[-1]


def fetch_vix():
    """Fetch current VIX value from Yahoo Finance."""
    import yfinance as yf
    vix = yf.Ticker("^VIX")
    hist = vix.history(period="5d")
    if hist.empty:
        return None
    return hist["Close"].iloc[-1]


def send_telegram_alert(token, chat_id, message):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true"
    }).encode()

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read())
        if result.get("ok"):
            print(f"  ✅ Alert sent to chat {chat_id}")
            return True
        else:
            print(f"  ❌ Telegram error: {result}")
            return False
    except Exception as e:
        print(f"  ❌ Failed to send alert: {e}")
        return False


def format_alert(symbol, macd_val, signal_val, hist_val, close_price, ha_color, vix_val):
    """Format the Stage 1 entry alert."""
    now = datetime.now(timezone(timedelta(hours=7)))
    return (
        f"🔔 *MACD 3-Way Confluence — Entry Signal*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"*Stock:* {symbol}\n"
        f"*Stage:* 1️⃣ Entry (awaiting EMA confirmation)\n"
        f"*Confluence:* MACD depth + HA green + VIX fear\n"
        f"*Close:* ${close_price:.2f}\n"
        f"*MACD:* {macd_val:.4f} (< {MACD_DEPTH_THRESH})\n"
        f"*Signal:* {signal_val:.4f}\n"
        f"*Histogram:* {hist_val:.4f} (↗ positive)\n"
        f"*Heikin Ashi:* {ha_color}\n"
        f"*VIX:* {vix_val:.1f} (≥ {VIX_FEAR_THRESH} fear)\n"
        f"*Next:* Watching for EMA {EMA_FAST_LEN}/{EMA_SLOW_LEN} golden cross\n"
        f"*Timeframe:* Daily\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"_{now.strftime('%Y-%m-%d %H:%M BKK')}_"
    )


def format_confirm_alert(symbol, close_price, ema_fast, ema_slow, entry_date, entry_close):
    """Format the Stage 2 confirmation alert."""
    now = datetime.now(timezone(timedelta(hours=7)))
    days_since = (now - datetime.strptime(entry_date, "%Y-%m-%d").replace(tzinfo=timezone(timedelta(hours=7)))).days
    price_change = ((close_price - entry_close) / entry_close) * 100
    return (
        f"✅ *EMA Golden Cross — Trend Confirmed*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"*Stock:* {symbol}\n"
        f"*Stage:* 2️⃣ Confirmed (trend reversal)\n"
        f"*Close:* ${close_price:.2f} ({price_change:+.1f}% from entry)\n"
        f"*EMA {EMA_FAST_LEN}:* ${ema_fast:.2f}\n"
        f"*EMA {EMA_SLOW_LEN}:* ${ema_slow:.2f}\n"
        f"*Signal:* EMA {EMA_FAST_LEN} crossed above EMA {EMA_SLOW_LEN}\n"
        f"*Entry:* {entry_date} @ ${entry_close:.2f}\n"
        f"*Days since entry:* {days_since}\n"
        f"*Timeframe:* Daily\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"_{now.strftime('%Y-%m-%d %H:%M BKK')}_"
    )


def format_status(symbol, macd_val, signal_val, hist_val, close_price, crossed, ha_green, macd_deep):
    """Format status message for no-signal case."""
    trend = "↗" if hist_val > 0 else "↘" if hist_val < 0 else "→"
    ha_icon = "🟢" if ha_green else "🔴"
    depth_icon = "✅" if macd_deep else "❌"
    return (
        f"*{symbol}*: ${close_price:.2f} | "
        f"MACD={macd_val:.4f}{depth_icon} | "
        f"Hist={hist_val:.4f} {trend} | HA={ha_icon}"
    )


# ── Main ──

def main():
    import pandas as pd  # needed for compute_heikin_ashi

    force = "--force" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    token, chat_id = load_env()
    if not token:
        print("❌ No TELEGRAM_BOT_TOKEN found in", ENV_FILE)
        sys.exit(1)

    state = load_state()
    today = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d")

    alerts_sent = 0
    status_lines = []

    print(f"📊 Stock MACD Monitor — {today}")
    print(f"   Watchlist: {', '.join(WATCHLIST)}")
    print(f"   Params: MACD({FAST_LENGTH},{SLOW_LENGTH},{SIGNAL_LENGTH})")
    print(f"   Confluence: MACD < {MACD_DEPTH_THRESH} + HA green + VIX ≥ {VIX_FEAR_THRESH}")
    print()

    # Fetch VIX once
    vix_val = fetch_vix()
    vix_str = f"{vix_val:.1f}" if vix_val else "N/A"
    vix_fear = vix_val is not None and vix_val >= VIX_FEAR_THRESH
    print(f"   VIX: {vix_str} {'🔴 FEAR' if vix_fear else '🟢 calm'}")
    print()

    for symbol in WATCHLIST:
        print(f"🔍 Checking {symbol}...")

        try:
            # Fetch data (1y for EMA 200 warmup)
            df = fetch_ohlcv(symbol, period="1y")
            close = df["Close"]

            # Compute MACD
            macd, signal_line, histogram = compute_macd(
                close, FAST_LENGTH, SLOW_LENGTH, SIGNAL_LENGTH
            )

            # Compute Heikin Ashi
            ha_open, ha_high, ha_low, ha_close = compute_heikin_ashi(df)

            # Latest values
            macd_val = macd.iloc[-1]
            signal_val = signal_line.iloc[-1]
            hist_val = histogram.iloc[-1]
            close_val = close.iloc[-1]

            # Check conditions
            crossed = detect_crossover(histogram)
            ha_green = detect_ha_green(ha_open, ha_close)
            ha_color = "🟢 Green (bullish)" if ha_green else "🔴 Red (bearish)"
            macd_deep = macd_val < MACD_DEPTH_THRESH

            # EMA golden cross detection
            ema_crossed, ema_fast_val, ema_slow_val = detect_ema_golden_cross(
                close, EMA_FAST_LEN, EMA_SLOW_LEN
            )

            # 4-way confluence: crossover + MACD depth + HA green + VIX fear
            signal_fired = crossed and macd_deep and ha_green and vix_fear

            if verbose or signal_fired or ema_crossed:
                print(f"  Close: ${close_val:.2f}")
                print(f"  MACD: {macd_val:.4f} {'✅ deep' if macd_deep else '❌ shallow'}")
                print(f"  Signal: {signal_val:.4f}")
                print(f"  Histogram: {hist_val:.4f}")
                print(f"  MACD Crossover: {'YES 🟢' if crossed else 'NO'}")
                print(f"  Heikin Ashi: {ha_color}")
                print(f"  VIX: {vix_str} {'✅ fear' if vix_fear else '❌ calm'}")
                print(f"  EMA {EMA_FAST_LEN}/{EMA_SLOW_LEN}: {'🟢 CROSSED' if ema_crossed else '⚪ waiting'}")
                print(f"  Confluence: {'✅ FIRE' if signal_fired else '❌ NO'}")

            # Stage 1: Entry signal
            if signal_fired:
                last_alert = state.get(symbol, {}).get("last_alert", "")
                if last_alert == today and not force:
                    print(f"  ⏭️  Already alerted today, skipping")
                else:
                    msg = format_alert(symbol, macd_val, signal_val, hist_val, close_val, ha_color, vix_val)
                    if send_telegram_alert(token, chat_id, msg):
                        state[symbol] = {
                            "last_alert": today,
                            "macd": round(macd_val, 6),
                            "signal": round(signal_val, 6),
                            "histogram": round(hist_val, 6),
                            "close": round(close_val, 2),
                            "entry_date": today,
                            "entry_close": round(close_val, 2)
                        }
                        alerts_sent += 1

            # Stage 2: EMA golden cross confirmation
            entry_date = state.get(symbol, {}).get("entry_date", "")
            entry_close = state.get(symbol, {}).get("entry_close", 0)
            confirmed = state.get(symbol, {}).get("ema_confirmed", False)

            if ema_crossed and entry_date and not confirmed:
                # Check if within confirmation window
                days_since = (datetime.now(timezone(timedelta(hours=7))) -
                              datetime.strptime(entry_date, "%Y-%m-%d").replace(
                                  tzinfo=timezone(timedelta(hours=7)))).days
                if days_since <= CONFIRM_WINDOW:
                    msg = format_confirm_alert(
                        symbol, close_val, ema_fast_val, ema_slow_val,
                        entry_date, entry_close
                    )
                    if send_telegram_alert(token, chat_id, msg):
                        state[symbol]["ema_confirmed"] = True
                        state[symbol]["confirm_date"] = today
                        alerts_sent += 1
                        print(f"  ✅ EMA Golden Cross CONFIRMED (Stage 2)")
                else:
                    print(f"  ⏭️  EMA cross but entry was {days_since}d ago (>{CONFIRM_WINDOW}d window)")
            elif ema_crossed and not entry_date:
                print(f"  ⏭️  EMA cross but no entry signal yet")

            # Collect status
            status_lines.append(
                format_status(symbol, macd_val, signal_val, hist_val, close_val, crossed, ha_green, macd_deep)
            )

        except Exception as e:
            print(f"  ❌ Error: {e}")
            status_lines.append(f"*{symbol}*: ❌ Error — {e}")

    # Save state
    save_state(state)

    # Print summary
    print()
    print(f"📋 Summary: {alerts_sent} alert(s) sent")
    for line in status_lines:
        # Strip markdown for console
        clean = line.replace("*", "").replace("_", "")
        print(f"   {clean}")

    # If verbose, send status to Telegram too
    if verbose and status_lines:
        status_msg = f"📊 *MACD Monitor Status* — {today}\n\n" + "\n".join(status_lines)
        send_telegram_alert(token, chat_id, status_msg)

    return alerts_sent


if __name__ == "__main__":
    main()
