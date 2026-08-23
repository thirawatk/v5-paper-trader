#!/usr/bin/env python3
"""
Daily Full-Market Scan — TradingView bulk API (single request).
Runs at 04:30 ICT after US close. Watchdog mode: outputs ONLY when
a setup scores >= MIN_SCORE and is NEW (not in previous day's report).
"""
import json, urllib.request, os
from datetime import datetime, timezone, timedelta

BKK = timezone(timedelta(hours=7))
STATE_FILE = "/root/.hermes/profiles/trader/scripts/daily_scan_state.json"
UNIVERSE_FILE = "/root/.hermes/profiles/trader/scripts/journey_universe.txt"

MIN_SCORE = 7.0        # quality floor for alerts
TOP_N = 10             # max setups to show

COLS = ["name","exch","close","open","rsi","stoch","atr","sma20","sma50","sma200",
        "vol","avgvol","macd","macd_sig","cmf","mfi_like","mom","high3m","mcap"]


def load_universe():
    with open(UNIVERSE_FILE) as f:
        return [l.strip() for l in f if l.strip() and not l.startswith('#')]


def scan():
    tickers = load_universe()
    ticker_set = set(tickers)
    url = "https://scanner.tradingview.com/america/scan"
    body = {
        "filter": [
            {"left": "name", "operation": "match", "right": "|".join(sorted(ticker_set))},
            {"left": "type", "operation": "equal", "right": "stock"},
        ],
        "options": {"lang": "en"},
        "markets": ["america"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": [
            "name", "exchange", "close", "open",
            "RSI", "Stoch.K", "ATR",
            "SMA20", "SMA50", "SMA200",
            "volume", "average_volume_30d_calc",
            "MACD.macd", "MACD.signal",
            "ChaikinMoneyFlow",
            "MoneyFlow",
            "momentum",
            "High.3M.all", "market_cap_basic",
        ],
        "sort": {"sortBy": "name", "sortOrder": "asc"},
        "range": [0, len(tickers) * 3],
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    rows = data.get("data", [])

    candidates = []
    matched_exact = 0
    for row in rows:
        d = row.get("d")
        if not d or len(d) < len(COLS):
            continue
        r = dict(zip(COLS, d))
        name = r['name']
        if name not in ticker_set:
            continue
        matched_exact += 1

        price = r['close']
        if price is None or price <= 1:
            continue
        if any(r.get(k) is None for k in ('close','rsi','stoch','atr','sma20','sma50','sma200')):
            continue

        mcap = r.get('mcap')
        vol = r.get('vol') or 0
        if mcap and mcap < 5e8:
            continue
        if vol * price < 2e6:
            continue

        rsi, stoch = r['rsi'], r['stoch']
        sma20, sma50, sma200 = r['sma20'], r['sma50'], r['sma200']
        atr = r['atr']
        avgvol = r.get('avgvol')
        vol_ratio = round(vol / avgvol, 2) if avgvol else 1.0

        if price > sma20 and sma20 >= sma50 and price > sma200:
            regime = 'UPTREND'
        elif sma50 <= price <= sma20 and price > sma200:
            regime = 'PULLBACK'
        elif price < sma20 and price >= sma50:
            regime = 'PULLBACK'
        elif price < sma50 and price < sma20 and price < sma200:
            regime = 'DOWNTREND'
        else:
            regime = 'MIXED'

        if regime not in ('UPTREND', 'PULLBACK') or rsi > 45:
            continue

        score = 0
        s = 3 if rsi < 25 else 2.5 if rsi < 30 else 2 if rsi < 35 else 1 if rsi < 40 else 0.5
        score += s
        s = 1.5 if stoch < 15 else 1 if stoch < 25 else 0
        score += s
        s = 2 if vol_ratio < 0.3 else 1.5 if vol_ratio < 0.5 else 1 if vol_ratio < 0.8 else 0
        score += s
        margin = (price / sma200 - 1) * 100
        s = 2 if margin > 3 else 1 if margin > 0 else 0
        score += s
        s = 1.5 if regime == 'PULLBACK' else 0.75
        score += s
        high3m = r.get('high3m')
        from_high = ((price / high3m - 1) * 100) if high3m else None
        s = (1 if from_high > -12 else 0.5 if from_high > -18 else 0) if from_high is not None else 0
        score += s
        macd, macd_sig = r.get('macd'), r.get('macd_sig')
        hist = (macd - macd_sig) if (macd is not None and macd_sig is not None) else None
        s = (1.5 if hist > 0 else 0.75 if hist > -abs(macd or 1) * 0.15 else 0) if hist is not None else 0
        score += s
        cmf = r.get('cmf')
        s = (1.5 if cmf > 0.1 else 0.75 if cmf > 0 else 0) if cmf is not None else 0
        score += s
        mfi_like = r.get('mfi_like')
        s = (1 if mfi_like < 40 else 0.5 if mfi_like < 55 else 0) if mfi_like is not None else 0
        score += s
        mom = r.get('mom')
        s = 1 if (mom is not None and mom > 0) else 0
        score += s

        candidates.append({
            'ticker': name, 'price': round(price, 2), 'regime': regime,
            'rsi': round(rsi, 1), 'stoch': round(stoch, 1), 'vol_ratio': vol_ratio,
            'score': round(score, 2),
            'macd_hist': round(hist, 3) if hist is not None else None,
            'cmf': round(cmf, 3) if cmf is not None else None,
            'mfi': round(mfi_like, 1) if mfi_like is not None else None,
            'sl': round(price - 2 * atr, 2),
            'tp2': round(price + 2.5 * atr, 2),
            'mcap_m': round(mcap / 1e6) if mcap else None,
        })

    candidates.sort(key=lambda x: -x['score'])
    return {'matched': matched_exact, 'universe': len(tickers), 'candidates': candidates}


def main():
    now = datetime.now(BKK)
    now_str = now.strftime("%a %d %b %Y")

    # Weekday gate only — cron schedule handles the time
    if now.weekday() >= 5:
        return

    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
    prev_tickers = set(state.get('reported_tickers', []))

    try:
        result = scan()
    except Exception:
        return  # silent on data failure; next run retries

    qualified = [c for c in result['candidates'] if c['score'] >= MIN_SCORE][:TOP_N]

    # Watchdog: only output if there are NEW qualifying tickers vs last reported
    new_qualified = [c for c in qualified if c['ticker'] not in prev_tickers]
    if not new_qualified:
        # save state silently
        state['last_run'] = now.isoformat()
        state['reported_tickers'] = [c['ticker'] for c in qualified]
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=1)
        return

    lines = [f"🔍 **Daily Market Scan — {now_str}**",
             f"Universe: {result['matched']} stocks analyzed | Qualifying: {len(qualified)} (≥{MIN_SCORE})", ""]
    for i, c in enumerate(new_qualified, 1):
        mcap = f"${c['mcap_m']/1000:.1f}B" if c['mcap_m'] and c['mcap_m'] >= 1000 else (f"${c['mcap_m']}M" if c['mcap_m'] else '?')
        flags = []
        if c['cmf'] is not None and c['cmf'] > 0: flags.append("💰CMF+")
        if c['macd_hist'] is not None and c['macd_hist'] > 0: flags.append("📈MACD+")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        lines.append(
            f"**{i}. {c['ticker']}** — Score {c['score']} | ${c['price']} | {c['regime']} | {mcap}{flag_str}\n"
            f"   RSI {c['rsi']} | Stoch {c['stoch']} | Vol {c['vol_ratio']}x\n"
            f"   SL ${c['sl']} | TP2 ${c['tp2']}"
        )
    lines.append("")
    lines.append("_Confirmation required before entry (green candle / Wyckoff buy-stop)._")

    print("\n".join(lines))

    state['last_run'] = now.isoformat()
    state['reported_tickers'] = [c['ticker'] for c in qualified]
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=1)


if __name__ == "__main__":
    main()
