# 📡 Entry Monitor Report — Mon 12 Oct 2026 20:00 ICT

**Pipeline:** 3-Expert Analysis (Thorp / Wyckoff 2.0 / Medallion)
**Context:** PRE-OPEN run — US equities open **20:30 ICT** (20 min after this run; Columbus Day = stocks open, bonds closed). Pre-run `monitor_entries.py` decision inputs are **byte-identical to the 00:06 / 01:30 / 02:30 ICT runs** (Friday 09 Oct completed bar: GOOG 347.86 / RDDT 159.91 / GEV 1,004.73 / MKSI 264.50 / ZS 233.73 / OPEN 2.22 / ACMR 71.37) → expert statistics carry forward unchanged and were re-verified against `_entry_0130_expert_out.txt` + backtest outputs. **NEW this run: live pre-market quotes** (CBOE delayed 20:10 ICT, Google Finance 20:06 ICT). Pre-market prints are **not triggers** — zero regular-session volume, no close.

## 🟢 Entry Triggered

**None — no confirmation trigger printed this run.** No regular-session bar exists yet today; Friday's completed bar also failed every trigger (GEV in-band but 0.49x volume, GOOG $0.49 under band, MKSI no SOS + gate fail, RDDT 6.5% under band). Pre-market can move quotes, not verdicts — triggers only print on today's close (03:00 ICT Tue), or intraday via buy-stop above an SOS candle high (MKSI).

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG — pre-market $0.95 under the band
- **Setup:** above SMA20 $342.45 / SMA50 $343.39, below SMA100 $350.33. 5d 1🔴/4🟢. 60d **−2.6% vs SPY +3.8%**.
- **Friday's bar:** C **$347.86 (+0.87%)**, vol **0.65x**, close pos 23% (lower third) — green day, weak close, opposite of an SOS.
- **Pre-market (CBOE 20:10 ICT): $347.40 (−0.13%) — $0.95 below band low $348.35.** Opens under the band; gap-open into the band is NOT the trigger.
- **Trigger needed (NOT printed):** regular-session green close **≥ $348.35 into band $348.35–356.25** (ideally reclaiming SMA100 $350.33) on **≥1.0x full-session volume**.
- **Planned levels:** Entry $348.35–356.25 · Stop $331.94 · TP $381.81 · **R:R 2.04:1** (risk $16.41 / reward $33.46, breakeven WR 32.9%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — MEDIUM confidence | 5y signal n=96, WR 57.3%, +0.184R, PF 1.44, **t=1.60 (<2, not significant)**, Kelly 17.5%. Recent half n=48 WR 72.9%, +0.578R, **t=3.74, PF 3.41** — edge is recent, not old. MA-pullback = most crowded signal class (logical basis 2/5), 60d −2.6% laggard → **~21/40** |
| 📊 Wyckoff 2.0 | **NEUTRAL → bullish on SOS** | Markup pullback: OBV 60d rising (+258k/day), 30d up/down vol 1.48, in value area, 35.3% retrace — but LH/LL, CMF −0.119, 4 distribution days, Friday closed lower third. Confirm: wide-range green bar, upper-third close, ≥1.0x vol, close ≥$348.35 (>$350.33 ideal) |
| 🧬 Medallion | **NOISE** | Composite **0.0/10**; 11-factor gate **+0.16 FAIL** (<±0.50); SMA stack 20<50; vol 0.65x — would not lift portfolio Sharpe |

- **Expert consensus: WAIT — band not claimed (pre-market under it).** Budget: 1 sh = $16.41 risk = **0.66% of $2,500 ✓ ready**, $0 committed.

### RDDT — two-move setup, band still 6.3% overhead
- **Setup:** above SMA20 $152.45 / SMA50 $154.04, below SMA100 $164.78. 60d **−21.3% vs SPY +3.8%**.
- **Friday's bar:** C **$159.91 (+2.20%)**, vol **1.06x** (✓ volume), close pos 34% — price condition failed: **6.5% below band low $171.11**.
- **Pre-market: $160.30 (+0.06%)** — unchanged picture, still a two-move away.
- **Trigger needed (NOT printed):** TWO-MOVE — rally **into $171.11–179.58**, then green close / SOS bar there on ≥1.0x volume. No market-buy, no front-running the band.
- **Planned levels:** Entry $171.11–179.58 · Stop $156.10 · TP $207.00 · **R:R 2.39:1** (risk $15.01 / reward $35.89, breakeven WR 29.5%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — HIGH confidence | Band 6.3% away — nothing to evaluate. n=30 (WR 63.3%, +0.480R, PF 2.27, t=2.15, Kelly 35.5%) is the best raw set but n=30 is statistically unstable; 60d −21.3% vs SPY = deep laggard, a 2-day bounce has no distinguishable edge |
| 📊 Wyckoff 2.0 | **NEUTRAL — accumulation attempt vs distribution footprint** | SMA50 reclaim = Phase D candidate, capped under SMA100 → range not trend; volume bearish: OBV 60d **falling −2.0M/day**, CMF −0.144, 30d up/down vol **0.67**, LH/LL, −22.7% off 3M high. "If close >$164.78 → expect band test $171+; failure <$154 → reclaim fails" |
| 🧬 Medallion | **NOISE** | Composite **+1.0/10**; gate **+0.10 FAIL**; below SMA100; one 2-day bounce only |

- **Expert consensus: WAIT — price far below band.** Budget: 1 sh = $15.01 risk = **0.60% ✓ ready**, $0 committed.

### GEV — Friday's in-band claim already slipping pre-market
- **Setup:** above SMA20 $958.41 / SMA50 $968.71 / **SMA100 $996.98 (+0.8%)**. HH/HL markup. 60d **−5.7% vs SPY +3.8%**.
- **Friday's bar:** C **$1,004.73 (+0.54%)** — inside band $1,004.62–1,036.80 (by $0.11), close pos **84% (upper third)** — but vol **0.49x**.
- **Pre-market (CBOE): $995.40 (−0.67%) — $9.22 BELOW band low.** The in-band close must be re-earned; this is the same failed pre-market-touch pattern as Oct 9 ($1,008 → close $989).
- **Trigger needed (NOT printed):** close inside band on **≥1.0x volume** + bullish test (SOS). Friday met 2/3 conditions; volume was half requirement and price has now slipped out.
- **Planned levels:** Entry $1,004.62–1,036.80 · Stop $936.39 · TP $1,140.99 · **R:R 2.00:1** (risk $68.23 / reward $136.37 from band low).
- **Sizing veto stands:** 1 sh = $68.23 stop-risk = **2.73% of $2,500, over the 1% cap** ✗ (0 shares affordable).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — sizing veto + decay** — MEDIUM confidence | Best structure of group but not sizeable at 1% risk. fib-dip n=34, WR 64.7%, +0.278R, PF 1.83, t=1.62 — **decayed: 2026 n=16 PF 0.74, recent half n=17 PF 0.86, both negative expectancy.** Score **22/40** |
| 📊 Wyckoff 2.0 | **ACCUMULATION (HH/HL) — SOS attempt, no initiative** | OBV rising (+159k/day), 30d up/down vol **2.06**, only 2 distribution days, +2.0% over 3m VPOC $984.64, 26% retrace, upper-third close. "Close ≥$1,004.62 on ≥1.0x vol → Back-Up resumes toward $1,052; close <$996.82 → range top rejected again" — pre-market $995.40 is on the wrong side of that line |
| 🧬 Medallion | **WEAK SIGNAL** | Composite **+2.0** (best of routed set) but gate **+0.07 FAIL**; vol 0.49x; SMA20<50 → no deploy |

- **Expert consensus: WAIT for ≥1.0x-volume in-band close. Not sizeable within 1% risk — $0.**

### MKSI ⭐ — pre-planned swing MKSI-SW-1, in zone, trigger still absent
- **Setup:** Oct 8 SOW bar (−4.68%, vol 1.03x, 17% close pos), Friday +1.58% to **$264.50** (69% close position off the $256.65 low), vol 0.53x. Below SMA50 $273.48 / SMA100 $310.02, 60d **−26.1% vs SPY**. Regime BOUNCE.
- **Price:** **inside approved swing zone $255–274**, on 1y VPOC $259.92 (+1.8%). **Pre-market: last $262.52, bid/ask $256.90/$264.19 — thin, wide spread; still in zone.**
- **Trigger needed (NOT printed):** Wyckoff **SOS bar + buy-stop above the trigger-candle high** (never market-buy the knife) **AND 11-factor gate ≥ +0.50** (live gate **+0.08 FAIL**). Alternative trigger per plan: daily close > $311.
- **Planned levels (at Friday's close):** single entry full size in $255–274 · SL = actual fill − $19.78 (2×ATR; at $264.50 → **$244.72**) · TP1 = fill +1.5R (**$294.17**) · TP2 = fill +2.5R (**$313.95**) · time stop 2–4wk · SL hit = exit, no averaging. Sizing: 1 sh risk $19.78 = **0.79% of $2,500 ✓**.

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET — conditional/armed** — MEDIUM confidence | Pre-registered plan, fixed $19.78 risk: 5y n=58, WR 63.8%, +0.522R, PF 2.42, **t=3.08 (passes >3 bar)**, Kelly 37.5% → 1% risk ≈ ⅙-Kelly. **Decay flag: recent half n=29 WR 58.6%, +0.144R, t=0.75, PF 1.34.** Counter-trend (60d −26.1%) — payoff must come from the R-multiple plan. VETO: buying the red knife turns a 2.5R plan into an unforced loss |
| 📊 Wyckoff 2.0 | **ACCUMULATION — SOW needs SOS** | HH/HL markup, CMF **+0.199**, OBV rising (+179k/day), 30d up/down **1.91**, 1 distribution day, at VPOC support. Oct 8 = SOW; Friday = test, not strength. "If green SOS prints off $255–274 on ≥1.0x vol → expect SMA50 $274 retest, then $311; close <$255 → zone fails, stand down" |
| 🧬 Medallion | **NOISE (pre-registered process ✓)** | Composite **−2.0** (below SMA50/SMA100); gate **+0.08 FAIL**; vol 0.53x. Plan written BEFORE the move = no curve-fitting — upgrades to STRONG only on printed SOS + passing gate |

- **Expert consensus: WAIT FOR TRIGGER — in zone, buy-stop not hit, gate fails.** Budget: reserved, $0 committed (1 sh = 0.79% ✓).

### OPEN 🟠 — squeeze watch, knife still falling
- **Setup:** DOWNTREND below all SMAs, at 3M-low zone $2.13. RSI 23.9 / Stoch 13.2 oversold. OI P/C 0.17, call walls $3/$4/$5. 60d **−51.2% vs SPY +3.8%**.
- **Friday's bar:** C **$2.22 (−3.06%)**, vol 0.95x, close pos 25% — red, no green close. **Pre-market: $2.22 (+0.07%) — flat, nothing changed.**
- **Trigger needed (NOT printed):** **green close + volume ≥1.3x** off the $2.13 low. Stop if entered: $2.00 (put wall/max pain).
- **Planned levels:** no entry until trigger · stop $2.00 (risk $0.23/sh → 108 sh = 0.99% of $2,500 if it ever qualifies).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET** — HIGH confidence | Falling knife, no structural edge (logical basis 1/5 = mean-reversion hunch); 60d −51.2%; call walls cap any bounce. Score **~15/40** — below the 20 floor |
| 📊 Wyckoff 2.0 | **DISTRIBUTION / markdown — no Spring yet** | LH/LL, −50% below 1y VPOC $4.44, CMF −0.302, OBV 60d **−7.0M/day**, 30d up/down vol 0.45 = Phase E markdown. Spring candidate ONLY if $2.13 holds with SOS + test |
| 🧬 Medallion | **NOISE — NEGATIVE** | Composite **−6.0/10** (worst of set); gate +0.08 FAIL; oversold RSI alone = 1 weak factor |

- **Expert consensus: WAIT — no entry on the knife.** Budget: $0.

## Not Routed This Run

- **ACMR $71.37 (pre-market $70.50, −1.75%)** — 🔴 WAIT, downtrend below all SMAs, 5d 4🔴/1🟢, at 78.6% retrace $71.02 and now pushing through it. Needs green close > SMA20 $74.03. Routine — no expert pass.
- **SPY pre-market $778.69 (+0.02%)** — flat open, no gap regime. CBOE confirms the expert script's SPY bars (Google Finance's SPY page showed a bogus $1,050 — discarded).

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| ZS (15 sh @ $150) | 🚨 **TRIM 5 sh at the open (20:30 ICT)** + TRAILING runner | Friday close $233.73 · **pre-market $234.55 (+0.36%)** | **+55.8% (+$1,255.95, 15 sh)** | **Trim level $216.97 crossed Thursday; journal still shows 15 sh OPEN — trim NOT executed for the 5th consecutive run; open is in ~20 min.** RSI 67.2 / Stoch 98.8 overbought, ATR $9.60 → trail **$214.53**; session high $234.31 = new 3M high. Trim 5 sh @ $234.55 → **+$422.75 realized**; remaining 10 sh trail $214.53 → locked min **+$645.30**; combined **≥ +$1,068 locked** (vs +$967.95 if all 15 sh only trail). Monitor verdict: TRAILING, let profits run |
| AMZN (10 sh @ $259.55) | HOLD (no alert) | Friday close $262.43 · **pre-market $261.98 (−0.21%)** | **+$28.80 (+1.11%)** | Above entry; SL $249.33 intact, TP1 $274.88 ahead, RSI 59.0, gate +0.27 (best of set, still FAIL) — nothing to do |
| NVDU | CLOSED Oct 7 | — | +$1,903.21 lifecycle | Fully closed — no action |

**ZS expert panel on the trim (pre-open):**

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET — trim** (HIGH) | Locking +55.8% into Stoch-98.8 overbought new-3M-high converts expected value into realized; ratchet discipline is the edge-gatekeeper |
| 📊 Wyckoff 2.0 | **Phase E markup — trim into strength** | No SOW bar yet (Friday 84%-range close, +12.25 body), but 6 distribution days/25 and +87.6% above 1y VPOC — distribution risk at highs is exactly where trims pay. Keep 10 sh on the $214.53 trail |
| 🧬 Medallion | **STRONG (risk-reducing)** | Composite **+5.5/10** (only positive confluence in the set), 60d **+53.7%** lone relative-strength winner; trimming cuts single-name variance — the combination, not the single asset, is the portfolio |

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| GOOG | $348.35–356.25 | $331.94 | $381.81 | — | 2.04:1 | **NOT PRINTED** — pre $347.40 under band; Friday closed $347.86, vol 0.65x, lower-third close | **WAIT** — NO BET (t=1.60; H2 t=3.74) · NEUTRAL→SOS · NOISE (gate +0.16) | $0 committed (1sh = 0.66% risk, ready) |
| RDDT | $171.11–179.58 | $156.10 | $207.00 | — | 2.39:1 | **NOT PRINTED** — pre $160.30, 6.3% below band (vol 1.06x ✓, price ✗); two-move | **WAIT** — NO BET (n=30 unstable) · NEUTRAL w/ distribution footprint · NOISE (gate +0.10) | $0 committed (1sh = 0.60%, ready) |
| GEV | $1,004.62–1,036.80 | $936.39 | — | $1,140.99 | 2.00:1 | **NOT PRINTED** — Friday closed INSIDE band but vol **0.49x** (2/3 met); pre-market **$995.40 back under band** | **WAIT** — NO BET (1sh = 2.73% risk > 1% cap; 2026 PF 0.74) · ACCUMULATION · WEAK (gate +0.07) | not sizeable within 1% |
| MKSI ⭐ | $255–274 (buy-stop over SOS high) | fill − $19.78 ($244.72 at Fri close) | fill +1.5R ($294.17) | fill +2.5R ($313.95) | 1.5R / 2.5R | **NOT PRINTED** — pre $262.52 in zone (thin 256.90/264.19), no SOS, gate +0.08 FAIL | **WAIT FOR TRIGGER** — armed conditional BET (t=3.08, H2 decayed) · ACCUMULATION-SOW · NOISE | reserved, $0 committed (1sh = 0.79% ✓) |
| OPEN 🟠 | trigger only (not set) | $2.00 | — | — | — | **NOT PRINTED** — Friday red −3.06% to $2.22, pre flat $2.22; needs green close + ≥1.3x vol | **WAIT** — NO BET (score ~15/40) · DISTRIBUTION · NOISE (−6.0) | $0 |
| ACMR | — | — | — | — | — | 🔴 DOWNTREND — not routed (pre $70.50 −1.75%) | n/a | $0 |

**Entries triggered this run: 0 · Exits to act on: 1 — ZS TRIM 5 sh at Monday's open (~$234.55 pre-market; level $216.97 crossed Thursday, journal still 15 sh OPEN, 5th run with the same recommendation — execute at 20:30 ICT). Capital: $2,500 available, $0 committed.**

Discipline notes:
- **Pre-market ≠ trigger:** all quotes above are 20:06–20:11 ICT indications on zero regular-session volume. Decidable triggers print at today's close (03:00 ICT Tue); MKSI can fill sooner intraday via buy-stop above an SOS candle high.
- **Verified, not assumed:** Friday-bar decision inputs diff-identical across all four runs today; Thorp/Wyckoff/Medallion numbers re-checked against `_entry_0130_expert_out.txt` and the backtest outputs (GOOG n=96 t=1.60 · RDDT n=30 t=2.15 · GEV n=34 t=1.62, 2026 PF 0.74 · MKSI n=58 t=3.08, H2 PF 1.34).
- **ZS trim is the weakest link in the process, not the analysis** — 5 runs in a row with the same recommendation and no fill; the open is now minutes away.
- Thorp litmus vs index (60d): GOOG −2.6%, RDDT −21.3%, GEV −5.7%, MKSI −26.1%, OPEN −51.2% vs SPY +3.8% — every entry candidate is a 60d laggard; they earn risk only through the planned R-multiples, never by assumption. ZS (+53.7%) is the lone relative-strength winner — hence the runner.
- 11-factor gate FAILED on all 7 tickers (GOOG +0.16, RDDT +0.10, GEV +0.07, MKSI +0.08, ZS +0.14, AMZN +0.27, OPEN +0.08 vs ±0.50 threshold): no confluence-based entry is authorized regardless of price location.

---
*Entry Monitor 3-Expert Pipeline · monitor_entries.py (20:00 ICT pre-open run) + CBOE/Google Finance pre-market quotes · Thorp / Wyckoff 2.0 / Medallion · Mon 12 Oct 2026 20:00 ICT*
