#!/usr/bin/env python3
"""
One-shot buy reminder: VOO 735C Sep 18 @ $3.80 limit.
Fetches live quote from CBOE and prints the reminder with current mid.
Fires Monday market open (or any scheduled time).
"""
import json, urllib.request, datetime

def get(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36',
        'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())

OCC_PREFIX = 'VOO260918C00735'  # Sep 18 2026 735 call

def main():
    lines = []
    lines.append("🔔 VOO 735C Sep 18 — BUY REMINDER")
    lines.append("• Order: 1 contract @ **$3.80** limit")
    try:
        d = get('https://cdn.cboe.com/api/global/delayed_quotes/options/VOO.json')
        data = d['data']
        spot = data['current_price']
        hit = None
        for o in data['options']:
            occ = o['option'].strip().replace(' ', '')
            if occ.startswith(OCC_PREFIX):
                bid, ask = o.get('bid'), o.get('ask')
                mid = (bid + ask) / 2 if bid and ask and bid > 0 else o.get('last_trade_price')
                hit = {'bid': bid, 'ask': ask, 'mid': mid, 'iv': o.get('iv'), 'oi': o.get('open_interest')}
                break
        if hit:
            iv = hit['iv'] * 100 if hit['iv'] else 0
            lines.append(f"• Live: mid **${hit['mid']:.2f}** (bid ${hit['bid']:.2f} / ask ${hit['ask']:.2f}), IV {iv:.1f}%, OI {hit['oi']}")
            lines.append(f"• Spot VOO: ${spot:.2f}")
            if hit['mid'] and hit['mid'] <= 4.20:
                lines.append("✅ Still in zone — mismatch likely intact, place the limit order.")
            else:
                lines.append("⚠️ Mid above $4.20 — mismatch may be gone. Re-run option_mismatch_scan.py before buying.")
        else:
            lines.append("• Live quote: NOT FOUND (chain may have rolled). Re-check manually.")
            lines.append("• Fri close reference: mid $4.00, edge EmpP 35.6% vs ImpP 21.2%, X@hit 6.1x")
    except Exception as e:
        lines.append(f"• Live quote unavailable ({e}). Fri close reference: mid $4.00.")
    lines.append("• Scan edge (Fri): EmpP 35.6% vs ImpP 21.2%, X@hit 6.1x, X@1σ 1.9x")
    print('\n'.join(lines))

if __name__ == '__main__':
    main()
