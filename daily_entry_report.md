# 📊 Daily Entry Report — Fri 23 Oct 2026 ICT
Consolidated report: Full-Scan watchlist (top DB candidates) + Intra-Day Entry-Monitor watchlist + 3-Expert Analysis + Active positions + Journey + Long-Term. ONE file to the user's DM.

> Architecture note: the Entry Monitor job (df659e3040fb) now runs as a cheap no_agent alert watchdog (text alerts + writes entry_monitor_report.md). The 3-expert analysis is consolidated into this single daily report produced by Daily Best Entry (51604df99f62, pro) at 04:30 ICT.

## 🔍 Full Scan Results (Daily Best Entry candidates)
_(Live full 1,463-scan top-5 is produced by the DB job itself (TradingView bulk). For today this report is assembled post-close from the Entry Monitor signals + ad-hoc expert runs; see the DB 04:30 job for the machine scan candidates.)_

## ⚡ Intra-Day Watchlist Snapshot (Entry Monitor — 03:00 ICT run)

| Ticker | Price | Δ% | RSI | Vol | SMA 20 | SMA 50 | SMA 100 | 5d | Verdict |
|--------|------:|---:|----:|----:|-------:|-------:|--------:|:--:|--------|
| GDDY | $114.68 | +5.40% | 80.0 | 0.87x | $101.51 | $99.51 | $93.35 | 1🔴/4🟢 | 🟡 OVERBOUGHT — wait pullback |
| BCC | $78.22 | +2.54% | 63.8 | 0.91x | $75.17 | $77.30 | $76.52 | 1🔴/4🟢 | 🟢 UPTREND — dip entry |
| FBK | $53.64 | +2.66% | 58.0 | 0.55x | $52.23 | $55.03 | $55.96 | 0🔴/5🟢 | ⚠️ BOUNCE — wait SMA50 reclaim |
| GEV | $827.34 | −7.07% | 20.7 | 2.35x | $959.42 | $956.50 | $989.29 | 5🔴/0🟢 | 🔴 WAIT — capitulation watch |
| MKSI | $196.11 | −7.12% | 14.2 | 1.98x | $250.84 | $260.95 | $302.51 | 4🔴/1🟢 | 🔴 WAIT — stop zone $196 |
| ACMR | $49.12 | −10.63% | 8.6 | 1.12x | $69.24 | $72.74 | $81.93 | 4🔴/1🟢 | 🔴 WAIT — knife below all SMAs |
| AMKR | $39.05 | −10.70% | 9.9 | 1.58x | $48.77 | $49.88 | $59.26 | 3🔴/2🟢 | 🔴 WAIT — sell-off |
| CRWV | $55.60 | −10.06% | 18.2 | 1.55x | $77.54 | $84.31 | $87.67 | 4🔴/1🟢 | ⏳ CAPITULATION WATCH |

## 🧠 3-Expert Analysis (active-position exits — consolidated from ad-hoc expert run)

| Ticker | Side | P&L | Verdicts (3 experts) | Consensus |
|--------|------|-----|----------------------|-----------|
| **ZS** | Trim | +58.5% (+$1,339) | Thorp(Med): trim half, stop $193.5→$217 · Wyckoff(Med): BC climax, UT risk Dec 1 · Medallion(Med): t≈0, extended | **TRIM 8–9/15 @ $235–241, trail $217–221, hard invalidation close<$212** |
| **AMZN** | Exit | −3.0% (−$77) | Thorp(HIGH): exit now · Wyckoff(Med): SOW breakdown · Medallion(Med): t<1 noise, coin-flip | **EXIT ALL 10 @ open ~$252; replay only >$256.68 / >$311** |

## 🚨 Exit Signals — Active Positions

| Ticker | Price | Entry | P&L | Regime | RSI | Stoch | ATR | Momentum | SL | TP1 | TP2 |
|--------|------:|------:|----:|--------|----:|------:|----:|----------|----|----:|----:|
| ZS | $237.76 | $150.00 | +58.5% | UPTREND | 69.1 | 92.7 | $12.05 | WEAK (+0) | $168.07 (1.5×ATR) | $168.07 (1.5R) | $174.10 (2.0R) |
| AMZN | $250.38 | $259.55 | −3.5% | DOWNTREND | 49.1 | 13.7 | $7.11 | NEUTRAL (+1) | $245.33 (2×ATR) | $270.22 (1.5R) | $277.32 (2.5R) |

| Ticker | Signals |
|--------|---------|
| ZS | 🎯 TP2 HIT $174.10 (2.0R); 📏 Near 3M High $241.12 — resistance; 📊 MACD Bearish (Hist −0.06); ⚠️ Do NOT carry into Dec 1 AMC earnings unprotected |
| AMZN | ⚠️ INVALIDATION PRINTED $250.38 < $256.68 → exit all; Earnings Oct 29 (T+5); 🔴 Below SMA20 |

## 📈 Trading Journey Snapshot (Thu 22 Oct, $10K paper)

| Ticker | Entry→ | R | Days | Status |
|--------|--------|:-:|:----:|---|
| ARKW | $154.06→$151.38 | −0.4R | 4d | 🔴 |
| HUBS | $240.51→$239.86 | −0.0R | 4d | 🔴 |
| ZM | $109.84→$106.30 | −0.5R | 4d | 🔴 |
| SPNT | $25.17→$25.68 | +0.4R | 22d | 🟢 |
| CON | $39.15→$39.09 | −0.0R | 4d | 🔴 |

Stats: 5 trades (W:2 L:3) · PF 0.79 · max DD 1.7% · Today +0.00%

## 📋 Summary — Entry Points & Active Decisions

| Ticker | Side | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|--------|------|------:|-----:|----:|----:|----:|:-------------:|------------------|:-------------:|
| ZS | 🔵 TRIM | $235–241 | $212 | — | — | 2.1 | EXIT SIGNAL | Trim 8–9/15, trail $217–221 | $0 (lock partial gains) |
| AMZN | 🔴 EXIT | $251.88 (close) | $245.33 | — | — | 0.7 | INVALIDATED | Exit all 10 @ open ~$252 | realize −$77 |
| BCC | 🟢 ENTRY | $82.18–80.25 | $76.22 | $88.43 | $88.43 | 3.9 | PRINTED (dip) | 3-expert @ Mon 04:30 DB run | $2,500 |
| GDDY | 🟡 ENTRY | $98.83–93.92 | $85.71 | $114.74 | $114.74 | 1.9 | NOT PRINTED | WAIT pullback | $2,500 |
| CRWV | 🔴 AVOID | $55.60 | $48.38 | — | — | — | knife | No entry — capitulation watch | — |

> Execution note: ZS/AMZN3-expert consensus above is live from today's expert run. Going forward, the DB job at04:30 produces this consolidated file each weekday with3-expert on every watchlist signal + exit — one report, one file, to this DM.
