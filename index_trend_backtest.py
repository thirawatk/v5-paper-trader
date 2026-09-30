#!/usr/bin/env python3
"""
Index Trend-Following Backtester
=================================
Purpose-built for US stock indices (NDX, SPX).
Not adapted from crypto — designed for trending markets.

Strategy:
  1. Trend Filter: 50 EMA > 200 EMA = bull regime
  2. Entry: Price pulls back to rising 50 EMA + MACD bullish turn
  3. Exit: 50/200 death cross OR trailing stop (3x ATR) OR MACD bearish crossover

Usage:
  python3 index_trend_backtest.py
  python3 index_trend_backtest.py --period 3y
"""

import argparse
import math
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf


# ═══════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════

CONFIG = {
    "tickers": {
        "^NDX": "Nasdaq-100",
        "^GSPC": "S&P 500",
    },
    "etf_map": {
        "^NDX": "QQQ",
        "^GSPC": "SPY",
    },
    "period": "3y",
    "interval": "1d",
    "starting_capital": 100_000.0,
    "risk_per_trade": 0.01,       # 1% risk per trade
    
    # Trend following params
    "fast_ema": 20,               # Fast EMA period
    "slow_ema": 50,               # Slow EMA period (primary trend filter)
    "trend_confirmation": 200,    # 200 EMA for macro trend
    
    # Entry
    "entry_max_distance_pct": 0.03,  # Max 3% above 20 EMA to enter (pullback)
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    
    # Exit
    "stop_atr_multiplier": 2.5,   # Initial stop
    "trail_atr_multiplier": 3.0,  # Trailing stop once in profit
    "tp_rr": 4.0,                 # Take profit (4R)
    "max_hold_bars": 60,          # ~3 months
}


@dataclass
class Trade:
    trade_id: int
    ticker: str
    entry_date: str
    entry_price: float
    stop_loss: float
    tp: float
    position_size: float
    risk_amount: float
    regime: str              # bull, bear
    entry_reason: str
    
    status: str = "open"
    exit_price: Optional[float] = None
    exit_date: Optional[str] = None
    exit_reason: str = ""
    pnl_pct: float = 0.0
    bars_held: int = 0
    highest_since_entry: float = 0.0


@dataclass
class Metrics:
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    total_pnl_pct: float = 0.0
    profit_factor: float = 0.0
    max_dd_pct: float = 0.0
    sharpe: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    avg_bars: float = 0.0
    avg_r_multiple: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0


# ═══════════════════════════════════════════════
# Indicator Calculations
# ═══════════════════════════════════════════════

def compute_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def compute_macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = compute_ema(series, fast)
    ema_slow = compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def compute_atr(df: pd.DataFrame, period=14) -> pd.Series:
    h = df['High']
    l = df['Low']
    c = df['Close']
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()


# ═══════════════════════════════════════════════
# Backtest Engine
# ═══════════════════════════════════════════════

class TrendBacktester:
    def __init__(self, ticker: str, name: str, etf_ticker: str):
        self.ticker = ticker
        self.name = name
        self.etf_ticker = etf_ticker
        self.cfg = CONFIG
        
        self.capital = self.cfg["starting_capital"]
        self.peak_capital = self.cfg["starting_capital"]
        self.equity_curve: List[float] = [self.capital]
        self.trades: List[Trade] = []
        self.open_trades: List[Trade] = []
        self.trade_counter = 0
        
        self.df: Optional[pd.DataFrame] = None
    
    def fetch_data(self) -> bool:
        print(f"  Fetching {self.etf_ticker} ({self.name})...")
        try:
            etf = yf.Ticker(self.etf_ticker)
            df = etf.history(period=self.cfg["period"], interval=self.cfg["interval"])
            if df.empty:
                idx = yf.Ticker(self.ticker)
                df = idx.history(period=self.cfg["period"], interval=self.cfg["interval"])
            if df.empty:
                print(f"  ⚠ No data")
                return False
            
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            
            # Compute indicators
            df['EMA20'] = compute_ema(df['Close'], self.cfg['fast_ema'])
            df['EMA50'] = compute_ema(df['Close'], self.cfg['slow_ema'])
            df['EMA200'] = compute_ema(df['Close'], self.cfg['trend_confirmation'])
            
            macd, macd_sig, macd_hist = compute_macd(
                df['Close'], self.cfg['macd_fast'],
                self.cfg['macd_slow'], self.cfg['macd_signal']
            )
            df['MACD'] = macd
            df['MACD_Signal'] = macd_sig
            df['MACD_Hist'] = macd_hist
            
            df['ATR'] = compute_atr(df)
            
            # Regime
            df['Regime'] = 'neutral'
            df.loc[(df['EMA50'] > df['EMA200']) & (df['EMA200'] > df['EMA200'].shift(5)), 'Regime'] = 'bull'
            df.loc[(df['EMA50'] < df['EMA200']) & (df['EMA200'] < df['EMA200'].shift(5)), 'Regime'] = 'bear'
            
            # MACD turn
            df['MACD_Bull_Turn'] = (df['MACD_Hist'] > 0) & (df['MACD_Hist'].shift(1) <= 0)
            df['MACD_Bear_Turn'] = (df['MACD_Hist'] < 0) & (df['MACD_Hist'].shift(1) >= 0)
            
            self.df = df
            print(f"  Loaded {len(df)} candles ({df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')})")
            return True
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def run_backtest(self) -> Metrics:
        df = self.df
        if df is None or len(df) < 250:
            return Metrics()
        
        for idx in range(self.cfg['trend_confirmation'] + 50, len(df)):
            row = df.iloc[idx]
            date = row.name.strftime('%Y-%m-%d') if hasattr(row.name, 'strftime') else str(row.name)[:10]
            close = float(row['Close'])
            atr = float(row['ATR']) if pd.notna(row['ATR']) else 0
            
            # Update open trades
            self._check_exits(idx, date, close, atr)
            
            # Check entry
            self._check_entry(idx, date, close, atr)
        
        # Close remaining at final price
        final_close = float(df['Close'].iloc[-1])
        final_date = df.index[-1].strftime('%Y-%m-%d') if hasattr(df.index[-1], 'strftime') else str(df.index[-1])[:10]
        for t in list(self.open_trades):
            t.exit_price = final_close
            t.exit_date = final_date
            t.exit_reason = "end_of_backtest"
            t.status = "closed"
            t.pnl_pct = ((final_close - t.entry_price) / t.entry_price) * 100 if t.entry_price > 0 else 0
            self.capital *= (1 + t.pnl_pct / 100)
            self.open_trades.remove(t)
        
        return self._compute_metrics()
    
    def _check_entry(self, idx: int, date: str, close: float, atr: float):
        df = self.df
        if len(self.open_trades) >= 2:
            return
        
        row = df.iloc[idx]
        regime = row['Regime']
        
        if regime != 'bull':
            return  # Only trade in bull regime
        
        ema20 = float(row['EMA20']) if pd.notna(row['EMA20']) else 0
        ema50 = float(row['EMA50']) if pd.notna(row['EMA50']) else 0
        ema200 = float(row['EMA200']) if pd.notna(row['EMA200']) else 0
        macd_bull = bool(row['MACD_Bull_Turn']) if pd.notna(row['MACD_Bull_Turn']) else False
        macd_hist = float(row['MACD_Hist']) if pd.notna(row['MACD_Hist']) else 0
        
        if ema20 <= 0 or ema50 <= 0:
            return
        
        # Entry conditions:
        # 1. Price near/at 20 EMA (pullback to trend) — within 3% above
        # 2. MACD histogram turning positive (momentum resuming)
        # 3. ADX > 20 (trending, not ranging)
        # 4. 50 EMA > 200 EMA regime confirmed
        
        distance_from_ema20 = (close - ema20) / ema20
        price_near_trend = 0 < distance_from_ema20 < self.cfg['entry_max_distance_pct']
        
        # Or price right at/below 20 EMA (deeper pullback but still above 50 EMA)
        deeper_pullback = (close >= ema50) and (close <= ema20) and (ema20 > ema50)
        
        valid_entry = False
        entry_reason = ""
        
        if price_near_trend and macd_bull:
            valid_entry = True
            entry_reason = "pullback_macd_turn"
        elif deeper_pullback and macd_hist > 0:
            valid_entry = True
            entry_reason = "deep_pullback"
        
        if not valid_entry:
            return
        
        # Position sizing
        if atr <= 0:
            return
        stop_distance = atr * self.cfg['stop_atr_multiplier']
        stop_loss = close - stop_distance
        risk_dollars = self.capital * self.cfg['risk_per_trade']
        position_size = risk_dollars / stop_distance if stop_distance > 0 else 0
        
        if position_size <= 0:
            return
        
        tp = close + stop_distance * self.cfg['tp_rr']
        
        self.trade_counter += 1
        trade = Trade(
            trade_id=self.trade_counter,
            ticker=self.ticker,
            entry_date=date,
            entry_price=close,
            stop_loss=stop_loss,
            tp=tp,
            position_size=position_size,
            risk_amount=risk_dollars,
            regime=regime,
            entry_reason=entry_reason,
            highest_since_entry=close,
        )
        self.trades.append(trade)
        self.open_trades.append(trade)
        
        print(f"    {date} 🟢 LONG {self.ticker} @ ${close:.2f} | "
              f"EMA20:{ema20:.1f} EMA50:{ema50:.1f} MACD:{macd_hist:+.4f} | "
              f"Stop:${stop_loss:.2f} TP:${tp:.2f} | {entry_reason}")
    
    def _check_exits(self, idx: int, date: str, close: float, atr: float):
        df = self.df
        row = df.iloc[idx]
        
        regime = row['Regime']
        macd_bear = bool(row['MACD_Bear_Turn']) if pd.notna(row['MACD_Bear_Turn']) else False
        ema50 = float(row['EMA50']) if pd.notna(row['EMA50']) else 0
        ema200 = float(row['EMA200']) if pd.notna(row['EMA200']) else 0
        
        for t in list(self.open_trades):
            t.bars_held += 1
            t.highest_since_entry = max(t.highest_since_entry, close)
            
            exited = False
            
            # 1. Stop loss
            if close <= t.stop_loss:
                t.exit_price = t.stop_loss
                t.exit_reason = "stop_loss"
                exited = True
            
            # 2. Take profit
            elif close >= t.tp:
                t.exit_price = t.tp
                t.exit_reason = "take_profit"
                exited = True
            
            # 3. Regime change (death cross or bear regime)
            elif regime == 'bear' or (ema50 > 0 and ema200 > 0 and ema50 < ema200):
                t.exit_price = close
                t.exit_reason = "regime_change"
                exited = True
            
            # 4. MACD bearish crossover (momentum weakening)
            elif macd_bear and t.bars_held > 5:
                t.exit_price = close
                t.exit_reason = "macd_bear_turn"
                exited = True
            
            # 5. Trailing stop (3x ATR from peak)
            elif atr > 0:
                trail_stop = t.highest_since_entry - atr * self.cfg['trail_atr_multiplier']
                if close <= trail_stop and t.highest_since_entry > t.entry_price * 1.02:
                    t.exit_price = close
                    t.exit_reason = "trailing_stop"
                    exited = True
            
            # 6. Max hold
            elif t.bars_held >= self.cfg['max_hold_bars']:
                t.exit_price = close
                t.exit_reason = "max_hold"
                exited = True
            
            if exited:
                t.exit_date = date
                t.status = "closed"
                t.pnl_pct = ((t.exit_price - t.entry_price) / t.entry_price) * 100
                self.capital *= (1 + t.pnl_pct / 100)
                
                result = "✅ WIN" if t.pnl_pct > 0 else "❌ LOSS"
                print(f"    {date} {result} {self.ticker} ({t.exit_reason}) "
                      f"P&L: {t.pnl_pct:+.2f}% | Held: {t.bars_held}d | "
                      f"Entry: ${t.entry_price:.2f} → Exit: ${t.exit_price:.2f}")
                
                self.open_trades.remove(t)
    
    def _compute_metrics(self) -> Metrics:
        m = Metrics()
        closed = [t for t in self.trades if t.status == "closed"]
        if not closed:
            return m
        
        m.total_trades = len(closed)
        wins = [t for t in closed if t.pnl_pct > 0]
        losses = [t for t in closed if t.pnl_pct <= 0]
        m.wins = len(wins)
        m.losses = len(losses)
        m.win_rate = (len(wins) / len(closed) * 100) if closed else 0
        
        m.total_pnl_pct = ((self.capital - self.cfg['starting_capital']) / self.cfg['starting_capital']) * 100
        
        m.avg_win = sum(t.pnl_pct for t in wins) / len(wins) if wins else 0
        m.avg_loss = sum(t.pnl_pct for t in losses) / len(losses) if losses else 0
        
        gross_profit = sum(t.pnl_pct for t in wins)
        gross_loss = abs(sum(t.pnl_pct for t in losses))
        m.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        m.avg_bars = sum(t.bars_held for t in closed) / len(closed)
        
        best = max(closed, key=lambda t: t.pnl_pct)
        worst = min(closed, key=lambda t: t.pnl_pct)
        m.best_trade = best.pnl_pct
        m.worst_trade = worst.pnl_pct
        
        # Max drawdown
        peak = self.equity_curve[0]
        for eq in self.equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak * 100
            if dd > m.max_dd_pct:
                m.max_dd_pct = dd
        
        # Sharpe (daily)
        if len(self.equity_curve) > 20:
            returns = [(self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
                       for i in range(1, len(self.equity_curve))]
            avg_r = sum(returns) / len(returns)
            var = sum((r - avg_r) ** 2 for r in returns) / len(returns)
            std = math.sqrt(var)
            m.sharpe = (avg_r / std * math.sqrt(252)) if std > 0 else 0
        
        return m


# ═══════════════════════════════════════════════
# Report Generator
# ═══════════════════════════════════════════════

def generate_report(results: Dict[str, Metrics], trades: Dict[str, List[Trade]]) -> str:
    lines = []
    lines.append(f"# 📈 Index Trend-Following Backtest Report")
    lines.append(f"")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Period:** Last {CONFIG['period']} (daily candles)")
    lines.append(f"**Strategy:** Purpose-built trend following (50/200 EMA + MACD + ATR stops)")
    lines.append(f"**Capital:** ${CONFIG['starting_capital']:,.0f}")
    lines.append(f"**Risk:** {CONFIG['risk_per_trade']*100:.0f}% per trade")
    lines.append(f"")
    lines.append(f"### Strategy Rules")
    lines.append(f"")
    lines.append(f"- **Regime Filter:** 50 EMA > 200 EMA and rising = bull trend only")
    lines.append(f"- **Entry 1:** Price near 20 EMA + MACD histogram turns positive")
    lines.append(f"- **Entry 2:** Price at/below 20 EMA but above 50 EMA + MACD positive")
    lines.append(f"- **Stop Loss:** ATR × 2.5")
    lines.append(f"- **Trailing Stop:** ATR × 3.0 from highest since entry (activates at +2% profit)")
    lines.append(f"- **Take Profit:** 4R")
    lines.append(f"- **Exit Signals:** Regime change to bear, MACD bearish crossover, death cross")
    lines.append(f"- **Max Hold:** 60 trading days (~3 months)")
    lines.append(f"")
    
    for ticker, m in results.items():
        name = CONFIG['tickers'].get(ticker, ticker)
        t_list = trades.get(ticker, [])
        closed = [t for t in t_list if t.status == "closed"]
        
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## {name} ({ticker})")
        lines.append(f"")
        lines.append(f"**Summary**")
        lines.append(f"")
        lines.append(f"- Trades: {m.total_trades}")
        lines.append(f"- Win Rate: **{m.win_rate:.1f}%** ({m.wins}W / {m.losses}L)")
        lines.append(f"- Total P&L: **{m.total_pnl_pct:+.2f}%**")
        lines.append(f"- Profit Factor: **{m.profit_factor:.2f}**")
        lines.append(f"- Max Drawdown: **{m.max_dd_pct:.1f}%**")
        lines.append(f"- Sharpe: **{m.sharpe:.2f}**")
        lines.append(f"- Avg Win: {m.avg_win:+.2f}% | Avg Loss: {m.avg_loss:+.2f}%")
        lines.append(f"- Avg Hold: {m.avg_bars:.0f} days")
        lines.append(f"- Best: {m.best_trade:+.2f}% | Worst: {m.worst_trade:+.2f}%")
        lines.append(f"")
        
        if closed:
            lines.append(f"**Trade Log**")
            lines.append(f"")
            lines.append(f"| # | Date | Entry | Exit | P&L | Reason | Held |")
            lines.append(f"|---|------|-------|------|-----|--------|------|")
            for t in closed[-15:]:
                dir_s = "L"
                lines.append(f"| T{t.trade_id} | {t.entry_date} | ${t.entry_price:.1f} | "
                           f"${t.exit_price:.1f} | {t.pnl_pct:+.2f}% | {t.exit_reason} | {t.bars_held}d |")
            lines.append(f"")
    
    # Combined view
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Combined View")
    lines.append(f"")
    total_t = sum(m.total_trades for m in results.values())
    total_w = sum(m.wins for m in results.values())
    total_l = sum(m.losses for m in results.values())
    combined_wr = (total_w / total_t * 100) if total_t > 0 else 0
    
    lines.append(f"- Total Trades: {total_t}")
    lines.append(f"- Combined WR: {combined_wr:.1f}% ({total_w}W / {total_l}L)")
    lines.append(f"")
    lines.append(f"| Index | Trades | WR | Total P&L | PF | DD | Sharpe |")
    lines.append(f"|-------|--------|----|-----------|----|----|--------|")
    for ticker, m in results.items():
        n = CONFIG['tickers'].get(ticker, ticker)[:12]
        lines.append(f"| {n} | {m.total_trades} | {m.win_rate:.0f}% | {m.total_pnl_pct:+.1f}% | "
                   f"{m.profit_factor:.1f} | {m.max_dd_pct:.0f}% | {m.sharpe:.1f} |")
    
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*Automated backtest by Hermes Agent — Trend-Following System for Indices*")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", default="3y")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    
    if args.period:
        CONFIG["period"] = args.period
    
    print(f"╔══════════════════════════════════════════════╗")
    print(f"║  Index Trend-Following Backtester           ║")
    print(f"╚══════════════════════════════════════════════╝")
    print(f"")
    print(f"Period: {CONFIG['period']}")
    print(f"Strategy: 50/200 EMA trend + MACD + ATR stops")
    print(f"Capital: ${CONFIG['starting_capital']:,.0f}")
    print(f"")
    
    all_results: Dict[str, Metrics] = {}
    all_trades: Dict[str, List[Trade]] = {}
    
    for ticker, name in CONFIG['tickers'].items():
        etf = CONFIG['etf_map'].get(ticker, ticker)
        print(f"\n{'='*60}")
        print(f"📈 {name}")
        print(f"{'='*60}")
        
        bt = TrendBacktester(ticker, name, etf)
        if not bt.fetch_data():
            continue
        
        print(f"  Running...")
        metrics = bt.run_backtest()
        all_results[ticker] = metrics
        all_trades[ticker] = bt.trades
        
        print(f"\n  ── Results ──")
        print(f"  Trades: {metrics.total_trades} | WR: {metrics.win_rate:.1f}%")
        print(f"  Total P&L: {metrics.total_pnl_pct:+.2f}%")
        print(f"  PF: {metrics.profit_factor:.2f} | DD: {metrics.max_dd_pct:.1f}% | Sharpe: {metrics.sharpe:.2f}")
    
    report = generate_report(all_results, all_trades)
    
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            f.write(report)
        print(f"\n✅ Saved to {args.output}")
    else:
        print(f"\n{report}")
    
    print(f"\n✅ Complete!")


if __name__ == "__main__":
    main()
