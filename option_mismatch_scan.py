#!/usr/bin/env python3
"""
VOO monthly option mismatch scanner.

Finds strikes where the market's implied probability of reaching the strike
is LOWER than VOO's empirical probability over the same horizon (from 5y of
daily data) -> underpriced/mispriced strikes with multiple-X potential.

Data: CBOE delayed quotes API (chain, no auth) + Yahoo chart API (history).
Note: quotes are Friday-close when run on weekends.

CBOE 'iv' field is a DECIMAL (0.1386 = 13.86%), not percent.
"""
import json, urllib.request, datetime, math, statistics as st
from statistics import NormalDist

N = NormalDist()
R = 0.042   # risk-free (approx 2026)
Q = 0.013   # VOO dividend yield approx
TICKER = 'VOO'

def get(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36',
        'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def parse_occ(occ):
    rest = occ.strip().replace(' ', '')
    yy, mm, dd = int(rest[3:5]), int(rest[5:7]), int(rest[7:9])
    ctype = rest[9]
    strike = int(rest[10:]) / 1000.0
    return datetime.date(2000 + yy, mm, dd), ctype, strike

def third_friday(year, month):
    d = datetime.date(year, month, 1)
    fridays = [d + datetime.timedelta(days=i) for i in range(35)
               if d + datetime.timedelta(days=i) <= datetime.date(year, month, 28) + datetime.timedelta(days=7)
               and (d + datetime.timedelta(days=i)).weekday() == 4]
    return fridays[2] if len(fridays) >= 3 else fridays[-1]

def emp_prob_from(sorted_fwd, x):
    lo, hi = 0, len(sorted_fwd)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_fwd[mid] < x: lo = mid + 1
        else: hi = mid
    return 1 - lo / len(sorted_fwd)

def main():
    today = datetime.date.today()

    # --- Chain ---
    d = get(f'https://cdn.cboe.com/api/global/delayed_quotes/options/{TICKER}.json')
    data = d['data']
    spot = data['current_price']
    contracts = []
    for o in data['options']:
        try:
            exp, ctype, strike = parse_occ(o['option'])
        except Exception:
            continue
        bid, ask = o.get('bid'), o.get('ask')
        mid = (bid + ask) / 2 if bid and ask and bid > 0 else o.get('last_trade_price') or o.get('theo')
        if not mid or mid <= 0: continue
        contracts.append({'exp': exp, 'type': ctype, 'strike': strike, 'mid': mid,
                          'iv': o.get('iv'), 'oi': o.get('open_interest') or 0})

    avail_exps = sorted(set(c['exp'] for c in contracts if c['exp'] > today))

    # --- Pick next 3 monthly expiries that EXIST in chain ---
    y, m = today.year, today.month
    monthlies = []
    for i in range(6):
        yy, mm = (y, m + i) if m + i <= 12 else (y + 1, m + i - 12)
        f = third_friday(yy, mm)
        if (f - today).days > 20:
            monthlies.append(f)
    picked = [e for e in monthlies if e in avail_exps]
    # fill with any available expiries 25-120 DTE if short
    for e in avail_exps:
        if len(picked) >= 3: break
        if e not in picked and 25 <= (e - today).days <= 120:
            picked.append(e)
    picked = sorted(picked)[:3]
    if not picked:
        print("No usable expiries"); return

    # --- History (5y daily) ---
    h = get(f'https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?range=5y&interval=1d')['chart']['result'][0]
    closes = [c for c in h['indicators']['quote'][0]['close'] if c]
    rv30 = st.pstdev([closes[i] / closes[i-1] - 1 for i in range(len(closes)-30, len(closes))]) * math.sqrt(252)
    rv60 = st.pstdev([closes[i] / closes[i-1] - 1 for i in range(len(closes)-60, len(closes))]) * math.sqrt(252)

    print(f"# {TICKER} option mismatch scan | spot {spot:.2f} | RV30 {rv30*100:.1f}% | RV60 {rv60*100:.1f}% | {today} (weekend = Fri close)\n")

    for e in picked:
        DTE = (e - today).days
        T = DTE / 365.0
        n_days = max(5, int(round(DTE * 5 / 7)))

        fwd = sorted([closes[i + n_days] / closes[i] - 1 for i in range(len(closes) - n_days)])
        emp = lambda x: emp_prob_from(fwd, x)

        calls = sorted([c for c in contracts if c['exp'] == e and c['type'] == 'C'], key=lambda c: c['strike'])
        puts = [c for c in contracts if c['exp'] == e and c['type'] == 'P']
        if not calls: continue
        atm_c = min(calls, key=lambda c: abs(c['strike'] - spot))
        atm_p = min(puts, key=lambda c: abs(c['strike'] - spot)) if puts else None
        straddle = atm_c['mid'] + (atm_p['mid'] if atm_p else atm_c['mid'])
        sigT = straddle / (0.8 * spot)

        def analyze(ctype, direction):
            # direction: +1 = calls OTM above spot, -1 = puts OTM below spot
            rows = []
            for c in contracts:
                if c['exp'] != e or c['type'] != ctype or not c['iv'] or c['iv'] <= 0: continue
                K = c['strike']
                dist = (K - spot) / spot
                if direction > 0:
                    if dist <= 0.005 or dist > 0.12: continue
                else:
                    if dist >= -0.005 or dist < -0.12: continue
                iv = c['iv']  # DECIMAL already
                d2 = (math.log(spot / K) + (R - Q - iv * iv / 2) * T) / (iv * math.sqrt(T))
                imp_prob = N.cdf(d2)
                emp_prob = emp(dist)
                edge = emp_prob - imp_prob
                # multiple-X: if spot reaches the 1-sigma target (realistic) — the old "X@hit" was
                # mislabeled: (K-spot)/mid is the multiple if spot finishes at 2x distance-to-strike,
                # NOT if spot merely touches the strike (which pays ~0 at expiry).
                if direction > 0:
                    X_1sig = max(0.0, spot * (1 + sigT) - K) / c['mid']
                else:
                    X_1sig = max(0.0, spot * (1 - sigT) - K) / c['mid']
                rows.append({'K': K, 'mid': c['mid'], 'iv': iv * 100, 'oi': c['oi'],
                             'imp': imp_prob, 'emp': emp_prob, 'edge': edge,
                             'X1sig': X_1sig})
            return rows

        call_rows = analyze('C', +1)
        put_rows = analyze('P', -1)

        print(f"=== {e} | DTE {DTE} | ATM {atm_c['strike']:.0f} | Straddle {straddle:.2f} "
              f"({straddle/spot*100:.2f}%) | Priced 1σ {sigT*100:.2f}% ===")

        print(f"-- CALLS (upside) --")
        print(f"{'Strike':>7} {'Mid$':>6} {'IV%':>6} {'ImpP%':>6} {'EmpP%':>6} {'Edge%':>7} {'X@1σ':>6} {'OI':>7}")
        liq = [x for x in call_rows if x['oi'] >= 100]
        for x in sorted(liq, key=lambda r: -r['edge'])[:10]:
            print(f"{x['K']:>7.0f} {x['mid']:>6.2f} {x['iv']:>6.1f} {x['imp']*100:>6.1f} {x['emp']*100:>6.1f} "
                  f"{x['edge']*100:>+7.1f} {x['X1sig']:>6.1f} {x['oi']:>7.0f}")

        print(f"-- PUTS (downside / crash lotto) --")
        print(f"{'Strike':>7} {'Mid$':>6} {'IV%':>6} {'ImpP%':>6} {'EmpP%':>6} {'Edge%':>7} {'X@1σ':>6} {'OI':>7}")
        liq_p = [x for x in put_rows if x['oi'] >= 100]
        for x in sorted(liq_p, key=lambda r: -r['edge'])[:8]:
            print(f"{x['K']:>7.0f} {x['mid']:>6.2f} {x['iv']:>6.1f} {x['imp']*100:>6.1f} {x['emp']*100:>6.1f} "
                  f"{x['edge']*100:>+7.1f} {x['X1sig']:>6.1f} {x['oi']:>7.0f}")
        print()

    # --- ATM vol premium reality check ---
    e0 = picked[0]
    atm_iv = next((c['iv'] for c in contracts if c['exp'] == e0 and c['type'] == 'C'
                   and abs(c['strike'] - spot) == min(abs(x['strike'] - spot) for x in contracts
                                                      if x['exp'] == e0 and x['type'] == 'C' and x['iv'])), None)
    if atm_iv:
        print(f"ATM IV ({e0}, DTE {(e0-today).days}): {atm_iv*100:.1f}% vs RV30 {rv30*100:.1f}% -> vol premium {atm_iv*100 - rv30*100:+.1f} pts")
        print("(+ premium = options expensive on average; - premium = vol underpriced NOW)")

if __name__ == '__main__':
    main()
