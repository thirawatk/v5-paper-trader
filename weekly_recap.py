#!/usr/bin/env python3
"""
Weekly Recap — Sunday combined digest.
Sections: market scan setups (last 7d), paper traders (V5/Journey/crypto POC),
real account (stocks + crypto journals), open positions with live prices.
Watchdog: prints recap to stdout; cron delivers verbatim.
"""
import json, glob, os, sys, re
from datetime import datetime, timezone, timedelta

BKK = timezone(timedelta(hours=7))
NOW = datetime.now(BKK)
WEEK_AGO = NOW - timedelta(days=7)

BASE = "/root/.hermes/profiles/trader"
SCAN_DIR = f"{BASE}/cron/output/51604df99f62"
V5_STATE = f"{BASE}/scripts/v5_paper_state.json"
JOURNEY_STATE = f"{BASE}/scripts/journey_state.json"
CRYPTO_STATE = f"{BASE}/paper_trader_data/live_state.json"
REAL_JOURNAL = f"{BASE}/scripts/trade_journal.json"
CRYPTO_JOURNAL = f"{BASE}/scripts/crypto_trade_journal.json"

sys.path.insert(0, f"{BASE}/scripts")


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def last_close(ticker):
    """Best-effort last close via monitor_entries TV fetch (returns Yahoo-shaped dict)."""
    try:
        from monitor_entries import fetch_chart, extract_series
        data = fetch_chart(ticker, "5d", "1d")
        closes, _, _, _, _, _ = extract_series(data)
        if closes:
            return closes[-1]
    except Exception:
        pass
    return None


# ---------------------------------------------------------------- scan digest
def scan_digest():
    alerts = {}  # ticker -> (score, price, regime)
    runs = 0
    if os.path.isdir(SCAN_DIR):
        for f in sorted(glob.glob(f"{SCAN_DIR}/*.md")):
            m = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})", f)
            if not m:
                continue
            try:
                fdate = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H-%M").replace(tzinfo=BKK)
            except ValueError:
                continue
            if fdate < WEEK_AGO:
                continue
            txt = open(f).read()
            if "Status: silent" in txt or "script failed" in txt:
                runs += 1
                continue
            runs += 1
            for ticker, score, price, regime in re.findall(
                r"\*\*\d+\. ([A-Z]+)\*\* — Score ([\d.]+) \| \$([\d.]+) \| (\w+)", txt
            ):
                prev = alerts.get(ticker)
                if not prev or float(score) > prev[0]:
                    alerts[ticker] = (float(score), float(price), regime)
    return runs, alerts


# ---------------------------------------------------------------- V5 paper
def v5_section(state):
    if not state:
        return "> V5: no state"
    capital = state.get("capital", 0.0)
    peak = state.get("peak_capital", 0.0)
    positions = state.get("positions", [])
    trades = state.get("closed_trades", [])
    total_value = capital + sum(p.get("capital_risked", 0) for p in positions)
    total_return = (total_value - 1000.0) / 1000.0 * 100
    dd = (peak - total_value) / peak * 100 if peak > 0 else 0
    wins = [t for t in trades if t.get("r_multiple", 0) > 0]
    losses = [t for t in trades if t.get("r_multiple", 0) < 0]
    total_r = sum(t.get("r_multiple", 0) for t in trades)
    pf = (abs(sum(t["r_multiple"] for t in wins) / sum(t["r_multiple"] for t in losses))
          if losses else 99.0)
    wr = len(wins) / len(trades) * 100 if trades else 0
    unrealized = sum(
        (p.get("current_price", p.get("entry_price", 0)) - p.get("entry_price", 0)) * p.get("shares", 0)
        for p in positions
    )
    lines = [
        f"**V5** (9-Factor S&P 500) — Equity ${total_value:,.2f} | {total_return:+.1f}% | DD {dd:.1f}%",
        f"Open {len(positions)} | Closed {len(trades)} | WR {wr:.0f}% | PF {pf:.2f} | ΣR {total_r:+.2f}",
    ]
    if positions:
        pos_str = ", ".join(
            f"{p.get('ticker')} {p.get('current_price', p.get('entry_price', 0)) - p.get('entry_price', 0):+.0f}%"
            for p in positions
        )
        lines.append(f"  Positions: {pos_str}")
    return "\n".join(lines)


def journey_section(state):
    if not state:
        return "> Journey: no state"
    capital = state.get("capital", 0.0)
    peak = state.get("peak_capital", 0.0)
    positions = state.get("positions", [])
    trades = state.get("closed_trades", [])
    total_value = capital + sum(p.get("capital_risked", 0) for p in positions)
    total_return = (total_value - 10000.0) / 10000.0 * 100
    dd = (peak - total_value) / peak * 100 if peak > 0 else 0
    return (
        f"**Journey** (11-Factor stocks) — Equity ${total_value:,.2f} | {total_return:+.1f}% | DD {dd:.1f}% | "
        f"Open {len(positions)} | Closed {len(trades)}"
    )


def crypto_section(state):
    if not state:
        return "> Crypto POC: no state"
    equity = state.get("equity", 0.0)
    start = state.get("starting_capital", 300.0)
    peak = state.get("peak_equity", 0.0)
    ret = (equity - start) / start * 100
    dd = (peak - equity) / peak * 100 if peak > 0 else 0
    open_n = sum(1 for cs in state.get("coin_states", {}).values() if cs.get("position"))
    trades = len(state.get("trades", []))
    return (
        f"**Crypto POC** (Hyperliquid 11-Factor) — Equity ${equity:,.2f} | {ret:+.1f}% | DD {dd:.1f}% | "
        f"Open {open_n} | Trades {trades}"
    )


# ---------------------------------------------------------------- real account
def real_stocks_section(journal):
    if not journal:
        return "> Real stocks: no journal"
    trades = journal.get("trades", [])
    closed = [t for t in trades if t.get("status") != "OPEN"]
    open_t = [t for t in trades if t.get("status") == "OPEN"]
    realized = sum(t.get("pnl_usd", 0) for t in closed)
    lines = [f"**Real stocks** (Dime/IBKR) — Realized {len(closed)} trades: ${realized:+,.2f} | WR {journal.get('realized_summary', {}).get('win_rate', 0):.0f}%"]
    for t in open_t:
        cost = t.get("cost_basis", 0)
        qty = t.get("quantity", 0)
        entry = t.get("entry_price", 0)
        close = last_close(t["ticker"])
        if close:
            pnl = (close - entry) * qty
            line = f"  {t['ticker']} {qty}sh @ ${entry:.2f} → ${close:.2f} ({pnl:+,.2f})"
        else:
            line = f"  {t['ticker']} {qty}sh @ ${entry:.2f} (cost ${cost:,.2f})"
        lines.append(line)
    return "\n".join(lines)


def real_crypto_section(journal):
    if not journal:
        return "> Real crypto: no journal"
    realized = journal.get("realized_pnl_usdc", 0)
    lines = [f"**Real crypto** (Hyperliquid perps) — Realized ${realized:+.2f} USDC | WR {journal.get('win_rate', 0)*100:.0f}%"]
    for t in journal.get("open_positions", []):
        lines.append(f"  {t['ticker']} {t.get('quantity', 0)} @ ${t.get('entry_price', 0):.2f} — {t.get('status', 'open')}")
    return "\n".join(lines)


# ---------------------------------------------------------------- main
def main():
    runs, alerts = scan_digest()
    v5 = v5_section(load_json(V5_STATE))
    journey = journey_section(load_json(JOURNEY_STATE))
    crypto = crypto_section(load_json(CRYPTO_STATE))
    real_s = real_stocks_section(load_json(REAL_JOURNAL))
    real_c = real_crypto_section(load_json(CRYPTO_JOURNAL))

    out = [f"📊 **Weekly Recap — {NOW.strftime('%a %d %b %Y')}** (W{NOW.isocalendar()[1]})", ""]

    out.append("## 🔍 Market Scans (7d)")
    if alerts:
        for t, (score, price, regime) in sorted(alerts.items(), key=lambda x: -x[1][0]):
            out.append(f"- {t} — {score:.1f} | ${price:.2f} | {regime}")
    else:
        out.append("- No qualifying setups (≥7.0) this week")
    out.append(f"_Runs: {runs} weekday scans_")
    out.append("")

    out.append("## 🤖 Paper Traders")
    for s in (v5, journey, crypto):
        out.append("- " + s)
    out.append("")

    out.append("## 💰 Real Account")
    for s in (real_s, real_c):
        for line in s.splitlines():
            out.append(("- " + line) if not line.startswith("  ") else line)
    out.append("")

    out.append("_Auto-generated Sunday recap — scan digest + paper + real._")
    print("\n".join(out))


if __name__ == "__main__":
    main()