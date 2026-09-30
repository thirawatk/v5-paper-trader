#!/usr/bin/env python3
"""
US Stocks 2-Stage Monitor — Production Script
==============================================
Stage 1: MACD cross + depth + HA green + VIX >= 20
Stage 2: EMA 50 golden cross within 30 days

Smart execution: VIX check first. If VIX < 20, skip stock scan entirely.
Universe: S&P 500 + NASDAQ 100 + key mid-caps (~600 stocks)
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import subprocess
from datetime import datetime, timezone, timedelta

# ── Config ──
FAST_LENGTH = 12
SLOW_LENGTH = 26
SIGNAL_LENGTH = 9
MACD_DEPTH_THRESH = -0.5
VIX_FEAR_THRESH = 20.0
EMA_FAST_LEN = 50
EMA_SLOW_LEN = 200
CONFIRM_WINDOW = 30

STATE_FILE = "/root/.hermes/profiles/trader/scripts/us_stocks_monitor_state.json"
ENV_FILE = "/root/.hermes/profiles/trader/.env"
UNIVERSE_FILE = "/root/.hermes/profiles/trader/scripts/us_stocks_universe.txt"


def load_env():
    token = None
    chat_id = None
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line.startswith("TELEGRAM") and "BOT_TOKEN" in line and "=" in line:
                    token = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("TELEGRAM_HOME_CHANNEL="):
                    chat_id = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not chat_id:
        chat_id = "-5195094488"
    return token, chat_id


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def send_telegram(token, chat_id, message):
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
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        return result.get("ok", False)
    except Exception as e:
        print(f"  Telegram error: {e}")
        return False


def fetch_vix():
    import yfinance as yf
    vix = yf.Ticker("^VIX")
    hist = vix.history(period="5d")
    if hist.empty:
        return None
    return hist["Close"].iloc[-1]


def get_universe():
    """Load stock universe from file or build it."""
    if os.path.exists(UNIVERSE_FILE):
        with open(UNIVERSE_FILE) as f:
            tickers = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        if tickers:
            return tickers

    # Build universe from Wikipedia
    tickers = set()

    # S&P 500
    try:
        sp = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        tickers.update(sp["Symbol"].tolist())
    except:
        pass

    # NASDAQ 100
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
        for table in tables:
            for col in table.columns:
                if 'ticker' in str(col).lower() or 'symbol' in str(col).lower():
                    vals = table[col].dropna().tolist()
                    if len(vals) > 50:
                        tickers.update(vals)
    except:
        pass

    # Clean
    cleaned = set()
    for t in tickers:
        t = str(t).strip().upper().replace(".", "-")
        if t and len(t) <= 6 and not t.startswith("^"):
            cleaned.add(t)

    # Save for next run
    sorted_tickers = sorted(cleaned)
    with open(UNIVERSE_FILE, "w") as f:
        f.write("# US Stocks Universe (S&P 500 + NASDAQ 100)\n")
        f.write(f"# Updated: {datetime.now().strftime('%Y-%m-%d')}\n")
        for t in sorted_tickers:
            f.write(t + "\n")

    return sorted_tickers


def batch_download(tickers, period="1y", batch_size=50):
    """Download stock data in batches using yfinance."""
    import yfinance as yf
    import pandas as pd

    all_data = {}
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        try:
            data = yf.download(
                batch, period=period, group_by="ticker",
                progress=False, threads=True
            )
            if len(batch) == 1:
                sym = batch[0]
                if not data.empty:
                    all_data[sym] = data
            else:
                for sym in batch:
                    try:
                        df = data[sym].dropna(how="all")
                        if not df.empty and len(df) > 50:
                            all_data[sym] = df
                    except:
                        pass
        except Exception as e:
            print(f"  Batch error ({batch[0]}-{batch[-1]}): {e}")
    return all_data


def check_stock(df, vix_val, state, symbol, today, force=False, report_mode=False):
    """Check a single stock for 2-stage signals. Returns (stage1, stage2, status_msg)."""
    import pandas as pd

    if df.empty or len(df) < 200:
        return None, None, None

    close = df["Close"]
    if len(close) < 200:
        return None, None, None

    # MACD
    ema_f = close.ewm(span=FAST_LENGTH, adjust=False).mean()
    ema_s = close.ewm(span=SLOW_LENGTH, adjust=False).mean()
    macd_line = ema_f - ema_s
    signal_line = macd_line.rolling(window=SIGNAL_LENGTH).mean()
    hist = macd_line - signal_line

    # Heikin Ashi
    ha_close = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4
    ha_open = df["Open"].copy()
    ha_open.iloc[0] = (df["Open"].iloc[0] + df["Close"].iloc[0]) / 2
    for i in range(1, len(ha_open)):
        ha_open.iloc[i] = (ha_open.iloc[i - 1] + ha_close.iloc[i - 1]) / 2

    # EMA 50/200
    ema_50 = close.ewm(span=EMA_FAST_LEN, adjust=False).mean()
    ema_200 = close.ewm(span=EMA_SLOW_LEN, adjust=False).mean()

    # Latest values
    macd_val = macd_line.iloc[-1]
    hist_val = hist.iloc[-1]
    close_val = close.iloc[-1]
    ha_green = ha_close.iloc[-1] > ha_open.iloc[-1]
    macd_deep = macd_val < MACD_DEPTH_THRESH

    # Stage 1: 4-way confluence
    crossed = hist.iloc[-2] < 0 and hist.iloc[-1] >= 0
    # report_mode (weekly --weekly-report): VIX gate waived for visibility only;
    # production alerts still require VIX >= 20.
    vix_ok = vix_val >= VIX_FEAR_THRESH if not report_mode else True
    stage1 = crossed and macd_deep and ha_green and vix_ok

    stage1_result = None
    stage2_result = None

    if stage1:
        last_alert = state.get(symbol, {}).get("last_alert", "")
        if last_alert == today and not force:
            pass  # already alerted
        else:
            stage1_result = {
                "symbol": symbol,
                "close": round(float(close_val), 2),
                "macd": round(float(macd_val), 4),
                "signal": round(float(signal_line.iloc[-1]), 4),
                "hist": round(float(hist_val), 4),
                "vix": round(float(vix_val), 1),
            }

    # Stage 2: EMA golden cross (check if any entry signal pending)
    entry_date = state.get(symbol, {}).get("entry_date", "")
    confirmed = state.get(symbol, {}).get("ema_confirmed", False)

    if entry_date and not confirmed:
        ema_crossed = (ema_50.iloc[-1] > ema_200.iloc[-1] and
                       ema_50.iloc[-2] <= ema_200.iloc[-2])
        if ema_crossed:
            days_since = (datetime.now(timezone(timedelta(hours=7))) -
                          datetime.strptime(entry_date, "%Y-%m-%d").replace(
                              tzinfo=timezone(timedelta(hours=7)))).days
            if days_since <= CONFIRM_WINDOW:
                stage2_result = {
                    "symbol": symbol,
                    "close": round(float(close_val), 2),
                    "ema50": round(float(ema_50.iloc[-1]), 2),
                    "ema200": round(float(ema_200.iloc[-1]), 2),
                    "entry_date": entry_date,
                    "entry_close": state.get(symbol, {}).get("entry_close", 0),
                    "days_since": days_since,
                }

    return stage1_result, stage2_result, None


def format_stage1_alert(sig):
    now = datetime.now(timezone(timedelta(hours=7)))
    return (
        f"🔔 *US Stock Alert — Entry Signal*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"*Stock:* {sig['symbol']}\n"
        f"*Stage:* 1️⃣ Entry\n"
        f"*Close:* ${sig['close']:.2f}\n"
        f"*MACD:* {sig['macd']:.4f}\n"
        f"*VIX:* {sig['vix']:.1f}\n"
        f"*Next:* Watching for EMA 50/200 golden cross\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"_{now.strftime('%Y-%m-%d %H:%M BKK')}_"
    )


def format_stage1_summary(alerts, vix_val, universe_name, stocks_scanned):
    now = datetime.now(timezone(timedelta(hours=7)))
    lines = [
        f"🔔 *2-Stage Confluence — Entry Signals*\n",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"*Universe:* {universe_name}",
        f"*Stocks scanned:* {stocks_scanned}",
        f"*VIX:* {vix_val:.1f}",
        f"*Signals found:* {len(alerts)}\n",
    ]
    for sig in sorted(alerts, key=lambda x: x["symbol"]):
        lines.append(f"• *{sig['symbol']}* — ${sig['close']:.2f} | MACD={sig['macd']:.4f}")
    lines.append(f"\n*Stage 2:* Watching for EMA 50/200 golden cross (30d)")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"_{now.strftime('%Y-%m-%d %H:%M BKK')}_")
    return "\n".join(lines)


def send_telegram_document(token, chat_id, file_path, caption=""):
    """Send a file via Telegram Bot API."""
    import subprocess
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.telegram.org/bot{token}/sendDocument",
        "-F", f"chat_id={chat_id}",
        "-F", f"document=@{file_path}",
        "-F", f"caption={caption}"
    ], capture_output=True, text=True)
    try:
        r = json.loads(result.stdout)
        return r.get("ok", False)
    except:
        return False


def format_stage2_alert(sig):
    now = datetime.now(timezone(timedelta(hours=7)))
    entry_close = sig.get("entry_close", 0)
    pct = ((sig["close"] - entry_close) / entry_close * 100) if entry_close else 0
    return (
        f"✅ *US Stock Alert — Trend Confirmed*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"*Stock:* {sig['symbol']}\n"
        f"*Stage:* 2️⃣ Confirmed\n"
        f"*Close:* ${sig['close']:.2f} ({pct:+.1f}% from entry)\n"
        f"*EMA 50:* ${sig['ema50']:.2f}\n"
        f"*EMA 200:* ${sig['ema200']:.2f}\n"
        f"*Entry:* {sig['entry_date']} @ ${entry_close:.2f}\n"
        f"*Days:* {sig['days_since']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"_{now.strftime('%Y-%m-%d %H:%M BKK')}_"
    )


def main():
    global STATE_FILE, UNIVERSE_FILE

    force = "--force" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    # Weekly visibility report: VIX gate waived, NO state writes, NO alerts sent.
    # Shows would-be Stage 1 signals regardless of market regime.
    report_mode = "--weekly-report" in sys.argv

    # Allow --universe flag to override stock list
    for arg in sys.argv:
        if arg.startswith("--universe="):
            UNIVERSE_FILE = arg.split("=", 1)[1]
            STATE_FILE = UNIVERSE_FILE.replace("_universe.txt", "_monitor_state.json")

    token, chat_id = load_env()
    if not token:
        print("❌ No TELEGRAM_BOT_TOKEN")
        sys.exit(1)

    state = load_state()
    today = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d")

    print(f"📊 US Stocks 2-Stage Monitor — {today}")
    print(f"   Universe: {os.path.basename(UNIVERSE_FILE)}")

    # Step 1: VIX check
    print("  Checking VIX...")
    vix_val = fetch_vix()
    vix_str = f"{vix_val:.1f}" if vix_val else "N/A"
    print(f"  VIX: {vix_str}")

    if vix_val is not None and vix_val < VIX_FEAR_THRESH and not force and not report_mode:
        print(f"  VIX < {VIX_FEAR_THRESH} — calm market. Skipping scan.")
        print(f"  (Use --force to override)")
        save_state(state)
        return 0

    # Step 2: Load universe
    mode_label = "WEEKLY REPORT MODE (VIX gate waived, no alerts)" if report_mode else f"FEAR mode!"
    print(f"  {mode_label} Loading universe...")
    tickers = get_universe()
    print(f"  Universe: {len(tickers)} stocks")

    # Step 3: Download data
    print(f"  Downloading data (this may take a few minutes)...")
    all_data = batch_download(tickers, period="1y")
    print(f"  Downloaded: {len(all_data)} stocks")

    # Step 4: Check each stock
    stage1_alerts = []
    stage2_alerts = []

    for sym, df in all_data.items():
        try:
            s1, s2, _ = check_stock(df, vix_val, state, sym, today, force, report_mode)
            if s1:
                stage1_alerts.append(s1)
            if s2:
                stage2_alerts.append(s2)
        except Exception as e:
            if verbose:
                print(f"  {sym}: error — {e}")

    # Step 5: Send alerts
    alerts_sent = 0
    universe_name = os.path.basename(UNIVERSE_FILE).replace("_universe.txt", "").upper()

    # Stage 1: Summary message + CSV
    if stage1_alerts:
        # Send summary message (report_mode: stdout only — no Telegram, no state)
        summary = format_stage1_summary(stage1_alerts, vix_val, universe_name, len(all_data))
        if report_mode:
            print(summary)
            print(f"\n  [WEEKLY REPORT] {len(stage1_alerts)} would-be Stage 1 signals (VIX {vix_val:.1f} < {VIX_FEAR_THRESH} — production gate blocked these)")
            return 0
        send_telegram(token, chat_id, summary)

        # Generate CSV
        csv_path = UNIVERSE_FILE.replace("_universe.txt", f"_stage1_{today}.csv")
        import csv as csv_mod
        with open(csv_path, "w", newline="") as f:
            writer = csv_mod.DictWriter(f, fieldnames=["symbol", "close", "macd", "signal", "hist", "vix"])
            writer.writeheader()
            writer.writerows(stage1_alerts)

        # Send CSV
        caption = f"Stage 1 Signals - {universe_name} - {today} - {len(stage1_alerts)} stocks"
        send_telegram_document(token, chat_id, csv_path, caption)

        # Update state
        for sig in stage1_alerts:
            state[sig["symbol"]] = {
                "last_alert": today,
                "entry_date": today,
                "entry_close": sig["close"],
                "ema_confirmed": False
            }
            print(f"  🔔 Stage 1: {sig['symbol']} ${sig['close']:.2f}")

        alerts_sent += len(stage1_alerts)

        # Clean up temp CSV
        try:
            os.remove(csv_path)
        except:
            pass

    # Stage 2: Individual alerts
    for sig in stage2_alerts:
        msg = format_stage2_alert(sig)
        if send_telegram(token, chat_id, msg):
            state[sig["symbol"]]["ema_confirmed"] = True
            state[sig["symbol"]]["confirm_date"] = today
            alerts_sent += 1
            print(f"  ✅ Stage 2: {sig['symbol']} ${sig['close']:.2f}")

    save_state(state)

    # Summary
    print(f"\n📋 Summary:")
    print(f"  VIX: {vix_str}")
    print(f"  Stocks scanned: {len(all_data)}")
    print(f"  Stage 1 alerts: {len(stage1_alerts)}")
    print(f"  Stage 2 alerts: {len(stage2_alerts)}")
    print(f"  Total sent: {alerts_sent}")

    return alerts_sent


if __name__ == "__main__":
    main()
