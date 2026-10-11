# 📡 Entry Monitor Report — Mon 12 Oct 2026 00:06 ICT

Run: `monitor_entries.py` (00:02 ICT) + `_entry_0002_experts.py` — **markets CLOSED** (Sunday 11:00 ET). Last bar = **Friday 09 Oct COMPLETED session** → volume ratios are full-session this run, so **trigger state is finally decidable** (the 22:00 Fri run could only guess on a 90-min bar). 3 TV-feed timeouts → Yahoo fallback held; yfinance 5y series loaded for all 8 tickers.

**New vs Fri 22:00 run:** GOOG faded into the close **$347.86 — $0.49 UNDER band low** (was touching band live) · RDDT $159.91 +2.20% full session, still 6.5% below band · **GEV closed $1,004.73 — INSIDE band** (upper-third close) but only **0.49x volume** · MKSI $264.50 in zone, red body / 69% close pos, 0.52x vol · **ZS +7.80% to $233.73, new 3M high $234.31 — trim STILL not executed (journal: 15 sh open)** · AMZN +3.29% to $262.43, back above entry · All 11-factor gates still FAIL.

## 🟢 Entry Triggered

**None — no confirmation trigger printed on Friday's completed bar.** GEV is the closest (closed inside its band, upper-third) but at 0.49x volume — half the ≥1.0x requirement. GOOG closed $0.49 under its band. MKSI in zone but no SOS bar and gate fails. RDDT/OPEN nowhere near their triggers. Next print opportunity: Monday session (close 03:00 ICT Tue), or a Monday intraday buy-stop hit.

---

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG — closed UNDER the band by $0.49
- **Setup:** above SMA20 $342.45 / SMA50 $343.39, below SMA100 $350.33. 5d 1🔴/4🟢. 60d **−2.6% vs SPY +3.8%**.
- **Friday's bar:** O 348.00 → C **$347.86 (+0.87%)**, vol **0.64x**, close position **23% range (lower third)** — green day, weak close, opposite of an SOS.
- **Trigger needed (NOT printed):** green close **≥ $348.35 into band $348.35–356.25** (ideally reclaiming SMA100 $350.33) on **≥1.0x full-session volume**. Missed by $0.49 on price and 0.36x on volume.
- **Planned levels:** Entry $348.35–356.25 · Stop $331.99 · TP $381.81 · R:R 2.05:1 (risk $16.36 / reward $33.46, breakeven WR 32.8%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — confidence MEDIUM | 5y signal n=96, WR 57.3%, +0.184R, PF 1.44, **t=1.60 (<2, marginal)**, Kelly 17.5% — but recent half n=48 WR 72.9%, +0.578R, **t=3.74, PF 3.41** (edge is recent, not old). MA-pullback = most crowded signal class (logical basis 2/5), 60d −2.6% laggard → ~21/40 |
| 📊 Wyckoff 2.0 | **NEUTRAL → bullish on SOS** | Markup pullback: OBV 60d rising (+258k/day), 30d up/down vol 1.48, in value area, 35.3% retrace — but LH/LL, CMF −0.119, 4 distribution days, Friday closed lower third. Confirm: wide-range green bar, upper-third close, ≥1.0x vol, close ≥$348.35 (>$350.33 ideal) |
| 🧬 Medallion | **NOISE** | Composite **0.0/10**; 11-factor gate **+0.16 FAIL** (<±0.50); SMA stack 20<50; vol 0.64x — would not lift portfolio Sharpe |

- **Expert consensus: WAIT — band not claimed.** Budget: 1 sh = $16.36 risk = **0.65% of $2,500 ✓ ready**, $0 committed.

### RDDT — strong 2-day bounce, band still 6.5% overhead (two-move)
- **Setup:** above SMA20 $152.45 / SMA50 $154.04, below SMA100 $164.78. 60d **−21.3% vs SPY +3.8%**.
- **Friday's bar:** C **$159.91 (+2.20%)**, vol **1.08x** (full session ≥1.0x ✓), close pos 34% — volume condition met, price condition not: **still 6.5% below band low $171.11**.
- **Trigger needed (NOT printed):** TWO-MOVE — rally **into $171.11–179.58**, then green close / SOS bar there on ≥1.0x volume. No market-buy, no front-running the band.
- **Planned levels:** Entry $171.11–179.58 · Stop $156.10 · TP $207.00 · R:R 2.39:1 (risk $15.01 / reward $35.89, breakeven WR 29.5%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — confidence HIGH | Band 6.5% away — nothing to evaluate; n=30 (WR 63.3%, +0.480R, PF 2.27, t=2.15, Kelly 35.5%) is the best raw set but n=30 is statistically unstable; 60d −21.3% vs SPY = deep laggard, a 2-day bounce has no distinguishable edge |
| 📊 Wyckoff 2.0 | **NEUTRAL — accumulation attempt vs distribution footprint** | SMA50 reclaim = Phase D candidate, capped under SMA100 → range not trend; volume footprint still bearish: OBV 60d **falling −2.0M/day**, CMF −0.144, 30d up/down vol **0.67**, LH/LL, −22.7% off 3M high. "If close >$164.78 → expect band test $171+; failure <$154 → reclaim fails" |
| 🧬 Medallion | **NOISE** | Composite **+1.0/10**; gate **+0.10 FAIL**; below SMA100; one 2-day bounce only |

- **Expert consensus: WAIT — price far below band.** Budget: 1 sh = $15.01 risk = **0.60% ✓ ready**, $0 committed.

### GEV — CLOSED inside the band, volume veto (closest to a print)
- **Setup:** above SMA20 $958.41 / SMA50 $968.71 / **SMA100 $996.98 (+0.8%)**. HH/HL markup. 60d **−5.7% vs SPY +3.8%**.
- **Friday's bar:** C **$1,004.73 (+0.54%)** — **inside band $1,004.62–1,036.80** (by $0.11), body +4.43, close pos **84% (upper third)** — but vol **0.49x**.
- **Trigger needed (NOT printed):** close inside band on **≥1.0x volume** + bullish test (SOS). **2 of 3 conditions met** (close in band, upper-third); volume is half of the requirement — a 0.49x drift is not initiative buying.
- **Planned levels:** Entry $1,004.62–1,036.80 · Stop $936.46 · TP $1,140.99 · R:R 2.00:1 (risk $68.16 / reward $136.37 from band low).
- **Sizing veto stands:** 1 sh = $68.16 stop-risk = **2.73% of $2,500, over the 1% cap** ✗ (0 shares affordable).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — sizing veto + decay** — confidence MEDIUM | Best structure of group but not sizeable at 1% risk. Carried stats: fib-dip n=34, WR 64.7%, +0.278R, t=1.62 — **decayed: 2026 n=16 PF 0.74, recent half n=17 PF 0.86, both negative expectancy.** Score 22/40 |
| 📊 Wyckoff 2.0 | **ACCUMULATION (HH/HL) — SOS attempt, no initiative** | OBV rising (+159k/day), 30d up/down vol **2.06**, only 2 distribution days, +2.0% over 3m VPOC $984.64, 26% retrace, upper-third close. "Close ≥$1,004.62 on ≥1.0x vol → Back-Up resumes toward $1,052; close <$996.82 → range top rejected again" |
| 🧬 Medallion | **WEAK SIGNAL** | Composite **+2.0** (best of the routed set) but gate **+0.07 FAIL**; vol 0.49x; SMA20<50 → no deploy |

- **Expert consensus: WAIT for ≥1.0x-volume in-band close. Not sizeable within 1% risk — $0.**

### MKSI ⭐ — pre-planned swing MKSI-SW-1, in zone, trigger still absent
- **Setup:** Oct 8 SOW bar (−4.68%, vol 1.03x, 17% close pos), Friday +1.58% to **$264.50** (red body −1.59 but **69% close position** off the $256.65 low), vol 0.52x. Below SMA50 $273.48 / SMA100 $310.02, 60d **−26.1% vs SPY**. Regime BOUNCE.
- **Price:** **inside approved swing zone $255–274**, on 1y VPOC $259.92 (+1.8%) — price/VPOC confluence held again.
- **Trigger needed (NOT printed):** Wyckoff **SOS bar + buy-stop above the trigger-candle high** (never market-buy the knife) **AND 11-factor gate ≥ +0.50** (live gate **+0.08 FAIL**). Alternative trigger per plan: daily close > $311.
- **Planned levels (at Friday's close):** single entry full size in $255–274 · SL = actual fill − $19.78 (2×ATR; at $264.50 → $244.72) · TP1 = fill +1.5R ($294.17) · TP2 = fill +2.5R ($313.95) · time stop 2–4wk · SL hit = exit, no averaging. Sizing: 1 sh = $264 notional, risk $19.78 = **0.79% of $2,500 ✓**.

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET — conditional/armed** — confidence MEDIUM | Pre-registered plan, fixed $19.78 risk: 5y n=58, WR 63.8%, +0.522R, PF 2.42, **t=3.08 (passes the >3 bar)**, Kelly 37.5% → 1% risk ≈ ⅙-Kelly. **Decay flag: recent half n=29 WR 58.6%, +0.144R, t=0.75, PF 1.34.** Counter-trend (60d −26.1%) — payoff must come from the R-multiple plan. VETO: buying the red knife turns a 2.5R plan into an unforced loss |
| 📊 Wyckoff 2.0 | **ACCUMULATION — SOW needs SOS** | HH/HL markup, CMF **+0.199**, OBV rising (+179k/day), 30d up/down **1.91**, 1 distribution day, at VPOC support. Oct 8 = SOW; Friday = test, not strength. "If green SOS prints off $255–274 on ≥1.0x vol → expect SMA50 $274 retest, then $311; close <$255 → zone fails, stand down" |
| 🧬 Medallion | **NOISE (pre-registered process ✓)** | Composite **−2.0** (below SMA50/SMA100, regime False); gate **+0.08 FAIL**; vol 0.52x. Plan written BEFORE the move = no curve-fitting — upgrades to STRONG only on printed SOS + passing gate |

- **Expert consensus: WAIT FOR TRIGGER — in zone, buy-stop not hit, gate fails.** Budget: reserved, $0 committed (1 sh = $19.78 risk = **0.79% ✓**).

### OPEN 🟠 — squeeze watch, knife still falling
- **Setup:** DOWNTREND below all SMAs, at 3M-low zone $2.13. Monitor RSI 23.9 / Stoch 13.2 oversold. OI P/C 0.17, call walls $3/$4/$5 overhead. 60d **−51.2% vs SPY +3.8%**.
- **Friday's bar:** C **$2.22 (−3.06%)**, vol 0.95x, close pos 25% — red, no green close.
- **Trigger needed (NOT printed):** **green close + volume ≥1.3x (full session)** off the $2.13 low. Stop if entered: $2.00 (put wall/max pain).
- **Planned levels:** no entry until trigger · stop $2.00 (risk $0.23/sh → 108 sh = 0.99% of $2,500 if it ever qualifies).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET** — confidence HIGH | Falling knife, no structural edge (logical basis 1/5 = mean-reversion hunch); 60d −51.2%; call walls cap any bounce. Score ~15/40 — below the 20 floor |
| 📊 Wyckoff 2.0 | **DISTRIBUTION / markdown — no Spring yet** | LH/LL, −50% below 1y VPOC $4.44, CMF −0.302, OBV 60d **−7.0M/day**, 30d up/down vol 0.45 = Phase E markdown. Spring candidate ONLY if $2.13 holds with SOS + test |
| 🧬 Medallion | **NOISE — NEGATIVE** | Composite **−6.0/10** (worst of set); gate +0.08 FAIL; oversold RSI alone = 1 weak factor |

- **Expert consensus: WAIT — no entry on the knife.** Budget: $0.

---

## Not Routed This Run

- **ACMR $71.37** — 🔴 WAIT, downtrend below all SMAs, 5d 4🔴/1🟢, Stoch 14.5, at 78.6% retrace $71.02. Needs green close > SMA20 $74.03. Routine — no expert pass.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| ZS (15 sh @ $150) | 🚨 **TRIM 5 sh** + TRAILING runner | Friday close **$233.73** (+7.80%, session high **$234.31 = new 3M high**, 96% close pos) | **+55.8% (+$1,255.95, 15 sh)** | **Trim level $216.97 crossed Thursday and price ran ~$17 above it — trade journal still shows 15 sh OPEN: trim NOT executed.** Expert: RSI 72.9 / Stoch 98.8 overbought, MACD hist +1.845, ATR $9.84 → trail **$214.05**; above 1y VAH $229.34 = price discovery. Trim 5 sh @ $233.73 → **+$418.65 realized**; remaining 10 sh trail $214.05 → locked min **+$640.49**; combined **≥ +$1,059 locked** (vs +$960.75 if the whole 15 sh only trails). Monitor verdict: TRAILING, let profits run |
| AMZN (10 sh @ $259.55) | HOLD (no alert) | Friday close **$262.43 (+3.29%)** | **+$28.80 (+1.11%)** | Rebounded above entry; SL $249.33 intact, TP1 $274.88 ahead, RSI 59.0, gate +0.27 (best of set, still FAIL) — nothing to do |
| NVDU | CLOSED Oct 7 | — | +$1,903.21 lifecycle | Fully closed — no action |

**ZS expert panel on the trim (updated for Friday's close):**

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET — trim** (HIGH) | Locking +55.8% into Stoch-98.8 overbought new-3M-high converts expected value into realized; ratchet discipline is the edge-gatekeeper |
| 📊 Wyckoff 2.0 | **Phase E markup — trim into strength** | No SOW bar yet (Friday was 84%-range close, +12.25 body), but 6 distribution days/25 and +87.6% above 1y VPOC — distribution risk at highs is exactly where trims pay. Keep 10 sh on the $214.05 trail |
| 🧬 Medallion | **STRONG (risk-reducing)** | Composite **+5.5/10** (only positive confluence in the set), 60d **+53.7%** lone relative-strength winner; trimming cuts single-name variance — the combination, not the single asset, is the portfolio |

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| GOOG | $348.35–356.25 | $331.99 | $381.81 | — | 2.05:1 | **NOT PRINTED** — Friday closed $347.86, $0.49 UNDER band, vol 0.64x, lower-third close | **WAIT** — NO BET (t=1.60; H2 t=3.74) · NEUTRAL→SOS · NOISE (gate +0.16) | $0 committed (1sh = 0.65% risk, ready) |
| RDDT | $171.11–179.58 | $156.10 | $207.00 | — | 2.39:1 | **NOT PRINTED** — closed $159.91, 6.5% below band (vol 1.08x ✓, price ✗); two-move | **WAIT** — NO BET (n=30 unstable) · NEUTRAL w/ distribution footprint · NOISE (gate +0.10) | $0 committed (1sh = 0.60%, ready) |
| GEV | $1,004.62–1,036.80 | $936.46 | — | $1,140.99 | 2.00:1 | **NOT PRINTED** — closed $1,004.73 INSIDE band, upper-third, but vol **0.49x** vs ≥1.0x required (2/3 met) | **WAIT** — NO BET (1sh = 2.73% risk > 1% cap; 2026 PF 0.74) · ACCUMULATION · WEAK (gate +0.07) | not sizeable within 1% |
| MKSI ⭐ | $255–274 (buy-stop over SOS high) | fill − $19.78 ($244.72 at Fri close) | fill +1.5R ($294.17) | fill +2.5R ($313.95) | 1.5R / 2.5R | **NOT PRINTED** — $264.50 in zone on VPOC, red body/0.52x vol, no SOS, gate +0.08 FAIL | **WAIT FOR TRIGGER** — armed conditional BET (t=3.08, H2 decayed) · ACCUMULATION-SOW · NOISE | reserved, $0 committed (1sh = 0.79% ✓) |
| OPEN 🟠 | trigger only (not set) | $2.00 | — | — | — | **NOT PRINTED** — Friday red −3.06% to $2.22; needs green close + ≥1.3x vol | **WAIT** — NO BET (score ~15/40) · DISTRIBUTION · NOISE (−6.0) | $0 |
| ACMR | — | — | — | — | — | 🔴 DOWNTREND — not routed | n/a | $0 |

**Entries triggered this run: 0 · Exits to act on: 1 — ZS TRIM 5 sh at ~$234 Monday's open (level $216.97 crossed Thursday, journal still 15 sh; every session of delay risks the +$418 lock). Capital: $2,500 available, $0 committed.**

Discipline notes:
- Unlike Friday 22:00, this run judges **completed bars**: Friday's full-session volume ratios are real (GOOG 0.64x, RDDT 1.08x, GEV 0.49x, MKSI 0.52x, OPEN 0.95x) — no partial-session excuse left. Still zero prints.
- ZS is the only actionable item NOW: trim 5 sh into ~$234, keep 10 sh on the $214.05 trail. The level was crossed two sessions ago without a fill — the trim is now the weakest link in the process, not the analysis.
- Thorp litmus vs index (60d): GOOG −2.6%, RDDT −21.3%, GEV −5.7%, MKSI −26.1%, OPEN −51.2% vs SPY +3.8%. Every entry candidate is a 60d laggard; they earn risk only through the planned R-multiples, never by assumption. ZS (+53.7%) is the lone relative-strength winner — hence the runner.
- 11-factor gate FAILED on all 7 tickers (GOOG +0.16, RDDT +0.10, GEV +0.07, MKSI +0.08, ZS +0.14, AMZN +0.27, OPEN +0.08 — threshold ±0.50): no confluence-based entry is authorized regardless of price location.
- Markets reopen Monday 20:30 ICT; the next decidable trigger print is Monday's close (03:00 ICT Tue). An intraday buy-stop (MKSI above an SOS candle high) can fill sooner.

---
*Entry Monitor 3-Expert Pipeline · monitor_entries.py + _entry_0002_experts.py · Thorp / Wyckoff 2.0 / Medallion · Mon 12 Oct 2026 00:06 ICT*
