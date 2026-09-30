#!/usr/bin/env python3
REPORT = r'''# 📡 Entry Monitor Report — Wed 30 Sep 2026 21:01 ICT

## Actionable Entry Signals

### GOOG — 🟢 UPTREND (fib-dip entry)

**Setup:** Uptrend pullback into the 38.2–50% fib band. Price $347.78 sits *just below* the stated dip zone, so this is a **two-move scenario**: wait for the rally into $348.35–$356.25, then trigger.

| Level | Value |
|---|---|
| Entry zone | $348.35 – $356.25 (fib50 → fib38.2) |
| Trigger | Buy-stop above SOS bar high — needs a wide-range green bar on >1x volume. Not printed yet (Vol 0.20x) |
| Stop | $331.84 (fib618 − ATR, −4.6% from zone bottom) |
| TP1 | ~$366 (prior minor HVN / reclaim of prior breakdown) |
| TP2 | $381.81 (3m high = 1y VAH $380.76 — strong confluence) |
| R:R | 2.07:1 from zone bottom · 1.47:1 from zone mid · **1.07:1 from zone top** |

### Expert Panel — GOOG

| Expert | Verdict | Score / Key numbers |
|---|---|---|
| 🔢 **Thorp Edge** | **NO BET** (full size) | Scorecard **21/40** · backtest of this exact signal, 5y / 9 tickers, net 10bp: n=833, WR 52.2%, exp **+0.118R**, PF 1.24, t=2.91 (below the 3.0 bar), Kelly 10.2%, maxConsecLoss **24**. GOOG-only: n=94, WR 56.4%, exp +0.183R, PF 1.43, t=1.56, Kelly 16.9%. **2026 is negative — all-tickers PF 0.96 / GOOG PF 0.85, Kelly 0%**: edge has decayed this year. Portfolio sim 25.4% CAGR vs SPY 87% total (14.1% CAGR) but **maxDD 53.6%** |
| 📊 **Wyckoff 2.0** | **NEUTRAL** (markup intact, no trigger) | Phase E markup: 10d HH/HL vs prior 10d, price +2.3%/+1.7% over SMA20/50, 36.9% retrace of the $325.63→$359.98 leg (≈ fib38.2 test). Price **+4.5% above 1y VPOC $332.26** = acceptance, inside value area. BUT: OBV 60d slope **falling (−699k/day)**, CMF20 +0.022 (flat), Vol 0.20x, 4 distribution days/25 — **no SOS bar on this pullback**. HVN stack $339/$342/$345 supports; $355 HVN = first resistance |
| 🧬 **Medallion** | **WEAK SIGNAL** | Composite **+2.0 / ~10**. ✗ SMA stack bearish (339 < 341) · ✗ volume 0.20x (no initiative) · ✓ regime + fib touch + VPOC + RSI 62.5. t=2.91 pooled **< 3.0 bar**; GOOG t=1.56. Cross-market inconsistent: ZS PF 2.69, RDDT 2.27, BCC 1.64, GOOG 1.43 vs **MRVL 0.49, GDDY 0.69, FBK 0.91** — the signal is NOT uniform across assets → data-mining risk. Parameters standard (no curve-fit), but 2026 expectancy negative = edge decay |

**Expert Consensus: ⏳ WAIT — NO BET.** All three agree: trend is up, but there is no trigger (no SOS bar, no volume), the R:R at the top of the zone is only 1.07:1, and the signal's own 2026 expectancy is negative. Price must first reclaim $348.35–$356.25 on >1x volume before this becomes a trade.

**Budget $2,500:** $0 deployed. Would size at 1% risk = $25 → ~1.5 sh (~$546 notional) **only after** the SOS trigger prints.

---

## Exit Signals (Active Positions)

| Ticker | Action | Price | Entry | P&L | Stop / Trigger | Notes |
|---|---|---|---|---|---|---|
| **ZS** | 🎯 **TAKE PROFITS** | $198.52 | $150.00 | **+32.3% ($+727.80)** | trail $166.02 | TP2 ($176.70 / 2.5R) hit and price ran past it. Momentum NEUTRAL (+1), **MACD bearish (hist −0.2)**, RSI 70.6. Close or trim ≥50%, trail the rest |
| **NVDU** | 📈 TRAILING — hold | $150.50 | $90.00 | **+67.2% ($+1,633.50)** | $137.78 (2×ATR) | Uptrend, momentum STRONG (+4), RSI 66.3, Stoch 96.0 (hot). TP1/TP2 exceeded → TP3 ∞, let it run |

Combined open P&L: **+$2,361.30**. One action: realize ZS, keep trailing NVDU.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| GOOG | $348.35–$356.25 **only after SOS bar >1x vol** | $331.84 | $366 | $381.81 | 2.07:1 | ⏳ WAIT (Thorp 21/40 · Wyckoff NEUTRAL · Medallion WEAK) | $0 — not deployed |
| GDDY | — | — | — | — | — | 🔴 NO TRADE | — |
| GEV | $966.10 (on SMA50 reclaim) | — | — | — | — | ⏳ WAIT | — |
| ZS | (exit) | — | — | — | — | 🎯 TAKE PROFITS | in position |
| NVDU | (hold) | $137.78 | — | — | — | HOLD / trail | in position |

**Action:** No new capital deployed. Wait for a GOOG SOS bar above $356.25 on volume; take ZS profits; trail NVDU at $137.78.

---
*Backtest: `_goog_experts.py` → `_goog_expert_out.txt` (5y, 9 monitor tickers, net 10bp RT costs). Signal replicated exactly as the monitor emits it.*
'''

with open('/root/.hermes/profiles/trader/scripts/entry_monitor_report.md', 'w') as f:
    f.write(REPORT)
print('WROTE', len(REPORT), 'chars')
