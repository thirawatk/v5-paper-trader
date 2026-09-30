# 📡 Entry Monitor Report — Wed 30 Sep 2026 22:01 ICT

## Actionable Entry Signals

### GOOG — 🟢 UPTREND (fib-dip)

**Setup:** Uptrend pullback toward the 38.2–50% fib band. Price **$343.61 sits ~1.4% BELOW the stated dip zone**, so this is a **two-move scenario**: price must first rally back into $348.35–$356.25, then print a trigger. No entry today.

| Level | Value |
|---|---|
| Entry zone | $348.35 – $356.25 (fib50 $348.12 → fib38.2 $356.02) |
| Current price | $343.61 — *outside* the zone (below it) |
| Trigger | Buy-stop above SOS bar high — wide-range green bar on **>1x volume**. Not printed (0.39x) |
| Stop | $331.84 (fib618 $340.23 − ATR $8.19, −4.6% from zone bottom) |
| TP1 | $356 (3m VAH $355.88 + 206M HVN — first magnet, trim point) |
| TP2 | $381.81 (3m high $381.56 ≈ 1y VAH $380.76 — strong confluence) |
| R:R | **2.08:1 from zone bottom** · 1.47:1 zone mid · 1.07:1 zone top · 3.02:1 if bought at market now |
| Breakeven WR | 32.5% at zone bottom · 48.4% at zone top |

### Expert Panel — GOOG

| Expert | Verdict | Score / Key numbers |
|---|---|---|
| 🔢 **Thorp Edge** | **NO BET** (full size) | Scorecard **22/40** → "paper trade only" band. Backtest of this exact signal, 5y / 9 monitor tickers, net 10bp RT: **n=833, WR 52.0%, exp +0.117R, PF 1.24, t=2.89** (below the 3.0 bar), Kelly 10.1%, maxConsecLoss **24**. GOOG-only: n=94, WR 54.3%, exp +0.171R, PF 1.40, t=1.46, Kelly 15.4%. **2026 is negative** — all-tickers PF 0.96 / GOOG PF 0.73 (exp −0.134R, Kelly 0%). Portfolio sim: 2.80x over 4.57y (CAGR 25.2% vs SPY 1.87x / 14.1%) **but maxDD 53.6%** — beats the index on return, fails it on risk |
| 📊 **Wyckoff 2.0** | **NEUTRAL** (markup intact, no trigger) | Phase E markup: 10d HH/HL vs prior 10d, price +1.5%/+0.9% over SMA20/50, **45.5% retrace** of the $325.63→$359.98 leg (≈ fib50 test). Price **+3.6% above 1y VPOC $332.26** = acceptance, inside value area, sitting right on **3m VPOC $343.06** (+0.4%). BUT: OBV 60d slope **falling (−695k/day = distribution)**, CMF20 +0.011 flat, vol 0.39x, 4 distribution days/25, price **−2.6% below SMA100** — **no SOS bar on this pullback**. HVN support $339/$342/$345 (~610M combined); first wall $355 HVN + 3m VAH $355.88 |
| 🧬 **Medallion** | **WEAK SIGNAL** | Composite **+2.0 / ~10**. ✗ SMA stack bearish (339 < 341) · ✗ volume 0.39x (no initiative) · ✓ regime + fib touch + VPOC + RSI 53.0 cool. Pooled **t=2.89 < 3.0 bar**; GOOG t=1.46. Cross-market inconsistent: ZS PF 2.69, RDDT 2.27, GEV 1.86, BCC 1.64, AMZN 1.60, GOOG 1.40 vs **FBK 0.91, GDDY 0.69, MRVL 0.49** — signal is NOT uniform across assets → data-mining risk. Standard parameters (no curve-fit), but 2026 expectancy negative = edge decay |

**Expert Consensus: ⏳ WAIT — NO BET.** All three agree: the trend is up, but price is *outside* the entry zone, there is no trigger (no SOS bar, no volume), R:R at the top of the zone is only 1.07:1, and the signal's own 2026 expectancy is negative. Flip condition: **reclaim $348.35–$356.25 with an SOS bar on >1x volume**.

**Budget $2,500:** **$0 deployed.** Would size at 1% risk = $25 → 1.0–1.5 sh ($370–$530 notional) **only after** the SOS trigger prints.

---

## Exit Signals (Active Positions)

| Ticker | Action | Price | Entry | P&L | Stop / Trigger | Notes |
|---|---|---|---|---|---|---|
| **ZS** | 🎯 **TAKE PROFITS** | $200.79 | $150.00 | **+33.9% ($+761.85)** | trail $166.09 | TP2 ($176.82 / 2.5R) hit and price ran **+13.6% past it**. Momentum NEUTRAL (+1), **MACD bearish (hist −0.06)**, RSI 71.3. Close ≥50%, trail the rest |
| **NVDU** | 📈 TRAILING — hold | $148.99 | $90.00 | **+65.5% ($+1,592.73)** | $136.23 (2×ATR) | Uptrend, momentum STRONG (+4), RSI 65.2, Stoch 90.7 (hot). TP1/TP2 exceeded → TP3 ∞, let it run |

Combined open P&L: **+$2,354.58**. One action: **realize ZS**, keep trailing NVDU.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| GOOG | $348.35–$356.25 **only after SOS bar >1x vol** | $331.84 | $356 | $381.81 | 2.08:1 | ⏳ WAIT (Thorp 22/40 · Wyckoff NEUTRAL · Medallion WEAK) | $0 — not deployed |
| GDDY | — | — | — | — | — | 🔴 NO TRADE (downtrend) | — |
| GEV | $965.87 (on SMA50 reclaim) | — | — | — | — | ⏳ WAIT (bounce risky) | — |
| ZS | (exit) | — | — | — | — | 🎯 TAKE PROFITS | in position |
| NVDU | (hold) | $136.23 | — | — | — | HOLD / trail | in position |

**Action:** No new capital deployed. Wait for GOOG to re-enter $348.35–$356.25 with an SOS bar on >1x volume; **take ZS profits**; trail NVDU at $136.23.

---
*Backtest: `_goog_experts.py` → `_goog_expert_out.txt` (5y, 9 monitor tickers, net 10bp RT costs; signal replicated exactly as the monitor emits it). Data note: tvDatafeed timed out twice this run — prices fell back to secondary feed.*
