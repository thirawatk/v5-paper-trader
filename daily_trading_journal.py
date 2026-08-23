#!/usr/bin/env python3
"""
Daily Trading Journal — Joplin Memory Palace
=============================================
Generates a daily journal entry from the live paper trader state
including full decision log (entries, exits, skips with reasons).

Usage: python3 daily_trading_journal.py
Output: Journal entry written to Joplin [System] Hermes Memory
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict

STATE_PATH = "/root/.hermes/profiles/trader/paper_trader_data/live_state.json"
JOPLIN_BIN = "/root/.hermes/node/bin/joplin"
NOTEBOOK = "This Week"  # Under Daily/This Week in Memory Palace

TZ_BKK = timezone(timedelta(hours=7))


def load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH) as f:
        return json.load(f)


def joplin_cmd(args: list[str]) -> str:
    env = os.environ.copy()
    env["PATH"] = f"/root/.hermes/node/bin:{env.get('PATH', '')}"
    result = subprocess.run(
        [JOPLIN_BIN] + args,
        capture_output=True, text=True, timeout=30, env=env
    )
    return result.stdout.strip()


def generate_journal(state: dict) -> tuple[str, str]:
    now = datetime.now(TZ_BKK)
    title = f"Trading Journal — {now.strftime('%Y-%m-%d')}"

    lines = [
        f"# 📊 {title}",
        f"",
        f"> Generated: {now.strftime('%Y-%m-%d %H:%M BKK')}",
        f"> Source: 24/7 Live Paper Trader",
        f"",
        f"---",
        f"",
    ]

    if not state or "coin_states" not in state:
        lines.append("⚠️ No trading data available today. Bot may not have run.")
        return title, "\n".join(lines)

    # Portfolio summary
    starting = state.get("starting_capital", 300)
    equity = state.get("equity", starting)
    peak = state.get("peak_equity", starting)
    pnl = equity - starting
    pnl_pct = (pnl / starting * 100) if starting else 0
    drawdown = ((equity - peak) / peak * 100) if peak else 0

    lines.extend([
        f"## Portfolio",
        f"- **Equity:** ${equity:.2f}",
        f"- **P&L:** ${pnl:+.2f} ({pnl_pct:+.1f}%)",
        f"- **Peak:** ${peak:.2f} | **Drawdown:** {drawdown:.1f}%",
        f"- **Starting:** ${starting:.2f}",
        f"",
    ])

    # Per-coin breakdown
    coin_states = state.get("coin_states", {})
    trades = state.get("trades", {})
    # Calculate per-coin allocated capital from state
    active_slots = 3  # ACTIVE_COIN_SLOTS
    per_slot_capital = starting / active_slots  # $100/slot when starting=$300

    lines.append("## Coins")
    for coin, cs in coin_states.items():
        open_trades = cs.get("open_trades", [])
        # Count actual closed trades for this coin (not cumulative counter)
        coin_closed = len(trades.get(coin, []))

        if open_trades:
            # Coin has open position — show entry details
            pos = open_trades[0]
            side = pos.get("direction", "?").upper()
            entry = pos.get("entry_price", 0)
            size = pos.get("position_size", 0)
            leverage = pos.get("leverage", 1)
            score = pos.get("confluence_score", 0)
            lines.append(
                f"- **{coin}:** {side} @ ${entry:.4f} "
                f"| Size: ${size:.2f} | Score: {score:+.1f} "
                f"| Trades: {coin_closed} | Open: {len(open_trades)}"
            )
        elif coin_closed > 0:
            # Coin has closed trades — show P&L from trades
            coin_pnl = sum(t.get("pnl", 0) for t in trades.get(coin, []))
            emoji = "🟢" if coin_pnl > 0 else "🔴" if coin_pnl < 0 else "⚪"
            lines.append(
                f"- **{coin}:** {emoji} P&L: ${coin_pnl:+.2f} "
                f"| Trades: {coin_closed} | Open: 0"
            )
        else:
            # Coin is watchlisted but no trades yet
            lines.append(
                f"- **{coin}:** Watchlisted | Allocated: ${per_slot_capital:.0f}/slot "
                f"| Trades: 0 | Open: 0"
            )
    lines.append("")

    # Open positions
    all_open = []
    for coin, cs in coin_states.items():
        for t in cs.get("open_trades", []):
            t["coin"] = coin
            all_open.append(t)

    if all_open:
        lines.append("## Open Positions")
        for pos in all_open:
            coin = pos.get("coin", "?")
            side = pos.get("direction", "?").upper()
            entry = pos.get("entry_price", 0)
            size = pos.get("position_size", 0)
            score = pos.get("confluence_score", 0)
            stop = pos.get("stop_loss", 0)
            entry_time = pos.get("entry_time", "N/A")
            emoji = "📈" if side == "LONG" else "📉" if side == "SHORT" else "❓"
            lines.append(
                f"- {emoji} **{coin}** {side} @ ${entry:.4f} "
                f"| Size: ${size:.2f} | Score: {score:+.1f} "
                f"| Stop: ${stop:.4f} | Opened: {entry_time}"
            )
        lines.append("")
    else:
        lines.extend(["## Open Positions", "_All flat_", ""])

    # ═══ DECISION LOG ═══
    decision_log = state.get("decision_log", [])

    if decision_log:
        # Filter to today only
        today_str = now.strftime("%Y-%m-%d")
        today_decisions = [d for d in decision_log if d.get("time", "").startswith(today_str)]

        if today_decisions:
            # Group by action type
            entries = [d for d in today_decisions if d.get("action") == "entry"]
            exits = [d for d in today_decisions if d.get("action") in ("exit", "partial_exit")]
            skips = [d for d in today_decisions if d.get("action") == "skip"]

            # ── ENTRIES ──
            if entries:
                lines.append("## ✅ Trades Entered (Why)")
                lines.append("")
                for e in entries:
                    coin = e.get("coin", "?")
                    direction = e.get("direction", "?").upper()
                    entry_price = e.get("entry_price", 0)
                    stop = e.get("stop_loss", 0)
                    tp1 = e.get("tp1", 0)
                    tp2 = e.get("tp2", 0)
                    score = e.get("score", 0)
                    breakdown = e.get("breakdown", "")
                    rr = e.get("rr_ratio", 0)
                    reason = e.get("reason", "")

                    lines.append(f"### {coin} {direction} @ ${entry_price:.2f}")
                    lines.append(f"- **Reason:** {reason}")
                    lines.append(f"- **Confluence Score:** {score:+.1f}/10")
                    lines.append(f"- **Factor Breakdown:** `{breakdown}`")
                    lines.append(f"- **R:R:** {rr:.2f}")
                    lines.append(f"- **Stop:** ${stop:.2f} | **TP1:** ${tp1:.2f} | **TP2:** ${tp2:.2f}")
                    lines.append("")

            # ── EXITS ──
            if exits:
                lines.append("## 🚪 Trades Exited (Why)")
                lines.append("")
                for e in exits:
                    coin = e.get("coin", "?")
                    exit_type = e.get("exit_type", "?")
                    reason = e.get("reason", "")
                    pnl_e = e.get("pnl", 0)
                    action = e.get("action", "exit")

                    emoji = "🟢" if pnl_e > 0 else "🔴" if pnl_e < 0 else "⚪"
                    label = "TP1 Partial" if action == "partial_exit" else exit_type.upper()

                    lines.append(f"### {coin} {label} — {emoji} ${pnl_e:+.2f}")
                    lines.append(f"- **Reason:** {reason}")
                    lines.append("")

            # ── SKIPS ──
            if skips:
                lines.append("## ⏭️ Trades Not Entered (Why)")
                lines.append("")
                lines.append("_Every 15 min, the bot checks 8 factors. Here's why it stayed flat:_")
                lines.append("")

                # Group skips by coin
                skips_by_coin = defaultdict(list)
                for s in skips:
                    skips_by_coin[s.get("coin", "?")].append(s)

                for coin, coin_skips in skips_by_coin.items():
                    lines.append(f"### {coin}")
                    # Summarize skip reasons with counts
                    reason_counts = defaultdict(int)
                    for s in coin_skips:
                        reason_text = s.get("reason", "unknown")
                        # Simplify reason for grouping
                        if "Score too low" in reason_text:
                            reason_counts["Score too low (confluence < 5)"] += 1
                        elif "No POC retest" in reason_text:
                            reason_counts["No POC retest (price not at value area)"] += 1
                        elif "Trend misalignment" in reason_text:
                            reason_counts["Trend misalignment (signal vs trend conflict)"] += 1
                        elif "Max open trades" in reason_text:
                            reason_counts["Max open trades reached (3/3)"] += 1
                        elif "R:R too low" in reason_text:
                            reason_counts["R:R ratio too low (< 1.5)"] += 1
                        elif "Confluence direction is none" in reason_text:
                            reason_counts["No clear direction (mixed signals)"] += 1
                        else:
                            reason_counts[reason_text] += 1

                    for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
                        lines.append(f"- {reason} × {count} checks")
                    lines.append("")

        else:
            lines.extend(["## Decisions Today", "_No decisions logged yet today. Bot may not have run._", ""])
    else:
        lines.extend(["## Decisions", "_Decision log is empty. Live trader may need the update deployed._", ""])

    # Recent trades (last 5 per coin)
    trades = state.get("trades", {})
    has_trades = False
    for coin, coin_trades in trades.items():
        if coin_trades:
            has_trades = True
            recent = list(coin_trades)[-5:]
            lines.append(f"## Recent {coin} Trades (Closed)")
            for t in reversed(recent):
                side = t.get("direction", "?").upper()
                entry = t.get("entry_price", 0)
                exit_p = t.get("exit_price", 0)
                pnl_t = t.get("pnl", 0)
                reason = t.get("exit_reason", "") or t.get("notes", "?")
                entry_time = t.get("entry_time", "N/A")[:16]
                exit_time = t.get("exit_time", "N/A")[:16]
                emoji = "🟢" if pnl_t > 0 else "🔴" if pnl_t < 0 else "⚪"
                lines.append(
                    f"- {entry_time} → {exit_time} | {side} "
                    f"${entry:.4f} → ${exit_p:.4f} | {emoji} ${pnl_t:+.2f} | {reason}"
                )
            lines.append("")

    if not has_trades:
        lines.extend(["## Recent Trades (Closed)", "_No completed trades yet_", ""])

    # Overall stats
    total_trades = sum(len(ct) for ct in trades.values())
    wins = sum(1 for ct in trades.values() for t in ct if t.get("pnl", 0) > 0)
    losses = total_trades - wins
    win_rate = (wins / total_trades * 100) if total_trades else 0

    lines.extend([
        f"## Stats",
        f"- Total trades: {total_trades}",
        f"- Wins: {wins} | Losses: {losses}",
        f"- Win rate: {win_rate:.0f}%",
        f"- Last run: {state.get('last_run', 'N/A')}",
        f"",
        f"---",
        f"_Auto-generated by Hermes Trader Profile — full decision log included_",
    ])

    return title, "\n".join(lines)


def write_to_joplin(title: str, body: str) -> bool:
    try:
        joplin_cmd(["use", NOTEBOOK])

        existing = joplin_cmd(["ls"])
        if title in existing:
            print(f"⚠️  Updating existing note: {title}")
            joplin_cmd(["set", title, "body", body])
        else:
            joplin_cmd(["mknote", title])
            joplin_cmd(["set", title, "body", body])

        joplin_cmd(["tag", "add", "trader", title])
        joplin_cmd(["tag", "add", "workflow", title])
        joplin_cmd(["sync"])
        print(f"✅ Written to Joplin: {title}")
        return True

    except Exception as e:
        print(f"❌ Joplin write failed: {e}")
        return False


def main():
    state = load_state()
    title, body = generate_journal(state)

    # Save locally too
    output_dir = "/root/.hermes/profiles/trader/paper_trade_reports"
    os.makedirs(output_dir, exist_ok=True)
    local_path = os.path.join(output_dir, f"journal_{datetime.now(TZ_BKK).strftime('%Y%m%d')}.md")
    with open(local_path, "w") as f:
        f.write(body)
    print(f"📄 Saved locally: {local_path}")

    # Write to Joplin
    success = write_to_joplin(title, body)

    if success:
        print(f"\n📊 Daily Journal: {title}")
        equity = state.get("equity", 300)
        starting = state.get("starting_capital", 300)
        pnl = equity - starting
        coin_states = state.get("coin_states", {})
        total_trades = sum(cs.get("trade_counter", 0) for cs in coin_states.values())
        decision_log = state.get("decision_log", [])
        print(f"Equity: ${equity:.2f} | P&L: ${pnl:+.2f}")
        print(f"Coins: {', '.join(coin_states.keys())} | Total trades: {total_trades}")
        print(f"Decision log entries: {len(decision_log)}")


if __name__ == "__main__":
    main()
