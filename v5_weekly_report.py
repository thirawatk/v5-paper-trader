#!/usr/bin/env python3
"""
V5 Weekly Paper Trader Report
==============================
Reads v5_paper_state.json, generates weekly report, saves .md, sends to Telegram.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

STATE_FILE = "/root/.hermes/profiles/trader/scripts/v5_paper_state.json"
STARTING_CAPITAL = 1000.0
REPORT_DIR = Path("/root/.hermes/profiles/trader/scripts")
REPORT_FILE = REPORT_DIR / "v5_weekly_report.md"

# Load bot token from .env
def load_env_token():
    env_path = Path("/root/.hermes/profiles/trader/.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                return line.split("=", 1)[1].strip()
    return None

TELEGRAM_BOT_TOKEN = load_env_token()
TELEGRAM_CHAT_ID = "2135517501"


def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        return json.load(f)


def generate_report():
    state = load_state()
    now = datetime.now()
    week = now.strftime("%Y-W%W")

    if not state:
        return f"⚠️ V5 Weekly Report — No state file found"

    capital = state.get("capital", STARTING_CAPITAL)
    peak = state.get("peak_capital", STARTING_CAPITAL)
    positions = state.get("positions", [])
    trades = state.get("closed_trades", [])
    last_run = state.get("last_run", "N/A")

    total_return = (capital - STARTING_CAPITAL) / STARTING_CAPITAL * 100
    dd = (peak - capital) / peak * 100 if peak > 0 else 0

    wins = [t for t in trades if t.get("r_multiple", 0) > 0]
    losses = [t for t in trades if t.get("r_multiple", 0) < 0]
    total_r = sum(t.get("r_multiple", 0) for t in trades)
    avg_r = total_r / len(trades) if trades else 0
    wr = len(wins) / len(trades) * 100 if trades else 0
    pf = (
        abs(sum(t["r_multiple"] for t in wins) / sum(t["r_multiple"] for t in losses))
        if losses
        else 99
    )

    unrealized = 0
    for p in positions:
        cur = p.get("current_price", p.get("entry_price", 0))
        entry = p.get("entry_price", 0)
        shares = p.get("shares", 0)
        unrealized += (cur - entry) * shares

    lines = [
        f"# 📊 V5 Weekly Report — {week}",
        f"",
        f"> Generated: {now.strftime('%Y-%m-%d %H:%M')}",
        f"> Strategy: 9-Factor Confluence (S&P 500 stocks)",
        f"> Config: 3% risk, 5 positions, TP2=1.5R",
        f"",
        f"---",
        f"",
        f"## Portfolio",
        f"",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Starting Capital | ${STARTING_CAPITAL:,.2f} |",
        f"| Current Capital | ${capital:,.2f} |",
        f"| Total Return | {total_return:+.2f}% |",
        f"| Peak Capital | ${peak:,.2f} |",
        f"| Drawdown | {dd:.1f}% |",
        f"| Unrealized P&L | ${unrealized:+,.2f} |",
        f"| Last Run | {last_run} |",
        f"",
    ]

    if positions:
        lines.extend([
            f"## Open Positions ({len(positions)})",
            f"",
            f"| Ticker | Entry | Current | P&L | SL | TP2 | Score | Days |",
            f"|---|---|---|---|---|---|---|---|",
        ])
        for p in positions:
            ticker = p.get("ticker", "?")
            entry = p.get("entry_price", 0)
            cur = p.get("current_price", entry)
            sl = p.get("sl", 0)
            tp2 = p.get("tp2", 0)
            shares = p.get("shares", 0)
            score = p.get("composite", p.get("score", 0))
            days = p.get("days_held", 0)
            pnl = (cur - entry) * shares
            pnl_pct = (cur - entry) / entry * 100 if entry > 0 else 0
            lines.append(
                f"| {ticker} | ${entry:.2f} | ${cur:.2f} | {pnl_pct:+.1f}% (${pnl:+.2f}) | ${sl:.2f} | ${tp2:.2f} | {score:.1f} | {days}d |"
            )
        lines.append("")
    else:
        lines.extend([f"## Open Positions", f"", f"✅ No open positions — fully flat.", f""])

    if trades:
        lines.extend([
            f"## Closed Trades ({len(trades)})",
            f"",
            f"| Ticker | Entry → Exit | Reason | R | P&L | Days |",
            f"|---|---|---|---|---|---|",
        ])
        for t in trades:
            ticker = t.get("ticker", "?")
            entry = t.get("entry_price", 0)
            exit_p = t.get("exit_price", 0)
            reason = t.get("exit_reason", "?")
            r = t.get("r_multiple", 0)
            pnl = t.get("pnl", t.get("risk", 0) * r)
            days = t.get("days_held", 0)
            emoji = "✅" if r > 0 else "❌"
            lines.append(
                f"| {ticker} | ${entry:.2f} → ${exit_p:.2f} | {emoji} {reason} | {r:+.2f}R | ${pnl:+.2f} | {days}d |"
            )

        lines.extend([
            f"",
            f"## Stats",
            f"",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Total Trades | {len(trades)} |",
            f"| Win Rate | {wr:.1f}% ({len(wins)}W / {len(losses)}L) |",
            f"| Avg R/Trade | {avg_r:+.3f}R |",
            f"| Total R | {total_r:+.2f}R |",
            f"| Profit Factor | {pf:.2f} |",
        ])
    else:
        lines.extend([f"## Closed Trades", f"", f"No trades closed yet.", f""])

    lines.extend([f"", f"---", f"*V5 Paper Trader — 9-Factor Confluence on S&P 500 stocks*"])
    return "\n".join(lines)


def send_telegram_document(filepath, caption=""):
    """Send a file to Telegram as a document."""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ No TELEGRAM_BOT_TOKEN found")
        return
    cmd = [
        "curl", "-s", "-X", "POST",
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
        "-F", f"chat_id={TELEGRAM_CHAT_ID}",
        "-F", f"document=@{filepath}",
        "-F", f"caption={caption}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if '"ok":true' in result.stdout:
        print(f"✅ Sent to Telegram: {filepath}")
    else:
        print(f"❌ Telegram error: {result.stdout[:200]}")


def main():
    report = generate_report()

    # Save .md file
    REPORT_FILE.write_text(report)
    print(f"Report saved: {REPORT_FILE}")

    # Send to Telegram
    send_telegram_document(str(REPORT_FILE), "📊 V5 Weekly Report")

    # Also print for no_agent stdout delivery
    print(report)


if __name__ == "__main__":
    main()
