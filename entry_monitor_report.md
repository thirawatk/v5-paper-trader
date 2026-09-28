# 📡 Entry Monitor Report — Mon 28 Sep 2026 22:00 ICT

**Run:** `monitor_entries.py` (pre-run 22:00 ICT), US session live (11:00 ET).
**Triggers:** MRVL = 🟢 UPTREND → 3-expert pipeline run. NVDU + ZS trailing hold → exit section.
**Silent:** GOOG, RDDT, BCC, FBK, AMZN — no signal.

---

## Actionable Entry Signals

### MRVL (Marvell) — pullback in markup

**Setup:** −4.4%→−5.1% today to ~$248.5–250.3 in a **sector-wide semi dip** (SMH −2.2%, AMD −5.3%, AVGO −1.1%; NVDA +2.3%; **no company-specific negative news found**). Structure intact: HH/HL since Jul (lows 162.9→201.7→211.1→213.6; highs 222.7→230.1→252.5→254.6→266.0), price **above ALL SMAs (20/50/100/200)** and above every 60-day HVN ($210/$220/$235). Pullback on **0.34× volume** = supply absent. Now at **fib 38.2% retrace** of the 3-month range ($162.90–$300.00).

| | |
|---|---|
| **Entry** | **$247.63–$231.45** (fib 38.2–50%) — limit in zone, OR SOS buy-stop above trigger-bar high |
| **Stop** | **$202.29** (monitor: fib61.8 − ATR = thesis kill) · tighter tactical **$226.90** (below fib50/SMA20 $234.60) |
| **TP1** | **$267.48** (prior swing high, 20d) |
| **TP2** | **$300.00** (3-month high = monitor TP) |
| **R:R** | **1.6:1** → TP2 from mid-zone @ monitor stop · **4.8:1** @ tight stop · ⚠️ TP1 alone = **0.75R** @ monitor stop (needs >57% WR to pay) |

**Expert panel:**

| Expert | Verdict | Score / basis |
|---|---|---|
| 🔢 **Thorp Edge** | **NO BET at full size** — small / paper only | **21/40**, confidence *medium*. Statistical significance **1/5** (n=1 signal, no backtest, no t-stat). Costs negligible (~0.1% round trip) → expectancy hinges entirely on unverified win rate. Kelly (assumed p=50%, RR=1.6) ≈ 19% full / **9.5% half-Kelly** — unreliable without a backtest |
| 📊 **Wyckoff 2.0** | **ACCUMULATION CONFIRMED** — markup Phase E, trigger pending | Back-up into fib38.2/HVN-top on 0.34× vol, no SOW. Needs **SOS bar** (wide green, close upper third, ≥1× vol) to fire. Alt scenario: lose $247.63 on rising volume → $231.45, then $215.27 |
| 🧬 **Medallion** | **WEAK SIGNAL** | 7 factors aligned (uptrend regime, fib retrace, HH/HL structure, >all HVNs, volume contraction, RSI cooled to 57–62, catalysts: MS PT $268 + Seaport Buy + Oct 6 Investor Day) — but **n=1, no t-stat**, moderate fib-window overfit risk |

**Expert consensus: ⚠️ CONDITIONAL — zone entry + SOS confirmation only; do NOT market-buy into the falling tape.** Wyckoff structure is bullish, but Thorp + Medallion both flag zero statistical validation → small size, wait for stabilization.

**Budget $2,500:** 10 sh = $2,476 @ zone top. Risk (10 sh): **$207** tight stop (8.4%) / **$453** monitor stop (18.3%). → **Start 5 sh (~$1,240) until SOS fires, then add.**

**Not actionable:** GDDY 🔴 WAIT ($94.56, below SMA50 $96.29) · GEV ⚠️ BOUNCE ($951.35, needs reclaim >$970.77 with volume — currently 0.24×).

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **NVDU** | 📈 TRAILING — hold | — (trail **$134.37**) | **+63.1% (+$1,532.25, 27 sh)** | RSI 52.6, mom +5, ATR $6.19, TP3 ∞. Floor locks ≥ **+$1,197.99** |
| **ZS** | 📈 TRAILING — hold | — (trail **$175.53**) | **+31.6% (+$711.15, 15 sh)** | RSI 70.0 (hot), mom +6, ATR $10.94. Floor locks ≥ **+$382.95** |

Combined open: **+$2,243.40** on $4,680 deployed (+47.9%). Both trails hit → **≥ +$1,580.94 (+33.8%) locked**.

*vs 21:01 ICT run:* NVDU $150.33→$146.75 (+67.0%→+63.1%), ZS $199.17→$197.41 (+32.8%→+31.6%) — **−$123 in the hour, no exit triggered.**
⚠️ Trail is still non-ratcheted: NVDU floor fell $137.95→$134.37, ZS $177.31→$175.53 as price dropped. Fix (`max(prev, price − 2×ATR)`) **still pending your confirmation** — exit-logic change.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **MRVL** | $247.63–$231.45 | $202.29 (tight $226.90) | $267.48 | $300.00 | 1.6:1 | ⚠️ **CONDITIONAL** — zone + SOS only (Thorp 21/40 · Wyckoff ACCUM · Medallion WEAK) | max 10 sh; **start 5 sh ($1,240)** |

**Positions:** NVDU trail $134.37 / ZS trail $175.53 — both TRAILING, hold.
