# 📡 Entry Monitor Report — Tue 29 Sep 2026 03:00 ICT

**Run:** `monitor_entries.py` @ 03:00 ICT, US session **closed** (Mon 28 Sep, 16:00 ET close).
**Triggers:** MRVL = 🟢 UPTREND → 3-expert pipeline run. NVDU + ZS trailing → exit section.
**Not actionable:** GDDY 🔴 WAIT ($93.74, below SMA50 $96.27, structurally broken) · GEV ⚠️ BOUNCE ($949.69, needs reclaim >$970.74 with volume, currently 0.62×) · GOOG/RDDT/BCC/FBK/AMZN no signal.

---

## Actionable Entry Signals

### MRVL (Marvell) — pullback in markup, still no trigger

**Setup:** Closed **$251.90 (−3.88%)**, off the intraday low $248.14 — dipped *into* the fib zone top intraday then reclaimed it. Pullback from the 25 Sep swing high **$267.48** on **0.62× volume** (13.75M vs 20.1M avg) = supply absent, no SOW. Structure intact — HH/HL out of the Aug base: lows 162.90→200.62→213.63→235.96→244.99, highs 241.88→261.18→267.48. Price **above every SMA**: $248.97 (10) / $234.65 (20) / $221.83 (50) / $228.69 (100). ATR14 **$12.98**.

**60-day volume profile (fresh):** VPOC **$222.16** · Value Area **$204.73–$253.54** → price is **testing VAH from the edge**; the entry zone $231.45–$247.63 sits on top of the **$218.7–$239.6 HVN cluster (≈35% of 60d volume)** = acceptance support, not air.

| | |
|---|---|
| **Entry** | **$247.63–$231.45** (fib 38.2–50% of the $162.90→$300.00 leg) — limit in zone, OR SOS buy-stop above trigger-bar high. **Never market-buy.** |
| **Stop** | **$202.29** (monitor: fib 61.8 − ATR = thesis kill) · tight tactical **$226.90** (below SMA100 $228.69) · structural **$213.63** (09-14 shakeout low) |
| **TP1** | **$267.48** (prior 20d swing high) |
| **TP2** | **$300.00** (monitor TP / fib 100 / round number) |
| **R:R** | **1.6:1** → TP2 from mid-zone @ monitor stop · **4.8:1** @ tight stop · ⚠️ TP1 alone = **0.75R** @ monitor stop (needs >57% WR to pay) · breakeven WR @ monitor stop = **38.5%** |

**Expert panel:**

| Expert | Verdict | Score / basis |
|---|---|---|
| 🔢 **Thorp Edge** | **NO BET at full size** — small/paper only | **21/40**, confidence *medium-low*. Logical 3 (momentum + pullback-to-value, textbook) · **Statistical 1 (n=1, no backtest, no t-stat)** · Cost-adj 3 (≈0.1% round trip vs $37 risk — negligible, sign of p unverified) · Robustness 3 · Capacity 4 (ADV ~20M sh) · Backtest 2 · Paper 2 · R:R 3. **Kelly: p=50%→f=18.8%, p=45%→f=10.6% → half-Kelly 5–9% = $130–235 ≈ 0.5–1 share.** |
| 📊 **Wyckoff 2.0** | **ACCUMULATION CONFIRMED** — Phase E markup, trigger pending | Rising swing lows + SOS bars (09-17/21/22, 0.95–1.07× vol) out of the Aug base; current decline is a **low-volume Back-Up into the fib/HVN zone**, no SOW. Needs **SOS bar** (wide green, close upper third, ≥1× vol) → buy-stop above its high. **Alt scenario:** lose $247.63 on rising volume → $231.45 → $215.27 (fib 61.8) = failed markup, stand down. Caution: lower highs vs Jul $297.89 / Jun $329.88 — recovery, not new highs. |
| 🧬 **Medallion** | **WEAK SIGNAL** | **7/11 factors aligned**: uptrend regime · HH/HL · fib 38.2–50 retrace · zone inside 60d HVN cluster · volume contraction (0.62×) · RSI cooled to 62.7 · catalysts (MS PT $268, Seaport Buy, Oct 6 Investor Day). **But n=1, no t-stat, single asset, moderate fib-window overfit risk** — passes zero of the "multiple markets / multiple periods / cost-survival" checks. |

**Expert consensus: ⚠️ CONDITIONAL — limit order inside $247.63–$231.45 + SOS confirmation only.** Wyckoff structure is bullish, Thorp (21/40) and Medallion both flag zero statistical validation → size small, wait for the trigger, do not chase above the zone.

**Budget $2,500:** At monitor stop, full 10 sh ($2,476 @ zone top) risks **$453 (18.1%)** — breaches the 1% rule. **Strict 1%/half-Kelly = 0.5–1 sh ($130–250).** Practical plan: **start 5 sh ($1,240) only after the SOS fires, tight stop $226.90 = $207 (8.3%) max loss**, scale rest on hold above $253.54 (VAH).

**vs 28 Sep 22:00 run:** price 248.5–250.3 → **251.90 close** (reclaimed zone top), RSI 57–62 → 62.7, vol 0.34× → 0.62×. Setup **unchanged, still untriggered** — no SOS bar printed in the final hour.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **NVDU** | 📈 TRAILING — hold | — (trail **$133.88**) | **+62.5% (+$1,519.02, 27 sh @ $90.00)** | RSI 52.6→52.2, Stoch 81.1, mom +5, ATR $6.19, TP3 ∞. Floor locks ≥ **+$1,184.76** |
| **ZS** | 📈 TRAILING — hold | — (trail **$177.36**) | **+33.0% (+$742.50, 15 sh @ $150.00)** | RSI **70.7 (hot)**, Stoch 68.9, mom +5, ATR $11.07. Floor locks ≥ **+$410.40** |

Combined open: **+$2,261.52** on $4,680 deployed (**+48.3%**). Both trails hit → **≥ +$1,595.16 (+34.1%) locked**.

*vs 28 Sep 22:00 ICT run:* NVDU $146.75→$146.26 (−$13), ZS $197.41→**$199.50** (+$31) → net **+$18 in 5h, no exit triggered.**
⚠️ Trail is still **non-ratcheted** (NVDU floor fell $134.37→$133.88 as price dropped; ZS $175.53→$177.36 rose only because price rose). Fix (`max(prev, price − 2×ATR)`) **still pending your confirmation** — exit-logic change, not applied.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **MRVL** | $247.63–$231.45 | $202.29 (tight $226.90) | $267.48 | $300.00 | 1.6:1 | ⚠️ **CONDITIONAL** — zone + SOS only (Thorp **21/40** · Wyckoff ACCUM · Medallion WEAK) | 5 sh starter after SOS = $1,240 (8.3% risk @ tight stop); **Kelly/1% rule → 0.5–1 sh only** |

**Positions:** NVDU trail **$133.88** / ZS trail **$177.36** — both TRAILING, hold. **No other actionable signals.**
