#!/usr/bin/env python3
"""
Long-Term Entry Monitor — VOO/VXUS deep pullback alerts.
Checks daily at US close. Silent unless RSI <30 or -5%+ drawdown from peak.
"""
import json, urllib.request, sys, subprocess
from datetime import datetime, timezone, timedelta

BKK = timezone(timedelta(hours=7))
SCRIPTS_DIR = "/root/.hermes/profiles/trader/scripts"
REPORT_FILE = SCRIPTS_DIR + "/lt_entry_report.md"

def _load_tg_token():
    try:
        with open("/root/.hermes/profiles/trader/.env") as f:
            for line in f:
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def send_telegram_document(filepath, caption=""):
    """Send a file to Telegram as a document (same pattern as monitor_entries.py)."""
    token = _load_tg_token()
    if not token:
        print("⚠️ No TELEGRAM_BOT_TOKEN found — report file not sent")
        return False
    cmd = [
        "curl", "-s", "-X", "POST",
        f"https://api.telegram.org/bot{token}/sendDocument",
        "-F", "chat_id=2135517501",
        "-F", f"document=@{filepath}",
        "-F", f"caption={caption}",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        ok = '"ok":true' in r.stdout
        print(f"{'✅' if ok else '❌'} Report file {'sent' if ok else 'FAILED'}: {filepath}")
        return ok
    except Exception as e:
        print(f"❌ Telegram send error: {e}")
        return False

def write_and_send_report(now_str, blocks):
    """Write lt_entry_report.md, send as Telegram document, best-effort git push."""
    report = f"# 📊 Long-Term Entry Report — {now_str}\n\n" + "\n---\n\n".join(blocks) + "\n"
    try:
        with open(REPORT_FILE, "w") as f:
            f.write(report)
    except Exception as e:
        print(f"❌ Report write error: {e}")
        return
    send_telegram_document(REPORT_FILE, f"📊 Long-Term Entry Report — {now_str}")
    try:
        subprocess.run(["git", "add", "lt_entry_report.md"], cwd=SCRIPTS_DIR, capture_output=True, timeout=15)
        subprocess.run(["git", "commit", "-m", f"Long-Term entry report — {now_str}"], cwd=SCRIPTS_DIR, capture_output=True, timeout=15)
        subprocess.run(["git", "push"], cwd=SCRIPTS_DIR, capture_output=True, timeout=60)
    except Exception:
        pass

def fetch_yf(ticker, period="1y", interval="1d"):
    """Fetch OHLCV from Yahoo Finance v8."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={period}&interval={interval}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        result = data["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        highs = result["indicators"]["quote"][0]["high"]
        lows = result["indicators"]["quote"][0]["low"]
        timestamps = result["timestamp"]
        # Filter out None values
        valid = [(t, c, h, l) for t, c, h, l in zip(timestamps, closes, highs, lows) if c is not None]
        return valid
    except Exception as e:
        return []

def compute_rsi(closes, p=14):
    if len(closes) < p + 1:
        return 50
    gains = losses = 0.0
    for i in range(len(closes) - p, len(closes)):
        ch = closes[i] - closes[i - 1]
        gains += max(ch, 0)
        losses += abs(min(ch, 0))
    if losses == 0:
        return 100
    return 100 - 100 / (1 + gains / losses)

def ema(data, p):
    if len(data) < p:
        return data[-1] if data else 0
    m = 2 / (p + 1)
    r = sum(data[:p]) / p
    for v in data[p:]:
        r = (v - r) * m + r
    return r

def sma(data, p):
    if len(data) < p:
        return sum(data) / len(data) if data else 0
    return sum(data[-p:]) / p

report_blocks = []
for ticker in ["VOO", "VXUS"]:
    bars = fetch_yf(ticker, "1y", "1d")
    if not bars or len(bars) < 50:
        continue

    closes = [b[1] for b in bars]
    highs = [b[2] for b in bars]
    price = closes[-1]

    # Key levels
    rsi = compute_rsi(closes)
    e50 = ema(closes, 50)
    e200 = ema(closes, 200) if len(closes) >= 200 else e50
    s50 = sma(closes, 50)
    s100 = sma(closes, 100)

    # 52-week high/low
    high_52w = max(highs[-252:]) if len(highs) >= 252 else max(highs)
    drawdown = (price - high_52w) / high_52w * 100

    # ATR (14-day)
    atr_vals = []
    for i in range(max(1, len(bars) - 14), len(bars)):
        h, l, pc = bars[i][2], bars[i][3], bars[i - 1][1]
        atr_vals.append(max(h - l, abs(h - pc), abs(l - pc)))
    atr = sum(atr_vals) / len(atr_vals) if atr_vals else 1

    # Trend
    above50 = price > s50
    above200 = price > e200
    trend = "bullish" if above50 and above200 else "bearish" if not above50 and not above200 else "neutral"

    # Daily change
    chg = (price - closes[-2]) / closes[-2] * 100 if len(closes) > 1 else 0

    # Signal thresholds for long-term entries
    signals = []
    if rsi < 30:
        signals.append(f"RSI oversold ({rsi:.1f})")
    elif rsi < 35:
        signals.append(f"RSI approaching oversold ({rsi:.1f})")
    if drawdown < -5:
        signals.append(f"-{abs(drawdown):.1f}% from 52-week high")
    elif drawdown < -3:
        signals.append(f"{drawdown:.1f}% from 52-week high")
    if price < s50 and price > s100:
        signals.append(f"At SMA50 support (${s50:.2f})")
    if price < s100:
        signals.append(f"Below SMA100 (${s100:.2f}) — deep value zone")

    # Only output if there's a signal
    if signals:
        block = (
            f"## 📊 {ticker} Long-Term Entry Alert\n\n"
            f"Price: ${price:.2f} ({chg:+.2f}%) | RSI: {rsi:.1f} | Trend: {trend}\n\n"
            f"SMA50: ${s50:.2f} | SMA100: ${s100:.2f} | EMA200: ${e200:.2f}\n\n"
            f"52-week high: ${high_52w:.2f} | Drawdown: {drawdown:.1f}%\n\n"
            f"ATR: ${atr:.2f} ({atr/price*100:.1f}%)\n\n"
            f"🔔 Signals:\n" + "\n".join(f"  • {s}" for s in signals) + "\n\n"
            f"💡 Long-term DCA opportunity — consider adding at these levels"
        )
        report_blocks.append(block)
        print(f"📊 **{ticker} Long-Term Entry Alert**")
        print(f"Price: ${price:.2f} ({chg:+.2f}%) | RSI: {rsi:.1f} | Trend: {trend}")
        print(f"SMA50: ${s50:.2f} | SMA100: ${s100:.2f} | EMA200: ${e200:.2f}")
        print(f"52-week high: ${high_52w:.2f} | Drawdown: {drawdown:.1f}%")
        print(f"ATR: ${atr:.2f} ({atr/price*100:.1f}%)")
        print(f"\n🔔 Signals:")
        for s in signals:
            print(f"  • {s}")
        print(f"\n💡 Long-term DCA opportunity — consider adding at these levels")
        print()

# Write .md report + send as Telegram document + git push (only when signals fired)
if report_blocks:
    now_str = datetime.now(BKK).strftime("%a %d %b %Y %H:%M ICT")
    write_and_send_report(now_str, report_blocks)

# If no signals, output nothing (silent)
