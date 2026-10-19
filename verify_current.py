#!/usr/bin/env python3
"""Quick verification of ZS exit and CRWV conditional state."""
from monitor_entries import analyze_ticker, calculate_dynamic_exits, check_exit_signals, POSITIONS, get_verdict
from datetime import datetime, timezone, timedelta
import sys

BKK = timezone(timedelta(hours=7))
now = datetime.now(BKK)
now_str = now.strftime("%a %d %b %Y %H:%M ICT")
print(f"=== Current time: {now_str} ===\n")

# ZS position check
zs = analyze_ticker("ZS")
if zs:
    print("=== ZS (Exit Signal Check) ===")
    pos = POSITIONS["ZS"]
    print(f"Position: {pos}")
    print(f"Current: price=${zs['price']:.2f}, rsi={zs['rsi14']}, stoch={zs.get('stoch_k')}, regime={zs['regime']}")
    print(f"SMA20={zs.get('sma20')}, SMA50={zs.get('sma50')}, ATR={zs.get('atr14')}")
    dx = calculate_dynamic_exits(zs, pos)
    print(f"Dynamic exits: {dx}")
    exit_msg = check_exit_signals(zs, pos)
    if exit_msg:
        print(f"\nExit signal:\n{exit_msg}")

print("\n" + "="*60 + "\n")

# CRWV analysis
crwv = analyze_ticker("CRWV")
if crwv:
    print("=== CRWV (Conditional Setup Check) ===")
    print(f"Current: price=${crwv['price']:.2f}, rsi={crwv['rsi14']}, stoch={crwv.get('stoch_k')}, regime={crwv['regime']}")
    print(f"SMA20={crwv.get('sma20')}, SMA50={crwv.get('sma50')}, SMA100={crwv.get('sma100')}")
    print(f"Vol ratio={crwv['vol_ratio']}, ATR={crwv.get('atr14')}, Fib786={crwv.get('fib_786')}")
    print(f"3M low={crwv.get('low_3m')}")
    print(f"Verdict: {get_verdict(crwv)}")

print("\n" + "="*60 + "\n")

# AMZN check
amzn = analyze_ticker("AMZN")
if amzn:
    print("=== AMZN (Exit Signal Check) ===")
    pos = POSITIONS["AMZN"]
    print(f"Position: {pos}")
    print(f"Current: price=${amzn['price']:.2f}, rsi={amzn['rsi14']}, regime={amzn['regime']}")
    print(f"SMA20={amzn.get('sma20')}, invalidation=$256.68")
    exit_msg = check_exit_signals(amzn, pos)
    if exit_msg:
        print(f"\nExit signal:\n{exit_msg}")
    else:
        print("\nNo exit signal — AMZN exit resolved, position OPEN")

print("\n" + "="*60 + "\n")

# ACMR check
acmr = analyze_ticker("ACMR")
if acmr:
    print("=== ACMR (Not Routed Check) ===")
    print(f"Current: price=${acmr['price']:.2f}, rsi={acmr['rsi14']}, stoch={acmr.get('stoch_k')}, regime={acmr['regime']}")
    print(f"Verdict: {get_verdict(acmr)}")
