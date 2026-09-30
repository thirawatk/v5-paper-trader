#!/usr/bin/env python3
"""Quick test: NASDAQ 100 only to verify the backtest runs."""
import sys, time
sys.path.insert(0, '/root/.hermes/profiles/trader/scripts')
from backtest_8factor_indices import *

t0 = time.time()

vix_df = yf.Ticker('^VIX').history(start=START_DATE, end=END_DATE)
vix_map = {idx.strftime('%Y-%m-%d'): vix_df.loc[idx, 'Close'] for idx in vix_df.index}
print(f'VIX: {len(vix_map)} points')

tickers = get_nasdaq100()
print(f'NASDAQ 100: {len(tickers)} tickers')

raw = run_backtest('NASDAQ 100', tickers, vix_map)
summary = compute_summary(raw)

print(f'\n=== RESULTS ===')
print(f'Elapsed: {time.time()-t0:.0f}s')
print(f'Signals: {summary["total_signals"]}')
print(f'Avg R: {summary["avg_r"]}')
print(f'Win Rate R: {summary["win_rate_r"]}%')
print(f'Profit Factor: {summary["profit_factor"]}')
print(f'TP1: {summary["tp1_pct"]}% | TP2: {summary["tp2_pct"]}% | SL: {summary["sl_pct"]}% | Exp: {summary["expired_pct"]}%')
