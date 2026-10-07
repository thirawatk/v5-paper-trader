# -*- coding: utf-8 -*-
REPORT = r'''# 📡 Entry Monitor Report — Thu 08 Oct 2026 03:00 ICT

Run: `monitor_entries.py` 03:01 ICT = **16:01 ET Oct 7 full-session close**. Changes vs the 22:00 run (0 triggers): **AMZN reclaim PRINTED** — closed $259.92 inside the $256.68–263.88 band AND above SMA50 $258.01 (yesterday closed $1.14 under). **GEV rejected a 2nd time** — closed $997.63, $7 below band bottom $1004.62, after breaking the $995.05 shelf intraday (low $980.47) and recovering. **MKSI fell INTO the $255–274 swing zone** ($273.15, bought back to upper-third close at SMA50). **AMKR missed its $52.60 buy-stop by 4 cents** (high $52.56, vol <1x). GOOG still ~$1 under its band. All expert backtests refreshed on the completed Oct-7 bar (`_amzn/_goog/_gev_experts.py` + new `_mksi_amkr_experts.py`: fib-dip pool extended with MKSI/AMKR, 11-factor gates, ZS exit probe).

## 🟢 Entry Triggered

### AMZN — the confirmation printed, the panel still says NO BET

- **Setup:** $259.88 (+1.40%) · bar O 254.07 / H 260.14 / L 253.17 / C **259.92**, closed **97% up the range** · vol 0.75x (monitor) / 0.94x (daily calc) — **below 1x** · 5d 2🔴/3🟢 · RSI 62.0 (monitor) / 58.5 (Wilder) · above SMA20 $251.63, **reclaimed SMA50 $258.01**, above SMA100 $252.87
- **Entry:** $259.88 at market / band retest $256.68–263.88
- **Stop:** $244.19 (monitor) · alt structure stop $246.71 (prior swing low, expert script)
- **TP1:** $267.56 (30d high, 0.85R) · **TP2:** $287.20 (3m high)
- **R:R:** **1.74:1** to TP at market (monitor stop) · 1.67:1 with expert stop → 2.1R target · breakeven WR 36.5%
- **Trigger: PRINTED** — evidence: green +1.42% close $259.92 **inside the $256.68–$263.88 band AND above SMA50 $258.01** (the exact reclaim that failed yesterday), closing 97% up the range. Caveat: volume 0.75–0.94x — no initiative volume on the reclaim.

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — 22/40** (below the 25 proceed-line) | Exact trigger backtest (5y, 9 monitor tickers, net 10bp): **Variant B (reclaim + vol>1x): n=85, WR 37.6%, +0.069R, PF 1.10, t=0.42** — nowhere near the 3.0 bar. Variant A (no vol): n=185, −0.027R, PF 0.96. **AMZN-only B: n=14, +0.422R, PF 1.74, t=0.97 — but 2026 0/3 (PF 0.00), H2 PF 0.77 = decay in progress.** Portfolio sim B: **+6.7% total (1.4% CAGR) over 4.5y vs SPY +85.7%** → fails the ultimate question decisively. Setup-class reading (fib-dip pullback) is better: AMZN n=107 +0.284R PF 1.72 t=2.49, pooled n=837 t=3.04 ✓ — still single-name <3.0. **11-factor gate +0.33 FAIL** (<±0.50). Scorecard: Logical 2 · Stat 2 · Cost-exp 3 · Robust 2 · Capacity 5 · Integrity 3 · Paper 2 · R/R 3 = **22/40**. Kelly 3.5% (trigger) — sizing binds anyway: 1 sh = 0.63% risk ✓, 2 sh = 1.26% ✗ |
| 📊 Wyckoff 2.0 | **ACCUMULATION-LEANING — reclaim printed, unconfirmed** | SMA50 reclaimed on a 97%-range close; HH/HL (10d H 260.14 / L 244.73 vs prior 259.49 / 244.30); only 2 distribution days/25; +12.0% over 1y VPOC $232.03, inside value area. **BUT OBV 60d falling (−7.3M/day), CMF20 +0.046 flat, 30d up/down vol 0.91, vol <1x = no initiative buying; SMA stack mixed (50>20), 60d range position 55% = balance not trend.** Confirmation = close **> $263.88 band top** or a >1x-vol SOS, then hold the $258 Back-Up. Failure < $251.63 (SMA20) kills it. Supply: $267.56 (30d high) → 1y VAH $271.24 → 3m VAH $283.30 |
| 🧬 Medallion | **WEAK SIGNAL — composite +3.0** | ✓ reclaim printed, ✓ >SMA100 (+2.8%), ✓ RSI 58.5 neutral-cool, ✓ >1y VPOC, ✓ 2R/3G week; ✗ SMA stack 20<50, ✗ vol 0.94x (no initiative), ✗ 60d mid-range 55% = balance. Trigger sample t=0.42 ≪ 3.0; cross-time H1 WR 43% vs H2 33% deteriorating; single-name textbook pattern = highest overfit class |

- **Expert consensus: NO BET — trigger valid, edge insufficient.** The confirmation the plan asked for is on the tape, but the trigger itself has no demonstrated expectancy (t=0.42), 2026 is PF 0.58, and the portfolio sim trails SPY by ~84 points over the same window. At most paper-size.
- **Budget $2,500: $0 deployed** (1 sh would fit the 1% cap at 0.63% risk — panel verdict overrides; gate +0.33 also below ±0.50).

---

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG — $1 under the band, SMA100 still overhead

- **Setup:** $347.29 (+0.78%) · C 347.37, closed 97% up range · vol 0.60x · above SMA20 $341.10 / SMA50 $342.92 but **1.0% BELOW SMA100 $351.27 — overhead supply, not support** · RSI 53.3 / 55.9 · 36.7% retrace of the $325.63→359.98 leg
- **Trigger needed (NOT printed):** price must first rally **into $348.35–356.25**, then print an SOS bar (wide-range green, upper-third close) on **>1.0x volume** → buy-stop above its high. Today: closed **$1.06 under band bottom**, vol 0.60x, no SOS.
- **Planned levels:** band $348.35–356.25 · stop $331.65 · TP $381.81 (3m high ≈ 1y VAH $380.76) · **R:R 2.00:1 band bottom / 1.04:1 band top**

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now — 24/40**; small size only on print | Pooled fib-dip signal 5y/9 tickers net 10bp: **n=837, WR 52.6%, +0.122R, PF 1.25, t=3.04 ✓** (clears 3.0), Kelly 10.7%, maxConsecLoss 24. GOOG-only: n=96, WR 57.3%, +0.184R, PF 1.44, t=1.60. **2026 GOOG negative** (n=18, PF 0.92, −0.033R). Portfolio sim 2.95× over 4.57y, **CAGR 26.7% vs SPY ≈16.6%/yr — beats the index — but maxDD 53.6%** blows the 25% cap. **Gate +0.29 FAIL.** On print: 1 sh at band bottom = $16.70 risk = 0.67% ✓; 2 sh = 1.34% ✗ |
| 📊 Wyckoff 2.0 | **NEUTRAL** — markup intact, no trigger | +4.5% over 1y VPOC $332.26, inside value area. But **OBV 60d falling, CMF20 −0.044 (5d −0.055), 4 distribution days/25, LH/LL mixed** (10d 350.09/332.65 vs prior 359.98/325.65), −1.0% vs SMA100, vol 0.60x = **no SOS on this pullback**. Profile: HVN $339–345 supports below; **LVN 68M at $348 = band bottom is thin** (price can slice it); $355 HVN (206M) = first resistance |
| 🧬 Medallion | **WEAK SIGNAL — +2.0** | ✓ regime (px>SMA20&SMA50), ✓ band-touch (0.2% below bottom), ✓ RSI neutral, ✓ >VPOC; ✗ SMA stack 20<50, ✗ vol 0.60x, ✗ no momentum burst. Pooled t=3.04 ✓ but GOOG t=1.60 ✗; GOOG 2026 negative = decay in progress |

- **Expert consensus: WAIT — no entry.** Green label, but price is outside the band, SMA100 is lost overhead, no SOS, gate fails.
- **Budget $2,500:** $0 now · on print at band bottom: **1 sh** ($348, 0.67% risk) ✓ — 2 shares = 1.34% ✗.

### GEV — second band rejection; structure shelf broke intraday and recovered

- **Setup:** $997.62 (−3.07%) · O 1008.90 / H 1014.95 / **L 980.47** / C 997.63 · vol 0.73x · closed **AT SMA100 $997.45–997.56** · **$7.00 BELOW band bottom $1004.62** · RSI 70.7 (monitor 14-day cut) / 56.8 (Wilder) — feed disagreement, treat "overbought" as window-dependent
- **Trigger needed (NOT printed):** reclaim **≥ $1004.62 on >1x vol** (band re-entry), OR hold this level as a higher-low then SOS above $1014.95. **Note: the $995.05 structure shelf was broken intraday (low $980.47) and bought back — held on a closing basis by $2.58.** Yesterday's spike to $1052.78 gave back −3.07% today = 2nd failed advance from the band.
- **Levels:** band $1004.62–1036.80 · stop $939.14 (expert alt $933.82 = fib618−ATR) · TP $1140.99 · **R:R 2.08:1 band bottom / 1.07:1 band top / 2.45:1 at market**

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — 22/40** | GEV-only fib-dip: **n=34, WR 64.7%, +0.278R, PF 1.83, t=1.62** (<3.0). **2026 GEV negative (n=16, PF 0.74, −0.121R); H2 PF 0.86 vs H1 PF 3.60 — decayed hard.** Pooled n=837 t=3.04 ✓ but cross-market is NOT uniform (ZS 4.44 / RDDT 2.15 vs MRVL −3.20 / GDDY −1.87) → data-mining risk. **Gate +0.07 FAIL.** **Not sizeable:** 1 sh at market with monitor stop = $58.48 risk = **2.3% of $2,500** (cap 1%) ✗ — even a band-bottom entry needs the structure stop to squeak in |
| 📊 Wyckoff 2.0 | **NEUTRAL / Upthrust risk unresolved** | OBV 60d **rising +90k/day**, 30d up/down vol 2.12, HH/HL, 2 distribution days/25 — but **52.6% retrace of the 868.25→1052.78 leg (>50% = deep)**, price sitting ON SMA100 with SMA50 $966.28 below, vol 0.73x. Two failed advances out of the band (Oct 6 tag $1052.78 → faded; today −3.07%). **3m VPOC $985.88 = magnet just below** — lose it → $966 SMA50 next; close >$1004.62 restores the bulls |
| 🧬 Medallion | **WEAK SIGNAL — +3.5** (tolerance caveat) | ✓ regime, ✓ >SMA100 (+0.0%), ✓ RSI cool, ✓ 5d 4🟢; ✗ SMA stack 20<50, ✗ deep retrace −0.5, ✗ vol 0.73x. The "inside band" +1 uses the script's ±2% tolerance — strict band says −0.7% outside |

- **Expert consensus: WAIT — no entry.** Trigger not printed, second rejection, gate fails, and the monitor stop cannot fit the 1% cap even if it did print.
- **Budget $2,500:** **$0** (1 sh at market with the plan stop = 2.3% risk > cap).

### MKSI — swing zone HIT, but the plan's execution gate blocks it

- **Setup:** $273.09 (−2.96%) / daily C **273.15 — inside the $255–274 swing zone ✓** · O 271.77 / H 274.99 / L 269.20 / C 273.15 — gap-down open, **bought back: green intraday body +$1.38, close in the upper third, sitting on SMA50 $273.89** · vol 0.80x · RSI **75.2 (monitor, 14-day cut = recent-window overbought) vs 53.2 (Wilder full-history = neutral)** · 5d 1🔴/4🟢
- **Plan (revised Oct 7):** ONE entry in zone · **SL = fill − 2×ATR** (plan ref ~$19.78 at ATR $9.89; **ATR now $11.50 → 2×ATR = $23.00** → SL ≈ $250.15 on a $273 fill) · **TP1 1.5R ≈ $302.82 · TP2 2.5R ≈ $322.60** · trail + overbought exit · time stop 2–4wk · size = $25 ÷ stop → **1 sh**
- **GATE: 11-factor = +0.12 FAIL (need ≥ +0.50; Oct 7 panel measured +0.05)** → **entry NOT authorized this run.** Alternate trigger: daily close ≥ $311 (SMA100 breakout).
- **Trigger needed: gate ≥ +0.50** (zone condition itself is met).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **CONDITIONAL BET at gate-pass — 25/40, small size** | Setup-class backtest (uptrend + 38.2–50% fib pullback, 5y, net 10bp): **MKSI n=58, WR 63.8%, +0.522R, PF 2.42, t=3.08 ✓ — clears the 3.0 bar**, Kelly 37.5%. H2 decayed but positive (n=29, +0.144R, PF 1.34); year split shows 2024 PF 0.21 (cycle crash) / 2025 PF 9.71. Extended pool (base9+MKSI+AMKR) n=986, t=5.35. **But the plan gate reads +0.12 < 0.50 → no execution until it passes.** On pass: 1 sh ≈ $273, risk $19.78–23.00 = 0.79–0.92% ✓. Scorecard: Logical 2 · Stat 4 · Cost 3 · Robust 3 · Capacity 4 · Integrity 3 · Paper 2 · R/R 4 = **25/40** |
| 📊 Wyckoff 2.0 | **ACCUMULATION — footprints confirmed, test in progress** | 1y: −40% markdown $447→$228.46 climax → V-recovery. Now: **OBV 60d rising +144k/day · CMF20 +0.213 (5d +0.250 = genuine accumulation) · 30d up/down vol 2.07 · 1 distribution day/25 · HH/HL** (10d 286.38/251.19 vs prior 270.29/228.46) · +5.0% over SMA20, above 1y VPOC $259.92, retrace only 22.8%. Today's gap-down bought to an upper-third close at SMA50 = **a test, not a breakdown**. Next confirmation: close >$286.38 (10d high) → $311 SMA100. Failure: loss of $260 (SMA20/3m VPOC $260.56 cluster) → $255 zone floor; **2×ATR stop = the exit (no averaging)** |
| 🧬 Medallion | **NOISE — composite −1.0** | ✗ regime (px < SMA50 by 0.3%), ✗ stack 20<50, ✗ −12.0% vs SMA100; ✓ RSI neutral, ✓ >VPOC, ✓ shallow 23% retrace, ✓ CMF/OBV positive (Wyckoff captures those). Raw price/volume factors alone do not justify entry — the binding constraint is the +0.50 gate |

- **Expert consensus: WAIT — zone right, gate not passed.** Structure says accumulation and the setup class has real measured edge (t=3.08), but the plan's own execution gate reads +0.12 → no entry this run. Do not front-run the gate.
- **Budget $2,500:** $0 now · on gate pass: **1 sh ≈ $273** (risk 0.79–0.92% ✓).

### AMKR — missed the buy-stop by 4 cents (0/3 conditions)

- **Setup:** $52.28 (−2.08%) / C 52.27 · O 51.90 / H **52.56** / L 51.11 / C 52.27 — green body, close 80% up range, holding the **SMA20/50 cluster ($51.73 / $51.45)** · vol 0.48x (monitor) / 0.64x (daily) · RSI 60.8 (monitor) / 49.6 (Wilder) · 5d 3🔴/2🟢
- **Trigger needed (NOT printed — 0/3):** Oct 7 panel consensus: **buy-stop $52.60 with vol ≥1.0x** (ideal structural $56.60). Today: high **$52.56 — short by $0.04**, close $52.27 < $52.60, vol 0.64x <1x. **Gate: 11-factor −0.08 FAIL.**
- **Levels:** stop $51.00 (tight, candle low) / $49.00 (fib786 wide) · TP1 $54.02 (fib618) · TP2 $57.53 · **R:R from $52.60 trigger: 0.89:1 → TP1 (tight stop), 3.08:1 → TP2; wide stop 1.37:1 → TP2**

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET (small) — but gated; 24/40** | Fib-dip class on AMKR: **n=91, WR 70.3%, +0.776R, PF 3.14, t=5.32 ✓✓ — strongest single-name in the extended pool**; H2 n=46, WR 87%, +1.329R, PF 9.54, t=8.31 (caveat: **2026 only n=3** — few signals while AMKR was in its downtrend). Scenario EV +0.375R (Oct 7 panel) unchanged; Kelly 48% → 1% risk cap binds. **Gate −0.08 FAIL + trigger 0/3 → no execution.** Scorecard: Logical 2 · Stat 4 · Cost 3 · Robust 3 · Capacity 4 · Integrity 3 · Paper 2 · R/R 3 = **24/40** |
| 📊 Wyckoff 2.0 | **Markup pullback, accumulation-leaning — needs volume** | HH/HL (10d 56.56/51.11 vs prior 54.89/45.33), cluster holding, today's $51.11 dip bought to an upper-third close; range 51.11–56.56 building since Sep 29; SOS breakout projects ~$61–62 (fib38.2 + SMA100). **BUT OBV 60d falling (−452k/day), 30d up/down vol 0.89, −15.5% vs SMA100** — supply still present on rallies. Upgrade only on **vol ≥1x + close >$52.60 (then $53.48 SMA10 reclaim)**; structural ideal remains $56.60 |
| 🧬 Medallion | **WEAK SIGNAL — +1.0** | ✓ regime (px>SMA20&SMA50), ✓ stack 20>50, ✓ >1y VPOC (+11.2%); ✗ −15.5% vs SMA100, ✗ vol 0.64x, ✗ net-red 5d week. Panel's "≈1.2 independent factors" read unchanged; needs vol >1.0x + SMA10 $53.48 reclaim to upgrade — same trigger the Wyckoff side wants |

- **Expert consensus: WAIT for the trigger** — close ≥ **$52.60 with vol ≥1x** (ideal $56.60), gate ≥ +0.50. Conditional GO from the Oct 7 panel stands; nothing printed today.
- **Budget $2,500:** $0 now · on print: **15 sh** on the tight stop ($789, risk $24 = 0.96% ✓) / 6 sh wide stop ($316).

---

## Not Routed This Run

- **GDDY** 🟡 PULLBACK ($97.25, entry $98.30 SMA20) — routine per routing rules.
- **ACMR** 🔴 WAIT — last night's panel: NO ENTRY 3/3 (re-trigger: green close >$74.09 → structural buy-stop $78.50).
- **RDDT, BCC, FBK, MRVL, OPEN** — no signals this run. **NVDU** — fully closed Oct 7 (context only).

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **ZS** (15 sh) | 📈 **HOLD + TRAIL** | $213.62 | **+42.4% (+$954.30)** | Trail **$194.88** (2×ATR $9.37; daily calc 194.69). Bar: **opened $216.00 = the 3M-high zone, faded to $209.70, closed $213.55 red/mid-range → 2nd consecutive fade at $216.97 resistance** (Oct 6 high 215.51). StochK 88.3 overbought · MACD hist still **+0.20** (intact) · MFI 71.6 · **7 distribution days/25 ⚠️** · above 1y VAH $211.88 = price discovery (1y high $336.99 far above) · Medallion **+6.0**. Let TP3 run on the trail; optional discipline: trim 5 sh banks **+$318** into the resistance zone (rest ride with $194.88 locked-min +$447) |

Open risk: **ZS only** · combined open P&L: **+$954**.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| **AMZN** | $259.88 mkt / band $256.68–263.88 | $244.19 (alt 246.71) | $267.56 | $287.20 | 1.74:1 | **PRINTED** — green +1.42% close $259.92 in band + above SMA50 $258.01 reclaim, 97% range; vol 0.75–0.94x (<1x) | **NO BET** — Thorp 22/40 (trigger t=0.42, 2026 PF 0.58, port 1.4% CAGR vs SPY 85.7%) · Wyckoff ACCUMULATION-LEANING unconfirmed · Medallion WEAK +3.0 · gate +0.33 FAIL | **$0** (1 sh = 0.63% risk would fit — panel rejects) |
| **GOOG** | band $348.35–356.25 **after SOS >1x vol** | $331.65 | — | $381.81 | 2.00 band-bot | **NOT PRINTED** — close $347.29, $1.06 under band, vol 0.60x, SMA100 overhead | **WAIT** — Thorp 24/40 (pooled t=3.04 ✓ but GOOG t=1.60, 2026 PF 0.92, maxDD 53.6%) · Wyckoff NEUTRAL · Medallion WEAK +2.0 · gate +0.29 | $0 now · on print 1 sh = 0.67% ✓ |
| **GEV** | band $1004.62–1036.80 **on >1x vol reclaim** | $939.14 | — | $1140.99 | 2.08 band-bot | **NOT PRINTED** — closed $997.62, $7 below band (2nd rejection); $995.05 shelf broke intraday (980.47), recovered by $2.58 | **WAIT** — Thorp 22/40 (2026 PF 0.74, H2 PF 0.86, t=1.62; 1 sh = 2.3% risk > cap) · Wyckoff UT-risk / neutral · Medallion WEAK +3.5 · gate +0.07 | $0 |
| **MKSI** | zone $255–274 (**HIT $273.15**) — gate-pass required | fill − 2×ATR ≈ $250 (ref $19.78) | $302.82 (1.5R) | $322.60 (2.5R) | plan 1.5R/2.5R | **ZONE HIT — GATE FAIL** (11-factor **+0.12 < +0.50**) | **WAIT FOR GATE** — Thorp CONDITIONAL BET 25/40 (setup-class t=3.08 ✓ PF 2.42) · Wyckoff **ACCUMULATION confirmed** · Medallion NOISE −1.0 | $0 now · on gate pass **1 sh ≈ $273** (0.79–0.92%) ✓ |
| **AMKR** | buy-stop **$52.60 w/ vol ≥1x** (ideal $56.60) | $51.00 / $49.00 | $54.02 | $57.53 | 0.89 / 3.08 | **NOT PRINTED 0/3** — high $52.56 (−$0.04), close $52.27, vol 0.64x; gate −0.08 FAIL | **WAIT** — Thorp BET-small 24/40 (fib-dip t=5.32 ✓✓ PF 3.14) · Wyckoff cluster hold, needs volume · Medallion WEAK +1.0 | $0 now · on print **15 sh tight-stop = $789** (0.96%) ✓ |
| **ZS** | n/a (holding) | $194.88 trail | — | — | — | HOLD | Trail, let TP3 run; 2nd fade at $216.97 + 7 dist days → optional 5-sh trim | position open +42.4% |

**This run: 1 trigger printed (AMZN — panel verdict NO BET, $0 deployed) · 4 conditional setups (GOOG, GEV, MKSI, AMKR) · 1 trailing-position alert (ZS) · new capital deployed: $0.**

---
*Entry Monitor 3-Expert Pipeline · `monitor_entries.py` + Thorp / Wyckoff 2.0 / Medallion · backtests refreshed on completed Oct-7 bar: `_amzn_experts.py` → `_amzn_expert_out.txt`, `_goog_experts.py`, `_gev_experts.py`, new `_mksi_amkr_experts.py` → `_mksi_amkr_expert_out.txt` (fib-dip pool extended to MKSI/AMKR, 11-factor gates via `confluence_score.py` on daily bars, ZS exit probe) · 08 Oct 2026 03:00 ICT*
'''
with open('/root/.hermes/profiles/trader/scripts/entry_monitor_report.md', 'w') as f:
    f.write(REPORT)
print('WROTE', len(REPORT), 'chars')
