# 📡 Entry Monitor Report — Thu 08 Oct 2026 22:00 ICT

*3-Expert pipeline: Thorp Edge · Wyckoff 2.0 · Medallion Pattern — from monitor_entries.py (22:00 ICT run)*

## ⏱️ Data Caveat — Mid-Session Run

US market is LIVE (22:00 ICT = 11:00 ET, ~30% of session elapsed). **No daily close has printed**, so every close-confirmation trigger is structurally NOT PRINTED this run. Vol ratios are partial-day cumulative; projected full-day ≈ **0.5–0.8×20d across the board** — still no initiative volume anywhere.

## Key Changes Since 21:00 Run

- **GEV back INSIDE the band** — $1012.31 in $1004.62–1036.80 (was $1001.34 below) → closest to trigger
- **RDDT + AMKR are NEW conditional signals** (SMA50 reclaim / SMA20-50 cluster test); AMZN entry section retired — now a position, entry alerts suppressed, no exit alert
- **ZS printed a NEW 3M high $218.48 intraday** (broke $216.97); trail ratcheted to $198.67
- **All 11-factor gates refreshed: 0/7 pass** (range −0.18 … +0.29, need ±0.50)

## 🟢 Entry Triggered

**None — no confirmation triggers printed this run.**

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG

- **Setup:** UPTREND, 5d 0🔴/5🟢 (momentum intact) — but price $348.13 sits **$0.22 BELOW band bottom** ($348.35), testing SMA100 $350.81 from below; vol 0.26x partial (proj ~0.8x), RSI 53.4
- **Trigger needed (NOT printed):** daily close ≥ $348.35 into the band on full-day vol ≥1.0x with SOS bar (wide-range green, upper-third close); reclaim of SMA100 $350.81 strengthens it
- **Planned levels:** entry $348.35–356.25 · stop $332.02 · TP $381.81 (3m high) · **R:R 2.05:1** at band bottom · 1 sh = $348, risk $16.33 = 0.65% ✓
- **11-factor gate:** +0.29 FAIL
- **Backtest:** pooled fib-dip n=837 t=3.04 ✓; GOOG-only n=96 t=1.60 ✗; 2026 PF 0.92; portfolio 2.95× / CAGR 26.7% vs SPY 97.1% same window, maxDD 53.6%

| Expert | Verdict | Key note |
|---|---|---|
| 🔢 Thorp | **NO BET — 24/40** | GOOG-only t=1.60 (<3.0), 2026 PF 0.92, gate +0.29 FAIL, maxDD 53.6% > cap. Port CAGR 26.7% vs SPY 97.1% → fails ultimate question. |
| 📊 Wyckoff | **NEUTRAL** | Price below SMA100 $350.62 (−0.4%, overhead). CMF20 worsened to −0.089, vol 0.28x, no SOS. **Positive: OBV 60d flipped RISING +144k/day** (was −54k at 03:00). 1y VPOC $332.26 below. |
| 🧬 Medallion | **WEAK — 0.0** (was +2.0 @03:00) | ✓ regime, ✓ above VPOC, ✓ 0R/5G week; ✗ SMA100, ✗ stack 20<50, ✗ vol 0.28x. Composite decayed to zero. |

**Consensus: WAIT — no entry.** Price still outside band, SMA100 overhead, gate fails, no volume. Budget: $0.

---

### RDDT *(new signal this run)*

- **Setup:** 🟢 UPTREND + "🚀 reclaimed SMA50 $154.40" (+2.34%) — **BUT price $156.29 is below the entire fib band ($171.11–179.58) and only $0.41 above the verdict stop $155.88**. Pullback ran deeper than the 61.8% level; vol 0.20x, RSI 55.4, 5d 2🔴/3🟢
- **Trigger needed (NOT printed):** two-move scenario — (1) price reclaims back INTO the band, (2) green close inside $171.11–179.58 on ≥1x vol. **Invalidation: close < $155.88**
- **Planned levels (valid ONLY from band):** entry $171.11–179.58 · stop $155.88 · TP $207.00 · R:R 2.36:1 at band bottom. **At current price entry would be $0.41 above the stop — nonsense R:R, do not enter**
- **11-factor gate:** +0.01 FAIL
- **Backtest:** RDDT-only fib-dip n=30, WR 63.3%, PF 2.27, **t=2.15 ✗ — sample below the 100-trade minimum**

| Expert | Verdict | Key note |
|---|---|---|
| 🔢 Thorp | **NO BET — 22/40** | n=30 < 100 min sample, t=2.15 <3.0, gate +0.01, entry-at-stop structure. Logical 2 · Stat 2 · Cost 3 · Robust 3 · Cap 4 · Integ 3 · Paper 2 · R/R 3. |
| 📊 Wyckoff | **NEUTRAL — bounce inside markdown** | CMF20 **−0.151 (worst in batch)**, OBV −2.05M/day = distribution, 30d up/down vol 0.55, LH/LL structure, 3m VPOC $177.45 sits 7% overhead (inside band = magnet + supply). Positives: SMA50 reclaim, today's close in upper third (+68% range). |
| 🧬 Medallion | **WEAK — 0.0** | ✓ regime, ✓ above 1y VPOC (+12%); ✗ stack 20<50, ✗ SMA100 (−5.1%), ✗ vol 0.20x. |

**Consensus: WAIT — no entry.** Setup invalid until price re-enters the band; distribution footprints dominate. Budget: $0.

---

### GEV *(closest to trigger — price back in band)*

- **Setup:** price $1012.31 (+1.53%) **INSIDE Fib band $1004.62–1036.80** ✓, RSI 70.5 (hot), vol 0.25x partial (proj ~0.8x), 5d 1🔴/4🟢
- **Trigger needed (NOT printed):** TODAY's **green close ≥ $1004.62 on full-day vol ≥1.0x (SOS bar)**. Invalidation: close < $997 (SMA100) → stand aside
- **Planned levels:** entry $1004.62–1036.80 · stop $937.75 · TP $1140.99 · **R:R 2.04:1** at band bottom
- **⚠️ Sizing blocker:** 1-share minimum = $1,012 notional, risk $66.87–70.48 = **2.7% of $2,500 > 1% cap — cannot size within risk limits even if trigger prints**
- **11-factor gate:** +0.07 FAIL
- **Backtest:** GEV-only n=34 t=1.62 ✗; 2026 PF 0.74, H2 PF 0.86 vs H1 PF 3.60 (decayed)

| Expert | Verdict | Key note |
|---|---|---|
| 🔢 Thorp | **NO BET — 22/40** | t=1.62 <3.0, 2026 PF 0.74, gate +0.07, min-size breaches 1% risk cap. Port: 31.0% GEV-window vs SPY 97.1% full-window. |
| 📊 Wyckoff | **NEUTRAL — structure improved** | Reclaimed band + SMA100 (+1.1%), OBV rising +123k/day, HH/HL markup, 30d up/down 2.0. But CMF20 flat 0.000, vol 0.31x = no confirmation, 3m VPOC $985.88 still a magnet below. |
| 🧬 Medallion | **WEAK — +2.0** | ✓ regime, ✓ SMA100, ✓ band touch, ✓ >1y VPOC (+74%); ✗ stack 20<50, ✗ vol 0.25x. |

**Consensus: WAIT — no entry.** Price is in the zone but nothing confirms: no close, no volume, gate fails, and 1-share sizing violates the risk cap anyway. Budget: $0.

---

### MKSI *(swing plan MKSI-SW-1)*

- **Setup:** price **$273.18 IN zone $255–274 ✓ (zone top)**, testing SMA50 $274.31 from below, RSI 69.8 (chase-danger zone — plan: never lump at zone top), vol **0.15x = weakest in batch** (proj ~0.5x), regime BOUNCE
- **Gate:** 11-factor composite **+0.12 FAIL** (need ≥ +0.50) — unchanged since 03:00
- **Trigger needed (NOT printed):** gate ≥ +0.50 while in zone, OR daily close > $311 (SMA100 breakout)
- **Planned levels:** 1 sh ≈ $271 notional · SL fill − $19.78 → $251.48 · TP1 $300.93 (1.5R) · TP2 $320.71 (2.5R) · risk $19.78 = **0.79% ✓** · time stop 2–4wk · no averaging
- **Backtest:** MKSI-only n=58, WR 63.8%, +0.522R, PF 2.42, **t=3.08 ✓ (clears Renaissance bar — best stats in this batch)**; H2 decayed (n=29 t=0.75); 2026 PF 0.00 / 2025 PF 9.71 / 2024 PF 0.21

| Expert | Verdict | Key note |
|---|---|---|
| 🔢 Thorp | **CONDITIONAL — WAIT FOR GATE (25/40)** | Setup-class t=3.08, PF 2.42 — best signal statistically. But gate +0.12 < 0.50 = hard block; 2026 PF 0.00. On pass: 1 sh sizing ✓. Scorecard: Logical 2 · Stat 4 · Cost 3 · Robust 3 · Cap 4 · Integ 3 · Paper 2 · R/R 4. |
| 📊 Wyckoff | **NEUTRAL — accumulation, unconfirmed** | Real accumulation footprints: CMF20 **+0.228**, OBV +164k/day rising, 30d up/down 1.90, only 1 distribution day, HH/HL. But vol 0.15x = zero initiative, below SMA50 −1.1% and SMA100 −12.6%, 3m VPOC $290 overhead. |
| 🧬 Medallion | **NOISE — −2.0** (was −1.0) | ✗ regime (px < SMA50), ✗ stack 20<50, ✗ SMA100, ✗ vol 0.15x; ✓ neutral RSI, ✓ >VPOC, ✓ 2R/3G. |

**Consensus: WAIT — zone right, gate not passed.** Only signal clearing t>3.0, but +0.50 gate reads +0.12 and volume is the batch's weakest. Budget: $0.

---

### AMKR *(new signal this run)*

- **Setup:** 🟢 UPTREND, price $52.16 sitting ON the SMA20/50 cluster ($51.86 / $51.68), RSI 55.2 (**need <50 per monitor confirms**), Stoch 13.4, vol 0.19x, 5d 4🔴/1🟢
- **Trigger needed (NOT printed):** monitor confirms = **RSI <50 + green close**; alternate plan trigger = full-day close ≥$52.60 on ≥1x vol. Today's intraday high $52.72 **tagged the $52.60 buy-stop but on 0.20x volume and price retreated below** — a live fill would be −1.3%, which is exactly why the vol≥1x requirement exists
- **Planned levels:** entry $51.68 (cluster dip) · stop $48.12 · TP1 $54.02 · TP2 $57.53 · **R:R 0.66:1 to TP1 (uneconomic alone) / 1.64:1 to TP2** · sizing ~7 sh ($362), risk $24.9 = 1.00% ✓
- **11-factor gate:** **−0.18 FAIL** (worsened from −0.08 at 03:00)
- **Backtest:** AMKR-only fib-dip n=91, WR 70.3%, +0.776R, PF 3.14, **t=5.32 ✓✓ — strongest single-name in the pool**; H2 t=8.31; caveat 2026 only n=3

| Expert | Verdict | Key note |
|---|---|---|
| 🔢 Thorp | **BET (small) — but GATED; 24/40** | t=5.32 ✓✓ setup class, Kelly 48% → 1% cap binds. But gate −0.18 FAIL + trigger 0/3 → no execution. Sizing ✓ on pass. |
| 📊 Wyckoff | **NEUTRAL — cluster test, distribution undertone** | On SMA20/50 cluster from above; but MFI 38.9 weak, OBV falling −407k/day, CMF +0.061 flat, 30d up/down 0.95, below SMA100 −15.8%, vol 0.19x. 10d HH/HL only positive. |
| 🧬 Medallion | **WEAK — +1.0** | ✓ regime, ✓ stack 20>50, ✓ >VPOC; ✗ SMA100 (−15.8%), ✗ vol, ✗ 5d 4R/1G. |

**Consensus: WAIT — no entry.** Best backtest in the batch (t=5.32) but gate negative, RSI not cooled, no green close, no volume. Budget: $0.

---

## Exit Signals (Active Positions)

| Ticker | Action | Mark | P&L | Notes |
|---|---|---|---|---|
| **ZS** | 📈 **HOLD + TRAIL** | $217.25 | **+44.8% (+$1,008.67)** | 15 sh @ $150. **NEW 3M HIGH $218.48 printed today** (broke $216.97). Trail SL **$198.67** (2×ATR $9.29). StochK 94–96 extreme overbought; MACD hist +0.598 intact; RSI 64–66. Medallion +4.5 POSITIVE (trend strongest in batch). 6 distribution days — watch for a wide-range red bar at the high. TP1/TP2 already exceeded; TP3 runner on trail. **Optional: trim 5 sh into $216.97–218.48 resistance → realize ~+$336, remaining 10 sh trail locks min +$487** |
| **AMZN** | ✅ **NO SIGNAL — hold** | $259.37 | −0.07% (−$1.76) | 10 sh @ $259.55. SL $249.33 (2×ATR) intact, RSI 57.6, above SMA20/50, MACD not bearish → no exit alert this run |

**Open positions: ZS + AMZN · combined open P&L: ≈ +$1,006.91 (unrealized)**

---

## Not Routed This Run

- **ACMR** 🔴 WAIT — $72.53 (−0.33%), 5d 5🔴/0🟢, below ALL SMAs ($74.14/$76.45/$83.59), Stoch 13.4. Needs green close > SMA20 $74.14. Per routing rules: 🔴 WAIT/DOWNTREND = not routed.
- **GDDY, BCC, FBK, MRVL, OPEN** — no signals this run.
- **NVDU** — fully closed Oct 7 (+$1,903.21 realized).
- **AMZN** — now a position; entry alerts suppressed (exit check ran → no alert).

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| GOOG | $348.35–356.25 (close in band, ≥1x vol) | $332.02 | — | $381.81 | 2.05 b.b. | **NOT PRINTED** — $0.22 below band, vol 0.26x partial | **WAIT** (NO BET 24/40 · NEUTRAL · WEAK 0.0) | $0 |
| RDDT | $171.11–179.58 (reclaim into band first) | $155.88 | — | $207.00 | 2.36 b.b. | **NOT PRINTED** — price BELOW band, $0.41 above stop | **WAIT** (NO BET 22/40 · NEUTRAL · WEAK 0.0) | $0 |
| GEV | $1004.62–1036.80 (green close ≥$1004.62, ≥1x vol) | $937.75 | — | $1140.99 | 2.04 b.b. | **NOT PRINTED** — IN band, awaiting close+vol (0.25x) · ⚠️ 1sh = 2.7% risk > cap | **WAIT** (NO BET 22/40 · NEUTRAL · WEAK +2.0) | $0 |
| MKSI | $255–274 (gate ≥+0.50) | ~$251.48 (fill−19.78) | $300.93 (1.5R) | $320.71 (2.5R) | 1.5R / 2.5R | **NOT PRINTED — GATE +0.12 FAIL** | **WAIT** (COND 25/40 · NEUTRAL · NOISE −2.0) | $0 |
| AMKR | $51.68 cluster (RSI<50 + green close) | $48.12 | $54.02 | $57.53 | 0.66 / 1.64 | **NOT PRINTED** — RSI 55.2, red day, vol 0.19x, gate −0.18 | **WAIT** (BET-gated 24/40 · NEUTRAL · WEAK +1.0) | $0 |
| ACMR | 🔴 WAIT (downtrend) | — | — | — | — | **NOT ROUTED** | — | $0 |
| ZS | (holding) | $198.67 trail | — | — | — | TRAILING +44.8%, new 3M high | Hold, TP3 run · optional trim 5sh @resistance | pos +$1,009 |
| AMZN | (holding) | $249.33 | — | — | — | NO SIGNAL | Hold | pos −$2 |

**This run: 0 triggers printed · 5 conditional setups (GOOG, RDDT, GEV, MKSI, AMKR) · 1 trailing alert (ZS) · 1 position quiet (AMZN) · capital deployed: $0.**

**Panel notes:**
- **Mid-session run:** no daily closes + all vol ratios partial-day → close-confirmation triggers cannot print before the 03:00 ICT close. Projected full-day volume 0.5–0.8×20d — no initiative volume anywhere.
- **All 11-factor gates FAIL: 0/7** (−0.18 to +0.29 vs ±0.50 threshold). The gate is the binding constraint across the whole batch.
- **GEV is closest to a trigger** (price back in band) but even if it closes green ≥$1004.62: gate +0.07 fails AND the 1-share minimum risks 2.7% > the 1% cap — structurally untradeable at this budget.
- **MKSI + AMKR have the best statistics** (t=3.08 PF 2.42 / t=5.32 PF 3.14) — both blocked by gates (+0.12 / −0.18). Strongest setups, no permission to execute.
- **RDDT is the weakest read:** price below its whole entry band and $0.41 above its stop, CMF −0.151, OBV distribution, n=30 sample. A "reclaim" alert inside a broken structure.
- **ZS at extremes:** new 3M high, StochK 94–96, Medallion +4.5 but 6 distribution days. Trail $198.67; optional 5-sh trim into $216.97–218.48 on a wide-range red bar.
- **Thorp ultimate question fails all:** portfolio sim 26.7% CAGR vs SPY 97.1% (same 4.57y window), maxDD 53.6%.

---

*Entry Monitor 3-Expert Pipeline · monitor_entries.py + Thorp Edge / Wyckoff 2.0 / Medallion Pattern · backtests on completed Oct-7 bar (`_goog_expert_out.txt`, `_gev_expert_out.txt`, `_mksi_amkr_expert_out.txt`) + fresh 22:00 gate/Wyckoff/Medallion refresh (`_entry_2200_expert_out.txt`) · 11-factor gates via `confluence_score.py` · 08 Oct 2026 22:00 ICT*
