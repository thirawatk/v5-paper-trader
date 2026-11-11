import json
data = json.load(open("/root/.hermes/profiles/trader/cache/scratch/bars_1112.json"))
for t, d in data.items():
    print(f"== {t} @{d['exchange']} last={d['last']} prev={d['prev']} chg={d['chg_pct']}% rsi14={d['rsi14']} atr14={d['atr14']}")
    print(f"   sma20={d['sma20']} sma50={d['sma50']} sma100={d['sma100']} sma200={d['sma200']} "
          f"52wH={d['high_52w']} 52wL={d['low_52w']} avgvol30={d['avg_vol30']}")
    for b in d["bars"]:
        print(f"   {b['date']} O{b['open']:>9} H{b['high']:>9} L{b['low']:>9} C{b['close']:>9} V{b['vol']:>10}")
