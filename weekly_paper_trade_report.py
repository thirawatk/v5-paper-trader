#!/usr/bin/env python3
"""
Weekly Paper Trade Report — Live Data
=======================================
Reads the 24/7 live trader's state and generates a weekly performance summary.

Usage: python3 weekly_paper_trade_report.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

STATE_PATH = "/root/.hermes/profiles/trader/paper_trader_data/live_state.json"
OUTPUT_DIR = "/root/.hermes/profiles/trader/paper_trade_reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_live_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH) as f:
        return json.load(f)


def run_weekly_report() -> str:
    state = load_live_state()
    now = datetime.now(timezone.utc)
    week_label = now.strftime("%Y-W%W")

    # Determine coin count and per-coin capital early — used in header
    if not state:
        lines = [
            f"# 📊 Weekly Paper Trade Report — {week_label}",
            f"",
            f"> Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}",
            f"> Source: 24/7 Live Paper Trader (15-min polling)",
            f"> Strategy: 8-Factor Confluence V2 (Trend, VWAP, OBV, CMF, MFI, Funding, VP, Candle)",
            f"",
            f"---",
            f"",
            f"⚠️ No live trading data found yet. The 24/7 bot may not have run.",
        ]
        report = "\n".join(lines)
        save_report(report, week_label)
        return report

    equity = state.get("equity", 300.0)
    peak_equity = state.get("peak_equity", 300.0)
    starting_capital = state.get("starting_capital", 300.0)
    total_return = ((equity / starting_capital) - 1) * 100 if starting_capital > 0 else 0
    drawdown = (peak_equity - equity) / peak_equity * 100 if peak_equity > 0 else 0

    watchlist = state.get("watchlist", ["BTC", "HYPE"])
    n_coins = max(len(watchlist), 1)
    cap_per_coin = starting_capital / n_coins

    lines = [
        f"# 📊 Weekly Paper Trade Report — {week_label}",
        f"",
        f"> Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}",
        f"> Source: 24/7 Live Paper Trader (15-min polling)",
        f"> Strategy: 8-Factor Confluence V2 (Trend, VWAP, OBV, CMF, MFI, Funding, VP, Candle)",
        f"> Dynamic coin selection ({n_coins} coins, ${cap_per_coin:.2f}/coin) | Risk: 1% per trade",
        f"",
        f"---",
        f"",
    ]

    lines.extend([
        f"## Portfolio Overview",
        f"",
        f"- **Starting Capital:** ${starting_capital:.2f}",
        f"- **Current Equity:** ${equity:.2f}",
        f"- **Total Return:** {total_return:+.2f}%",
        f"- **Peak Equity:** ${peak_equity:.2f}",
        f"- **Current Drawdown:** {drawdown:.1f}%",
        f"- **Watchlist:** {', '.join(watchlist)} (${cap_per_coin:.2f}/coin)",
        f"- **Last Run:** {state.get('last_run', 'N/A')}",
        f"",
        f"---",
        f"",
    ])

    total_trades_all = 0
    total_wins = 0
    total_losses = 0
    total_pnl = 0.0
    open_count = 0

    for coin in watchlist:
        cs = state.get("coin_states", {}).get(coin, {})
        coin_equity = cs.get("equity", cap_per_coin)
        coin_peak = cs.get("peak_equity", cap_per_coin)
        coin_return = ((coin_equity / cap_per_coin) - 1) * 100
        coin_trades = state.get("trades", {}).get(coin, [])
        open_trades = cs.get("open_trades", [])
        open_count += len(open_trades)

        lines.extend([
            f"## {coin} Performance",
            f"",
            f"- **Current Equity:** ${coin_equity:.2f} ({coin_return:+.2f}%)",
            f"- **Peak Equity:** ${coin_peak:.2f}",
        ])

        if coin_trades:
            coin_pnl = sum(t.get("pnl", 0.0) for t in coin_trades)
            wins = len([t for t in coin_trades if t.get("pnl", 0) > 0])
            losses = len([t for t in coin_trades if t.get("pnl", 0) < 0])
            total_wins += wins
            total_losses += losses
            total_trades_all += len(coin_trades)
            total_pnl += coin_pnl

            r_values = [t.get("pnl_r", 0) for t in coin_trades if t.get("pnl_r", 0) != 0]
            avg_r = sum(r_values) / len(r_values) if r_values else 0
            total_r = sum(r_values)
            wr = (wins / len(coin_trades)) * 100 if coin_trades else 0

            lines.extend([
                f"- **Total Trades:** {len(coin_trades)} ({wins}W / {losses}L)",
                f"- **Win Rate:** {wr:.1f}%",
                f"- **Total PnL:** ${coin_pnl:+,.2f}",
                f"- **Total R:** {total_r:+.2f}R",
                f"- **Avg R per Trade:** {avg_r:+.3f}R",
            ])
        else:
            lines.append(f"- **No closed trades yet**")

        if open_trades:
            lines.append(f"- **Open Positions:** {len(open_trades)}")
            for t in open_trades:
                t_dir = t.get("direction", "?").upper()
                t_entry = t.get("entry_price", 0)
                t_stop = t.get("stop_loss", 0)
                t_score = t.get("confluence_score", 0)
                status = "TP1✓" if t.get("partial_closed") else "Active"
                lines.append(f"  - {t_dir} @ ${t_entry:,.2f} | Stop: ${t_stop:,.2f} | Score: {t_score:+.1f} | {status}")

        lines.append("")

    if total_trades_all > 0:
        overall_wr = (total_wins / total_trades_all) * 100
        lines.extend([
            f"## Combined Summary",
            f"",
            f"- **Total Trades:** {total_trades_all}",
            f"- **Wins / Losses:** {total_wins} / {total_losses}",
            f"- **Overall Win Rate:** {overall_wr:.1f}%",
            f"- **Combined PnL:** ${total_pnl:+,.2f}",
            f"- **ROI:** {total_return:+.2f}%",
            f"- **Max DD:** {drawdown:.1f}%",
            f"",
        ])
    else:
        lines.extend([
            f"## Combined Summary",
            f"",
            f"- **No trades closed yet across any coin.**",
            f"- **Bot is monitoring 24/7 — first signal triggers a notification.**",
            f"",
        ])

    if open_count > 0:
        lines.append(f"⚠️ **{open_count} open position(s)** — will carry into next week.")
    else:
        lines.append(f"✅ **No open positions** — fully flat.")

    lines.append(f"\n---\n")
    lines.append(f"*Report generated by Hermes Agent — 24/7 Paper Trader*")

    report = "\n".join(lines)
    save_report(report, week_label)
    return report


def save_report(report: str, week_label: str) -> None:
    report_path = os.path.join(OUTPUT_DIR, f"weekly_report_{week_label}.md")
    with open(report_path, "w") as f:
        f.write(report)
    latest_path = os.path.join(OUTPUT_DIR, "latest_report.md")
    with open(latest_path, "w") as f:
        f.write(report)
    print(f"Report saved: {report_path}")
    print(f"Latest: {latest_path}")


if __name__ == "__main__":
    report = run_weekly_report()
    print("\n" + report)
