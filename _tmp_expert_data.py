#!/usr/bin/env python3
from monitor_entries import *
for t in ["RDDT", "BCC", "FBK", "AMZN", "ZS"]:
    a = analyze_ticker(t)
    if a:
        pos = POSITIONS.get(t, {})
        print(f"=== {t} ===")
        print(f"  price={a['price']}, regime={a['regime']}, RSI={a['rsi14']}, stoch={a.get('stoch_k')}, macd_hist={a.get('macd_hist')}, vol={a['vol_ratio']}x")
        print(f"  SMA20={a['sma20']}, SMA50={a['sma50']}, SMA100={a['sma100']}")
        print(f"  fib382={a['fib_382']}, fib50={a['fib_50']}, fib618={a['fib_618']}, fib786={a['fib_786']}")
        print(f"  high_3m={a['high_3m']}, low_3m={a['low_3m']}, atr14={a['atr14']}")
        print(f"  green_streak={a['green_streak']}, 5d: {a['red_days_5']}R/{a['green_days_5']}G")
        if t in POSITIONS:
            pos = POSITIONS[t]
            dx = calculate_dynamic_exits(a, pos)
            print(f"  POS: entry={pos['entry']}")
            print(f"  dyn: stop={dx['stop_loss']}, tp1={dx['tp1']}, tp2={dx['tp2']}, tp3={dx['tp3']}, tp2_r={dx['tp2_r']}")
            print(f"  dyn: momentum={dx['momentum_tag']}({dx['momentum_score']}), trailing={dx['trailing_active']}, signals={dx['signals']}")
            R = dx['R']
            print(f"  R={R}, entryR={pos['entry']}, 1.5R={round(pos['entry']+1.5*R,2)}, 2.5R={round(pos['entry']+2.5*R,2)}, 3.5R={round(pos['entry']+3.5*R,2)}")
    else:
        print(f"=== {t} === NO DATA")
