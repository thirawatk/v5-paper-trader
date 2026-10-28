#!/usr/bin/env python3
"""
Daily Full-Market Scan — TradingView bulk API (paginated full-market pull).
Runs at 04:30 ICT after US close. Outputs the qualified list every run, flagging
tickers new vs the previous day.

FIX 2026-10-29: the old `name match |TI|ER|LIST` filter is SUBSTRING-based in the
TradingView screener (asking for "BA" returns BAC, BABA, ABAT...). With 1,463
tickers it produced ~4,389 rows against a capped response, so only 539 exact
names survived — i.e. the scan silently covered ~37% of the universe and the
surviving set depended on truncation order. Now: paginated full-market pull with
server-side liquidity floors, then exact intersection with the universe file.
"""
import json, urllib.request, os
from datetime import datetime, timezone, timedelta

BKK = timezone(timedelta(hours=7))
STATE_FILE = "/root/.hermes/profiles/trader/scripts/daily_scan_state.json"
UNIVERSE_FILE = "/root/.hermes/profiles/trader/scripts/journey_universe.txt"

MIN_SCORE = 7.0        # quality floor for alerts
TOP_N = 10             # max setups to show
MIN_MCAP = 5e8         # $500M liquidity floor (server-side)
MIN_VOL = 200000       # 200k shares/day (server-side; dollar floor applied again client-side)

COLS = ["name","exch","close","open","rsi","stoch","atr","sma20","sma50","sma200",
        "vol","avgvol","macd","macd_sig","cmf","mfi_like","mom","high3m","mcap"]

URL = "https://scanner.tradingview.com/america/scan"


def load_universe():
    with open(UNIVERSE_FILE) as f:
        return [l.strip() for l in f if l.strip() and not l.startswith('#')]


def _post(body):
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST")
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read()).get("data", [])


def fetch_market_rows():
    """Paginated full-market pull. Deterministic + complete (no substring bleed)."""
    base = {
        "filter": [
            {"left": "type", "operation": "equal", "right": "stock"},
            {"left": "market_cap_basic", "operation": "greater", "right": MIN_MCAP},
            {"left": "volume", "operation": "greater", "right": MIN_VOL},
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
    }
    rows = []
    for lo in range(0, 8000, 1000):
        body = dict(base)
        body["range"] = [lo, lo + 1000]
        chunk = _post(body)
        rows.extend(chunk)
        if len(chunk) < 1000:
            break
    return rows


def scan():
    tickers = load_universe()
    ticker_set = set(tickers)
    rows = fetch_market_rows()

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
        if mcap and mcap < MIN_MCAP:
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
            'from_high': round(from_high, 1) if from_high is not None else None,
            'atr': round(atr, 2),
            'sma20': round(sma20, 2), 'sma50': round(sma50, 2), 'sma200': round(sma200, 2),
        })

    candidates.sort(key=lambda x: -x['score'])
    return {'matched': matched_exact, 'universe': len(tickers),
            'market_rows': len(rows), 'candidates': candidates}


def main():
    now = datetime.now(BKK)
    now_str = now.strftime("%a %d %b %Y")

    if now.weekday() >= 5:
        return

    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
    prev_tickers = set(state.get('reported_tickers', []))

    try:
        result = scan()
    except Exception as e:
        print(f"SCAN ERROR: {e}")
        state['last_run'] = now.isoformat()
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=1)
        return

    # persist full candidate list for downstream report writers
    with open('/root/.hermes/profiles/trader/scripts/daily_scan_latest.json', 'w') as f:
        json.dump({'run': now.isoformat(), **{k: v for k, v in result.items() if k != 'candidates'},
                   'candidates': result['candidates'][:40]}, f, indent=1)

    qualified = [c for c in result['candidates'] if c['score'] >= MIN_SCORE][:TOP_N]
    new_set = set(c['ticker'] for c in qualified) - prev_tickers

    lines = [f"🔍 **Daily Market Scan — {now_str}**",
             f"Universe: {result['matched']} stocks analyzed | Qualifying: {len(qualified)} (>= {MIN_SCORE})",
             f"_(market rows pulled: {result['market_rows']} | universe file: {result['universe']})_", ""]
    for i, c in enumerate(qualified, 1):
        mcap = f"${c['mcap_m']/1000:.1f}B" if c['mcap_m'] and c['mcap_m'] >= 1000 else (f"${c['mcap_m']}M" if c['mcap_m'] else '?')
        new_tag = " 🆕" if c['ticker'] in new_set else ""
        flags = []
        if c['cmf'] is not None and c['cmf'] > 0: flags.append("💰CMF+")
        if c['macd_hist'] is not None and c['macd_hist'] > 0: flags.append("📈MACD+")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        lines.append(
            f"**{i}. {c['ticker']}**{new_tag} — Score {c['score']} | ${c['price']} | {c['regime']} | {mcap}{flag_str}\n"
            f"   RSI {c['rsi']} | Stoch {c['stoch']} | Vol {c['vol_ratio']}x\n"
            f"   SL ${c['sl']} | TP2 ${c['tp2']}"
        )
    if not qualified and result['candidates']:
        best = result['candidates'][:3]
        lines.append("**Near-misses (below floor):** " + ", ".join(
            f"{c['ticker']} {c['score']}" for c in best))
    lines.append("")
    lines.append("_Confirmation required before entry (green candle / Wyckoff buy-stop)._")

    print("\n".join(lines))

    state['last_run'] = now.isoformat()
    state['reported_tickers'] = [c['ticker'] for c in qualified]
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=1)


if __name__ == "__main__":
    main()
