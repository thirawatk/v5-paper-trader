#!/usr/bin/env python3
"""
Trading Journal Prometheus Exporter — V5 Paper Trader (S&P 500)
================================================================
Exposes V5 paper trader state as Prometheus metrics.
Runs on port 9102.

Data source: v5_paper_state.json (NOT the Hyperliquid perps state)

Metrics:
  trading_total_equity          - Total portfolio value (capital + positions)
  trading_total_peak_equity     - Peak capital
  trading_total_trades          - Total closed trade count
  trading_open_positions        - Number of open positions
  trading_starting_capital      - Starting capital ($1000)
  trading_equity{coin}          - Position value per ticker (coin=ticker)
  trading_watchlist{coin}       - 1 if position is open (for dashboard compat)
  trading_position_*            - Per-position detail metrics
  trading_closed_trade_pnl      - PnL of each closed trade
  trading_weekly_*              - Weekly aggregate metrics
  trading_daily_*               - Daily metrics derived from closed trades
"""

import json
import os
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from prometheus_client import (
    Gauge, Counter, Info, generate_latest, REGISTRY
)

# ── Paths ──
STATE_PATH = "/root/.hermes/profiles/trader/scripts/v5_paper_state.json"
TRADES_CSV = "/root/.hermes/profiles/trader/scripts/v5_paper_trades.csv"
EXPORTER_PORT = 9102
STARTING_CAPITAL = 1000.0

# ── Prometheus metrics ──
EQUITY = Gauge("trading_equity", "Position value per ticker", ["coin"])
PEAK_EQUITY = Gauge("trading_peak_equity", "Peak equity per coin", ["coin"])
TRADE_COUNTER = Gauge("trading_trade_counter", "Number of trades per coin", ["coin"])
STARTING_CAPITAL_GAUGE = Gauge("trading_starting_capital", "Starting capital")
TOTAL_EQUITY = Gauge("trading_total_equity", "Total portfolio value")
TOTAL_PEAK_EQUITY = Gauge("trading_total_peak_equity", "Total peak capital")
TOTAL_TRADES = Gauge("trading_total_trades", "Total closed trade count")
WATCHLIST = Gauge("trading_watchlist", "1 if ticker has open position", ["coin"])
LAST_RUN = Gauge("trading_last_run_timestamp", "Unix timestamp of last run")
DECISION_LOG_TOTAL = Gauge("trading_decision_log_total", "Total decision log entries (N/A for V5)")
OPEN_POSITIONS = Gauge("trading_open_positions", "Number of open positions")
JOURNAL_ENTRIES = Gauge("trading_journal_entries", "Number of closed trades (acts as journal)")

# Weekly report metrics
WEEKLY_PNL = Gauge("trading_weekly_pnl", "Total P&L", ["week"])
WEEKLY_TRADES = Gauge("trading_weekly_trades", "Total trade count", ["week"])
WEEKLY_WIN_RATE = Gauge("trading_weekly_win_rate", "Win rate", ["week"])

# Position detail metrics (for Open Positions table panel)
POSITION_ENTRY_PRICE = Gauge("trading_position_entry_price", "Entry price", ["coin", "direction"])
POSITION_STOP_LOSS = Gauge("trading_position_stop_loss", "Stop loss price", ["coin", "direction"])
POSITION_TP1 = Gauge("trading_position_tp1", "Take profit 1", ["coin", "direction"])
POSITION_TP2 = Gauge("trading_position_tp2", "Take profit 2", ["coin", "direction"])
POSITION_SCORE = Gauge("trading_position_score", "Confluence score", ["coin", "direction"])
POSITION_RISK = Gauge("trading_position_risk_amount", "Risk amount", ["coin", "direction"])
POSITION_SIZE = Gauge("trading_position_size", "Position size (shares)", ["coin", "direction"])
POSITION_PNL = Gauge("trading_position_pnl", "Realized P&L", ["coin", "direction"])
POSITION_HOURS_OPEN = Gauge("trading_position_hours_open", "Hours since entry", ["coin", "direction"])
POSITION_CURRENT_PRICE = Gauge("trading_position_current_price", "Current price", ["coin", "direction"])
POSITION_UNREALIZED_PNL = Gauge("trading_position_unrealized_pnl", "Unrealized PnL", ["coin", "direction"])

# Historical trade metrics
CLOSED_TRADE_PNL = Gauge("trading_closed_trade_pnl", "PnL of closed trade", ["coin", "exit_type", "direction", "reason", "trade_id"])
CLOSED_TRADE_COUNT = Gauge("trading_closed_trades_total", "Total closed trades")

# Daily metrics (derived from closed trades by entry_date)
DAILY_EQUITY = Gauge("trading_daily_equity", "Daily equity snapshot", ["date"])
DAILY_PNL = Gauge("trading_daily_pnl", "Daily P&L", ["date"])
DAILY_TRADES = Gauge("trading_daily_trades", "Trades opened that day", ["date"])
DAILY_DRAWDOWN = Gauge("trading_daily_drawdown", "Daily drawdown %", ["date"])
DAILY_PEAK = Gauge("trading_daily_peak", "Daily peak equity", ["date"])
DAILY_TRADE_COUNT = Gauge("trading_daily_trade_count", "Total trades executed", ["date"])


def load_state():
    """Load the V5 paper trader state."""
    if not os.path.exists(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def clear_stale_labels(gauge, label_name):
    """Remove label values no longer in the live state."""
    stale = list(gauge._metrics.keys())
    for lv in stale:
        try:
            gauge.remove(*lv)
        except KeyError:
            pass


def update_metrics():
    """Update all Prometheus metrics from the V5 paper trader state."""
    state = load_state()
    if not state:
        return

    # ── Clear all stale labels first ──
    for gauge in [EQUITY, PEAK_EQUITY, TRADE_COUNTER, WATCHLIST,
                  WEEKLY_PNL, WEEKLY_TRADES, WEEKLY_WIN_RATE,
                  POSITION_ENTRY_PRICE, POSITION_STOP_LOSS, POSITION_TP1,
                  POSITION_TP2, POSITION_SCORE, POSITION_RISK, POSITION_SIZE,
                  POSITION_PNL, POSITION_HOURS_OPEN, POSITION_CURRENT_PRICE,
                  POSITION_UNREALIZED_PNL, CLOSED_TRADE_PNL,
                  DAILY_EQUITY, DAILY_PNL, DAILY_TRADES, DAILY_DRAWDOWN,
                  DAILY_PEAK, DAILY_TRADE_COUNT]:
        clear_stale_labels(gauge, None)

    # ── Starting capital ──
    STARTING_CAPITAL_GAUGE.set(STARTING_CAPITAL)

    # ── Portfolio-level equity ──
    capital = state.get("capital", 0)
    peak = state.get("peak_capital", 0)

    # Total value = cash + sum of capital_risked per position
    # capital_risked is the actual capital allocated (not full market value)
    positions = state.get("positions", [])
    position_value = sum(p.get("capital_risked", 0) for p in positions)
    total_value = capital + position_value

    TOTAL_EQUITY.set(total_value)
    TOTAL_PEAK_EQUITY.set(peak)

    # ── Open positions ──
    open_count = len(positions)
    OPEN_POSITIONS.set(open_count)

    # ── Per-ticker metrics for open positions ──
    # In V5, "equity" per ticker = market value of position
    # We use "long" as direction since V5 trades stocks (always long)
    seen_tickers = set()
    for pos in positions:
        ticker = pos.get("ticker", "UNK")
        seen_tickers.add(ticker)
        shares = pos.get("shares", 0)
        entry = pos.get("entry_price", 0)
        current = pos.get("current_price", entry)
        sl = pos.get("sl", 0)
        tp1 = pos.get("tp1", 0)
        tp2 = pos.get("tp2", 0)
        score = pos.get("composite", 0)
        risk = pos.get("capital_risked", 0)
        days = pos.get("days_held", 0)

        # Capital allocated to this position (not full market value)
        risk = pos.get("capital_risked", 0)
        mkt_value = risk
        EQUITY.labels(coin=ticker).set(mkt_value)
        PEAK_EQUITY.labels(coin=ticker).set(mkt_value)
        TRADE_COUNTER.labels(coin=ticker).set(0)  # Open = not yet closed
        WATCHLIST.labels(coin=ticker).set(1)

        # Position detail metrics
        direction = "long"
        POSITION_ENTRY_PRICE.labels(coin=ticker, direction=direction).set(entry)
        POSITION_STOP_LOSS.labels(coin=ticker, direction=direction).set(sl)
        POSITION_TP1.labels(coin=ticker, direction=direction).set(tp1)
        POSITION_TP2.labels(coin=ticker, direction=direction).set(tp2)
        POSITION_SCORE.labels(coin=ticker, direction=direction).set(score)
        POSITION_RISK.labels(coin=ticker, direction=direction).set(risk)
        POSITION_SIZE.labels(coin=ticker, direction=direction).set(shares)
        POSITION_PNL.labels(coin=ticker, direction=direction).set(0)  # Realized = 0 for open

        # Hours open (from days_held)
        hours = days * 24
        POSITION_HOURS_OPEN.labels(coin=ticker, direction=direction).set(round(hours, 1))
        POSITION_CURRENT_PRICE.labels(coin=ticker, direction=direction).set(current)

        # Unrealized P&L
        if current > 0 and entry > 0:
            unrealized = (current - entry) * shares
            POSITION_UNREALIZED_PNL.labels(coin=ticker, direction=direction).set(round(unrealized, 2))

    # ── Closed trades ──
    closed_trades = state.get("closed_trades", [])
    total_trades = len(closed_trades)
    TOTAL_TRADES.set(total_trades)
    JOURNAL_ENTRIES.set(total_trades)  # Use as journal count for dashboard compat

    # Derive win/loss stats from closed trades
    total_wins = 0
    total_losses = 0
    total_pnl = 0.0
    for trade in closed_trades:
        pnl = trade.get("pnl", 0)
        total_pnl += pnl
        if pnl > 0:
            total_wins += 1
        elif pnl < 0:
            total_losses += 1

    closed_count = total_wins + total_losses

    # Win rate metric (for dashboard stat panel)
    if closed_count > 0:
        WEEKLY_WIN_RATE.labels(week="current").set(round(total_wins / closed_count * 100, 1))
        WEEKLY_PNL.labels(week="current").set(round(total_pnl, 2))
        WEEKLY_TRADES.labels(week="current").set(closed_count)
    else:
        WEEKLY_WIN_RATE.labels(week="current").set(0)
        WEEKLY_PNL.labels(week="current").set(0)
        WEEKLY_TRADES.labels(week="current").set(0)

    # ── Closed trade PnL metrics (for Trade History table) ──
    for i, trade in enumerate(closed_trades):
        ticker = trade.get("ticker", "UNK")
        exit_reason = trade.get("exit_reason", "unknown")
        pnl = trade.get("pnl", 0)
        entry_date = trade.get("entry_date", "")
        exit_date = trade.get("exit_date", "")
        entry_price = trade.get("entry_price", 0)
        r_mult = trade.get("r_multiple", 0)
        days = trade.get("days_held", 0)

        reason = f"{exit_reason} | R:{r_mult:+.2f} | {days}d"
        if entry_date:
            reason += f" | {entry_date}→{exit_date}"
        reason = reason[:200]

        tid = f"v5_{ticker}_{i}"
        # V5 stocks = always "long" direction
        CLOSED_TRADE_PNL.labels(
            coin=ticker, exit_type=exit_reason, direction="long",
            reason=reason, trade_id=tid
        ).set(round(pnl, 2))

    CLOSED_TRADE_COUNT.set(total_trades)

    # ── Daily metrics from closed trades ──
    # Group trades by entry_date to build daily snapshots
    daily_data = {}
    for trade in closed_trades:
        entry_date = trade.get("entry_date", "")
        if not entry_date:
            continue
        if entry_date not in daily_data:
            daily_data[entry_date] = {"pnl": 0, "trades_opened": 0, "peak": total_value}
        daily_data[entry_date]["trades_opened"] += 1

    # Also add exit dates
    running_pnl = 0.0
    for trade in sorted(closed_trades, key=lambda t: t.get("exit_date", "")):
        exit_date = trade.get("exit_date", "")
        if not exit_date:
            continue
        pnl = trade.get("pnl", 0)
        running_pnl += pnl
        if exit_date not in daily_data:
            daily_data[exit_date] = {"pnl": 0, "trades_opened": 0, "peak": total_value}
        daily_data[exit_date]["pnl"] += pnl

    for date, dd in sorted(daily_data.items()):
        if dd["trades_opened"] > 0:
            DAILY_TRADES.labels(date=date).set(dd["trades_opened"])
        if dd["pnl"] != 0:
            DAILY_PNL.labels(date=date).set(round(dd["pnl"], 2))
        # Approximate equity from running PnL
        approx_eq = STARTING_CAPITAL + running_pnl
        DAILY_EQUITY.labels(date=date).set(round(approx_eq, 2))
        DAILY_PEAK.labels(date=date).set(round(max(peak, approx_eq), 2))
        # Drawdown
        if peak > 0:
            dd_pct = max(0, (peak - approx_eq) / peak * 100)
            DAILY_DRAWDOWN.labels(date=date).set(round(dd_pct, 2))

    # ── Last run timestamp ──
    last_run = state.get("last_run", "")
    if last_run:
        try:
            # V5 uses ISO format: 2026-09-11T12:02:01.045624
            dt = datetime.fromisoformat(last_run)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            LAST_RUN.set(dt.timestamp())
        except (ValueError, TypeError):
            LAST_RUN.set(0)

    # Decision log N/A for V5
    DECISION_LOG_TOTAL.set(0)


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint."""

    def do_GET(self):
        if self.path == "/metrics":
            try:
                update_metrics()
                output = generate_latest(REGISTRY)
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4")
                self.end_headers()
                self.wfile.write(output)
            except Exception as e:
                import traceback
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(traceback.format_exc().encode())
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = """<html><head><title>V5 Trading Exporter</title></head>
<body><h1>📊 V5 Paper Trader Prometheus Exporter</h1>
<p>Metrics available at <a href="/metrics">/metrics</a></p>
<p>Data source: v5_paper_state.json</p>
<p>Port: {}</p></body></html>""".format(EXPORTER_PORT)
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress request logging


def main():
    server = HTTPServer(("0.0.0.0", EXPORTER_PORT), MetricsHandler)
    print(f"V5 Trading Journal Prometheus Exporter running on port {EXPORTER_PORT}")
    print(f"State: {STATE_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
