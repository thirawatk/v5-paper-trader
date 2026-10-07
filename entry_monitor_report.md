# 📡 Entry Monitor Report — Wed 07 Oct 2026 21:00 ICT

**US open run** (market open ~90 min: 21:00 ICT = 10:00 ET). All prices below are **intraday** — volume ratios (0.06–0.14x) are partial-session, volume-based triggers must be judged at the daily close. Expert backtests unchanged (last run 03:02 ICT on the completed Oct-6 bar; no new completed bar since).

**Routing:** GOOG + GEV carry 🟢 verdicts but price is *below* the entry band → conditional, not triggered. AMZN ⚠️ partial confirmation. MKSI ⏳ but price is **inside the plan's T2 zone** → routed.

## 🟢 Entry Triggered

**None — no confirmation triggers printed this run.**

---

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG — below band, SMA100 overhead, no SOS
- **Setup:** $343.11 (-0.43%) · RSI 49.5 · vol 0.14x · 5d 2🔴/3🟢. Above SMA20 $340.89 / SMA50 $342.84 by a whisker, **2.4% below SMA100 $351.22** — monitor's "testing SMA100 support" line is stale, it's overhead supply. 1y: -14.0% off $398.54. Price sits **right at the 90d VPOC $341–343** = acceptance node; 20d up/dn vol 339M/308M (1.10).
- **Trigger needed (NOT printed):** green close **into $348.35–$356.25**, then SOS bar (upper-third close) on **>1.0x daily volume** → buy-stop above its high.
- **Levels:** band $348.35–356.25 · stop $331.86 · TP $381.81 · R:R **1.05 (band top) – 2.03 (band bottom)**

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — 24/40** | Pooled fib-dip signal 5y/9 tickers net 10bp: **n=836, WR 52.2%, +0.122R, PF 1.25, t=3.03 ✓**, Kelly 10.5%, maxConsecLoss 24. GOOG-only n=95, t=1.47 ✗; **2026 GOOG PF 0.74** (decay). Portfolio sim 26.4% CAGR beats SPY ≈14.4%/yr same window — but **maxDD 53.6%** blows the 25% cap |
| 📊 Wyckoff 2.0 | **NEUTRAL** — markup intact, no trigger | Above 1y VPOC $332.26 (+3.7%). But OBV 60d **falling (−213k/day)**, CMF20 −0.048, 4 distribution days/25, −2.4% under SMA100, no SOS. HVN $339–345 supports (price inside); **LVN $348 = band bottom thin**; $355 HVN first resistance |
| 🧬 Medallion | **WEAK SIGNAL** | Composite **+2.0/10** (✓ regime, ✓ at VPOC; ✗ SMA stack 20<50, ✗ vol, ✗ no momentum burst). GOOG t=1.47 ✗ vs t>3.0 bar; 2026 negative = decay → data-mining risk |

- **Consensus: WAIT — no entry.** Price below band, SMA100 lost, no SOS.
- **Budget $2,500:** $0 now. On print at band bottom: 1% risk = $25 → **1 share** ($16.6 = 0.66%) ✓.

### AMZN — MACD confirmation fired, SMA50 gate still not reclaimed
- **Setup:** $255.36 (-0.36%) · RSI 56.2 · vol 0.12x · 5d 3🔴/2🟢. At the fib-pullback zone's lower edge ($256.68 ±1%) and above SMA20 $251.4, **MACD hist +0.81 fired — one of the two approved-plan confirmations** ✓ — but price is still **below the SMA50 gate $257.92** ✗.
- **Trigger needed (NOT printed):** daily close **> $257.92 (SMA50) on >1.0x volume**.
- **Levels:** entry $257.92 · stop $246.33 · risk $11.59 (4.5%) · TP1 $267.56 (**0.83R**) · TP2 $280.72 (**1.97R**)

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — 19/40** | Exact SMA50-reclaim trigger Variant B (+vol>1x): **n=85, WR 37.6%, +0.070R, PF 1.10, t=0.42** ✗, Kelly 3.5%. AMZN-only B n=14 +0.422R but t=0.97; **2026 AMZN 0/3 (PF 0.00)**. Portfolio B: **+6.8% total (1.5% CAGR) over 4.5y vs SPY +86.2%** → fails the ultimate question decisively |
| 📊 Wyckoff 2.0 | **ACCUMULATION — NOT CONFIRMED** | 49% of the 60d range $226–287 = balance, not trend. Under SMA50 supply; OBV 60d falling (−7.6M/day), 30d up/dn 0.80, no initiative buying. Needs real SOS close >$257.92 >1x vol, then Back-Up. Failure of $244.73 → failed accumulation |
| 🧬 Medallion | **NOISE** | Composite **+1.0/10**; t=0.42 ≪ 3.0 bar; H1 43% vs H2 33% deteriorating; mid-range = balance. Single-name textbook pattern = highest overfit risk |

- **Consensus: WAIT — gate not printed, and the trigger family itself has no demonstrated edge.**
- **Budget $2,500:** 2 sh = $22 risk (0.9%) sizing-compliant — but NO BET → **$0**.

### GEV — band trigger FAILED intraday; SMA100 lost
- **Setup:** $988.32 (**-3.97%**) · RSI 67.1 · vol 0.13x. Oct-6 close printed inside the band ($1,029.34, 1.19x vol) — but today's session broke **down through band bottom $1,004.62 AND below SMA100 $997.47**, the exact "failure < $998.38 kills it" line from the expert run. Now testing **3m VPOC $985.88**.
- **Trigger needed (restart):** reclaim $997.47 (SMA100) → then band bottom $1,004.62 on >1x volume; prior gate $1,052.78 still overhead. Below: fib61.8 $972.44 → SMA50 $966.10 → 3m VAL $899.
- **Levels (unchanged):** band $1,004.62–1,036.80 · stop $939.44 · TP $1,140.99 · R:R 1.07–2.09

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — 19/40** | GEV-only fib-dip: **n=33, WR 66.7%, +0.333R, PF 1.99, t=1.89** < 3.0 bar. **2026 GEV PF 0.94** (negative); H2 decayed (PF 1.18 vs H1 3.41). Sizing fails the cap: 1 sh = **3.6% risk** > 1% ✗. At-band R:R ≈ coin flip |
| 📊 Wyckoff 2.0 | **Gate rejection → structure broken intraday** | Oct-6 $1,052.78 gate rejected to the tick, today lost band + SMA100 → distribution risk now outweighs the Phase-E accumulation read. Alternative scenario (band-bottom retest $1,004.62) also failed. **Stand aside until reclaim** |
| 🧬 Medallion | **STRONG but underpowered → downgraded** | Composite was +5.0/10, but t=1.89 ✗ and 2026 PF 0.94; positive confluence is not a deployable signal once structure fails |

- **Consensus: NO BET / WAIT — stronger than the 20:00 run.** Structure now actively failing; only a reclaim of $997→$1,005 revives it.
- **Budget $2,500:** $0.

### MKSI — T2 ZONE HIT (plan tranche), SOS trigger not printed
- **Setup:** $271.20 (**-3.63%**) · RSI 73.1 (cooled from 87.3) · Stoch 65 · vol 0.06x intraday · 5d 1🔴/4🟢 (today red). **Price is INSIDE the plan's T2 zone $255–274** and testing SMA50 $273.96; SMA20 $259.98 below. Plan status **PLANNED — no tranche filled**; T1 ref $281.41 → price now 3.7% *below* the anchor reference.
- **Trigger needed (NOT printed):** SOS bar (wide-range green, upper-third close) on expanding volume while higher-low holds >$228.46 → **buy-stop above its high** (never market-buy the knife). Today is a red knife — no SOS. Early warning: daily close <$261 → skip T3. **Kill: weekly close <$228.46.**
- **Planned levels:** T2 zone $255–274 (Thorp cluster $261–268) · kill $228.46 · T3 confirm daily >$311 / weekly >$322 · plan 3 sh ≈ $857, cap 4 sh

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **STAGED ENTRY** (panel Oct 7) | Scenario-weighted EV +8.3%/18mo (+5.5%/yr) → **fails "better than the index" vs SMH** as core; satellite only. Full Kelly 16% = 1.4 sh; neutral gate → half-Kelly anchor. Entry timing *less* negative now than the $281 panel snapshot — pullback delivered the zone |
| 📊 Wyckoff 2.0 | **EARLY ACCUMULATION, UNCONFIRMED** — pullback zone ON PLAN | Primary entry = low-volume pullback to **$255–274 holding >$228.46 → buy-stop above SOS** — price walked into it today. Needs low-volume higher-low hold; heavy-vol stall $286–322 then loss $255 = redistribution → stand aside. Targets $380.50 → $447 |
| 🧬 Medallion | **NOISE** | No validated 12–24mo edge (n=1–2 independent obs at 35% ann vol); "buy the -40% drawdown recovery" = narrative. If exposure wanted: **stage, never lump** — agrees mechanically |

- **Consensus: CONDITIONAL BUY — zone condition met, SOS trigger not printed.** The only setup sitting *in* its entry zone this run; today's red knife means buy-stop discipline applies.
- **Budget $2,500:** if initiating fresh, T1 anchor + T2 both eligible at $271 (below T1 ref) → **2 sh ≈ $543** on SOS print; cap 4 sh; park remainder SMH/SOXX. Funding ready: NVDU trim $2,284.80 realized.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **NVDU** (13 sh runner) | **HOLD + TRAIL $149.54** | $158.42 | **+76.0%** ($+889.46 open) | Monitor "TP2 $108.72" is entry-based/stale — position is at **~11R**, deep past TP3 in trailing mode. RSI 79.1 overbought, -6.8% off 3M high $170.20. Trail $149.54 (2×ATR) — **never lower**; fail-safe red close < $155. 14 sh already trimmed @ $163.20 Oct 6 → +$1,024.80 realized |
| **ZS** (15 sh) | **TRIM 5–8 sh near $216.97 + TRAIL $193.03** | $211.53 | **+41.0%** ($+922.95 open) | Monitor trail $192.87 ≈ journal $193.03 — keep the higher, never lower. Near 3M high $216.97 resistance; planned trim funds MKSI plan |

Combined open P&L: **+$1,812.41** · Realized (journal, all closed): **+$1,387.93**.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| **GOOG** | band $348.35–356.25 after SOS >1x vol | $331.86 | — | $381.81 | 1.05–2.03 | **NOT PRINTED** — $343.11 below band, no SOS, SMA100 overhead | **WAIT** — Thorp NO BET 24/40 (pooled t=3.03 ✓ but 2026 PF 0.74, maxDD 53.6%) · Wyckoff NEUTRAL · Medallion WEAK +2.0 | $0 now; on print 1 sh = 0.66% risk ✓ |
| **AMZN** | $257.92 (SMA50 reclaim, >1x vol) | $246.33 | $267.56 | $280.72 | 0.83 / 1.97 | **NOT PRINTED** — $255.36 under gate; MACD hist +0.81 fired (partial confirm) | **WAIT** — Thorp NO BET 19/40 (t=0.42, 1.5% CAGR vs SPY 86.2%) · Wyckoff accum. unconfirmed · Medallion NOISE | $0 (2 sh = 0.9% risk ✓, but NO BET) |
| **GEV** | reclaim $1,004.62 band (via $997.47 SMA100) on >1x vol | $939.44 | — | $1,140.99 | 1.07–2.09 | **FAILED** — Oct-6 print broken intraday: $988.32 < band $1,004.62 **and** < SMA100 $997.47 | **NO BET** — Thorp 19/40 (t=1.89, 2026 PF 0.94, sizing 3.6% ✗) · Wyckoff gate + SMA100 lost · Medallion underpowered | $0 |
| **MKSI** | T2 zone $255–274 on SOS bar → buy-stop above high | kill: weekly <$228.46 | — | T3 $311 / $322 | plan-level (staged) | **IN ZONE, SOS NOT PRINTED** — $271.20 inside T2, red -3.63% knife, no SOS | **STAGED ENTRY** — Thorp staged/half-Kelly anchor · Wyckoff pullback zone ON PLAN, needs SOS · Medallion NOISE → staged only | T1+T2 ≈ $543 (2 sh) on print; cap 4 sh; rest SMH/SOXX |

**Entries triggered: 0 · Conditional: 4 (GOOG, AMZN, GEV — structure failing, MKSI — in zone awaiting SOS) · Exits to act on: ZS trim near $217 + trail, NVDU trail only · New capital deployed: $0.**

**MKSI is the only setup inside its entry zone this run — but today is a red knife: buy-stop above the SOS bar, never market-buy.**

---
*Entry Monitor 3-Expert Pipeline · monitor_entries.py (21:00 ICT open run, intraday prices) + Thorp / Wyckoff 2.0 / Medallion · backtests refreshed 03:02 ICT on completed Oct-6 bar: `_gev_experts.py` / `_goog_experts.py` / `_amzn_experts.py` → `_*_expert_out.txt` (5y, 9 monitor tickers, net 10bp RT) · MKSI panel: `mksi_longterm_report.md` · 07 Oct 2026 21:00 ICT*
