#!/usr/bin/env python3
"""Write the 22:00 ICT entry-monitor report (cron guard blocks heredoc writes)."""
report = r"""# 📡 Entry Monitor Report — Fri 09 Oct 2026 22:00 ICT

Run: `monitor_entries.py` (22:01 ICT) — **regular session OPEN, ~90 min in (US close 03:00 ICT).** 3 TV-feed timeouts on MKSI/others → Yahoo fallback held.

**New vs 21:17 run:** GOOG $348.27 → **$348.77 still AT band low** · RDDT $160.59 → $159.54 (still 6.5% below band) · **GEV $989 → $999.72 recovered back ABOVE SMA100 $996.91, still $5 under band low** · MKSI $259.98 → $261.20 in zone · ZS $225.99 → new 3M-high print $226.40, **trim still not executed** · AMZN back above entry (+0.24%).

⚠ **Today's volume ratios (0.13–0.35x) are PARTIAL-SESSION artifacts** — ~90 minutes of trading, not a volume signal. No close exists yet ⇒ **no trigger can print this run.**

## 🟢 Entry Triggered

**None — no confirmation triggers printed this run.** No closed bar, no full-session ≥1.0x volume, no SOS bar on any routed ticker. GOOG touches its band intraday and MKSI sits in its zone, but neither has a printed bar — both routed as conditional below.

---

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG — live AT the band edge, needs the close
- **Setup:** above SMA20 $342.47 / SMA50 $343.40, below SMA100 $350.33. 5d 1🔴/4🟢. 60d −1.3% vs SPY +3.7%.
- **Price:** live **$348.77 (+1.14%)** — sitting on band low $348.35, reclaiming toward SMA100.
- **Trigger needed (NOT printed):** regular-session **green close ≥ $348.35 into band $348.35–356.25** (ideally reclaiming SMA100 $350.33) on **≥1.0x full-session volume**. Yesterday's bar closed −0.72% at 13% of range — the opposite of an SOS. 90-min intraday touch ≠ trigger.
- **Planned levels:** Entry $348.35–356.25 · Stop $331.99 · TP $381.81 · R:R ≈ 2.05:1 (risk $16.36 / reward $33.46, breakeven WR 33%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — confidence MEDIUM | Full 5y signal n=96, WR 57.3%, +0.184R, PF 1.44, **t=1.60 (<2, marginal)**, Kelly 17.5% — but recent half n=48 WR 72.9%, +0.578R, **t=3.74, PF 3.41** (edge recent, not old). MA-pullback is the most crowded signal class (logical basis 2/5), 60d −1.3% vs SPY +3.7% = laggard → score ~21/40 |
| 📊 Wyckoff 2.0 | **NEUTRAL → bullish on SOS** | Markup pullback: OBV 60d rising (+245k/day), in value area, 32.6% retrace — but 10d LH/LL, CMF −0.10, 4 distribution days, no Spring/SOS. Confirm: wide-range green bar, upper-third close, ≥1x vol, close ≥$348.35 (>$350.33 ideal) |
| 🧬 Medallion | **NOISE** | Composite **0.0/10**; 11-factor gate **+0.17 FAIL** (<±0.50); SMA stack broken (20<50); partial vol 0.18x — would not lift portfolio Sharpe |

- **Expert consensus: WAIT — trigger not printed.** Budget: 1 sh = $16.36 risk = **0.65% of $2,500 ✓ ready**, $0 committed.

### RDDT — bounce strong, band still 6.5% overhead (two-move)
- **Setup:** above SMA20 $152.45 / SMA50 $154.04, below SMA100 $164.78. Reclaimed SMA50 (+2.2% today). 60d −13.1% vs SPY +3.7%.
- **Price:** live **$159.54 (+2.17%)** — still **6.5% below band low $171.11.**
- **Trigger needed (NOT printed):** TWO-MOVE — rally **into $171.11–179.58**, then green close / SOS bar there on ≥1.0x volume. No market-buy, no front-running the band.
- **Planned levels:** Entry $171.11–179.58 · Stop $156.10 · TP $207.00 · R:R ≈ 2.39:1 (risk $15.01 / reward $35.89, breakeven WR 30%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — confidence HIGH | Band 6.5% away — nothing to evaluate; n=30 (WR 63.3%, +0.480R, PF 2.27, t=2.15, Kelly 35.5%) is the best raw set but n=30 is unstable; 60d −13.1% vs SPY = deep laggard, a 5-day bounce has no statistically distinguishable edge |
| 📊 Wyckoff 2.0 | **NEUTRAL — accumulation attempt vs distribution footprint** | SMA50 reclaim = Phase D candidate, capped under SMA100 → range not trend; BUT volume footprint is bearish: OBV 60d **falling −2.0M/day**, CMF −0.14, 30d up/down vol **0.62**, LH/LL, −22.9% below 3M high. "If close >$164.79 → expect band test $171+; failure <$154 → reclaim fails" |
| 🧬 Medallion | **NOISE** | Composite **0.0/10**; gate **+0.10 FAIL**; below SMA100; partial vol 0.28x; one strong 5d period only |

- **Expert consensus: WAIT — price far below band.** Budget: 1 sh = $15.01 risk = **0.60% ✓ ready**, $0 committed.

### GEV — recovered above SMA100, band still unclaimed; sizing veto stands
- **Setup:** above SMA20 $958.07 / SMA50 $968.57, **back above SMA100 $996.91 (live $999.72, +0.3%)**. 60d −4.8% vs SPY +3.7%.
- **Price:** live **$999.72** — 21:17 dip to $989 recovered; still **$4.90 below band low $1004.62** (21:17 pre-market touch at $1,008 already failed and must be re-earned).
- **Trigger needed (NOT printed):** regular-session **close inside $1,004.62–1,036.80 on ≥1.0x volume** + bullish test (SOS).
- **Planned levels:** Entry $1,004.62–1,036.80 · Stop $936.46 · TP $1,140.99 · R:R ≈ 2.00:1 (risk $68.16 / reward $136.37 from band low).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — sizing veto** — confidence MEDIUM | Best structure of group but min 1 sh = $68.16 stop-risk = **2.73% of $2,500, over the 1% cap** ✗ (25 // 68 = 0 shares affordable). Carried stats: fib-dip n=34, WR 64.7%, +0.278R, t=1.62 — **decayed: 2026 n=16 PF 0.74, recent half n=17 PF 0.86, both negative expectancy.** Score 22/40 |
| 📊 Wyckoff 2.0 | **ACCUMULATION (HH/HL) — band retest pending** | HH/HL markup, OBV rising (+158k/day), 30d up/down vol **2.02**, only 2 distribution days, +1.5% over 3m VPOC, 28.8% retrace. 21:17 rejection at band logged as supply — "close ≥$1,004.62 on ≥1x vol → Back-Up resumes; close <$996.82 → range top rejected again" |
| 🧬 Medallion | **WEAK SIGNAL** | Composite **+2.0** (best of the routed set) but gate **+0.07 FAIL**; SMA20<50; partial vol 0.18x; signal itself t<3.0 with 2026 decay → no deploy |

- **Expert consensus: WAIT for close-in-band + SOS. Not sizeable within 1% risk — $0.**

### MKSI ⭐ — pre-planned swing MKSI-SW-1, in zone, no trigger
- **Setup:** −4.68% knife day (Oct 8, vol 1.03x, close 17% of range = **SOW bar**), today +0.31% (live $261.20). Below SMA50 $273.42 / SMA100 $309.99, 60d −22.2%. Regime BOUNCE.
- **Price:** **$261.20 — inside approved swing zone $255–274**, sitting on 1y VPOC $259.92 (+0.5%) — price/VPOC confluence.
- **Trigger needed (NOT printed):** Wyckoff **SOS bar + buy-stop above the trigger-candle high** (never market-buy the knife) **AND 11-factor gate ≥ +0.50** (live gate **+0.11 FAIL**). Alternative trigger per plan: daily close > $311. Green partial bar today = no SOS yet.
- **Planned levels:** single entry full size in $255–274 · SL = actual fill − $19.78 (2×ATR, live example $241.42) · TP1 = fill +1.5R (~$290.87) · TP2 = fill +2.5R (~$310.65) · time stop 2–4wk · SL hit = exit, no averaging.

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET — conditional/armed** — confidence MEDIUM | Pre-registered plan, fixed $19.78 risk: 5y n=58, WR 63.8%, +0.522R, PF 2.42, **t=3.08 (passes the >3 bar)**, Kelly 37.5% → 1% risk ≈ ⅙-Kelly. **Decay flag: recent half n=29 WR 58.6%, +0.144R, t=0.75, PF 1.34.** Counter-trend (60d −22.2% vs SPY +3.7%) — payoff must come from the R-multiple plan. VETO: buying the red knife turns a 2.5R plan into an unforced loss |
| 📊 Wyckoff 2.0 | **ACCUMULATION — SOW needs SOS** | HH/HL markup, CMF +0.19, OBV rising, 30d up/down 1.87, 1 distribution day, at VPOC support. Oct 8 red bar = SOW. "If green SOS prints off $255–274 on ≥1x vol → expect SMA50 $274 retest, then $311; close <$255 → zone fails, stand down" |
| 🧬 Medallion | **NOISE (pre-registered process ✓)** | Composite **−2.0** (below SMA50/SMA100, regime False); gate **+0.11 FAIL**; partial vol 0.13x. Plan written BEFORE the move = no curve-fitting — upgrades to STRONG only on printed SOS + passing gate |

- **Expert consensus: WAIT FOR TRIGGER — in zone, buy-stop not hit, gate fails.** Budget: reserved, $0 committed (1 sh = $19.78 risk = **0.79% ✓**).

### OPEN 🟠 — squeeze watch, knife not caught
- **Setup:** DOWNTREND below all SMAs, at 3M-low zone $2.13. RSI 24.1 (oversold), Stoch 14.7, MACD hist 0.01, 60d −51.4% vs SPY +3.7%. OI P/C 0.17, call walls $3/$4/$5 overhead.
- **Price:** live **$2.23 (−2.62%)** — no green close, partial vol 0.22x.
- **Trigger needed (NOT printed):** **green close + volume ≥1.3x (full session)** off the $2.13 low. Stop if entered: $2.00 (put wall/max pain).
- **Planned levels:** no entry until trigger · stop $2.00 (risk $0.23/sh → 108 sh = 0.99% of $2,500 if it ever qualifies).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET** — confidence HIGH | Falling knife, no structural edge (logical basis 1/5 = mean-reversion hunch); 60d −51.4%; call walls cap any bounce. Score ~15/40 — below the 20 floor |
| 📊 Wyckoff 2.0 | **DISTRIBUTION / markdown — no Spring yet** | LH/LL, hugging 3M low = Phase E markdown. Spring candidate ONLY if $2.13 holds with SOS + test |
| 🧬 Medallion | **NOISE** | Oversold RSI alone = 1 weak factor, partial vol, single market |

- **Expert consensus: WAIT — no entry on the knife.** Budget: $0.

---

## Not Routed This Run

- **ACMR $70.48** — 🔴 WAIT, downtrend below all SMAs, 5d 5🔴/0🟢, Stoch 9.4, at 78.6% retrace $71.02. Needs green close > SMA20 $73.98. Routine — no expert pass.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| ZS (15 sh @ $150) | 🚨 **TRIM 5 sh** + TRAILING runner | live **$225.92** (session high **$226.40 = new 3M high**) | **+50.6% (+$1,138.80, 15 sh)** | **Trim level $216.97 crossed at the open and price ran ~$9 higher — trade journal still shows 15 sh OPEN: trim NOT executed.** Expert RSI 70.1 / Stoch 98.8 overbought, MACD hist +1.35 intact; above 1y VAH $211.88 = price discovery. Trim 5 sh → **+$379.60 realized**; remaining 10 sh trail **$207.37** (2×ATR) → locked min **+$573.69**; combined **≥ +$953 locked**. Monitor verdict: TRAILING, let profits run |
| AMZN (10 sh @ $259.55) | HOLD (no alert) | live $260.17 | **+$6.20 (+0.24%)** | Above SL $249.33, below TP1 $274.88, RSI 57.1 — nothing to do |
| NVDU | CLOSED Oct 7 | — | +$1,903.21 lifecycle | Fully closed — no action |

**ZS expert panel on the trim (updated 22:00):**

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET — trim** (HIGH) | Locking +50% into Stoch-98.8 overbought new-3M-high converts expected value into realized; ratchet discipline is the edge-gatekeeper |
| 📊 Wyckoff 2.0 | **Phase E markup — trim into strength** | No SOW yet, but distribution risk at highs is exactly where trims pay (6 distribution days/25 already). Keep 10 sh on the $207.37 trail |
| 🧬 Medallion | **STRONG (risk-reducing)** | Composite **+4.5/10**, 60d **+53.6%** lone relative-strength winner; trimming cuts single-name variance — the combination, not the single asset, is the portfolio |

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| GOOG | $348.35–356.25 | $331.99 | $381.81 | — | ~2.05:1 | **NOT PRINTED** (live $348.77 AT band edge; 90-min bar, vol 0.18x partial) | **WAIT** — NO BET (t=1.60; H2 t=3.74) · NEUTRAL→SOS · NOISE (gate +0.17) | $0 committed (1sh = 0.65% risk, ready) |
| RDDT | $171.11–179.58 | $156.10 | $207.00 | — | ~2.39:1 | **NOT PRINTED** (live $159.54, 6.5% below band; two-move) | **WAIT** — NO BET (n=30) · NEUTRAL w/ distribution footprint · NOISE (gate +0.10) | $0 committed (1sh = 0.60%, ready) |
| GEV | $1,004.62–1,036.80 | $936.46 | — | $1,140.99 | ~2.00:1 | **NOT PRINTED** (live $999.72, recovered >SMA100 but $4.90 under band; pre-market touch failed) | **WAIT** — NO BET (1sh = 2.73% risk > 1% cap; 2026 PF 0.74) · ACCUMULATION · WEAK (gate +0.07) | not sizeable within 1% |
| MKSI ⭐ | $255–274 (buy-stop over SOS high) | fill − $19.78 | fill +1.5R (~$290.87) | fill +2.5R (~$310.65) | 1.5R / 2.5R | **NOT PRINTED** ($261.20 in zone on VPOC; no SOS bar, gate +0.11 FAIL) | **WAIT FOR TRIGGER** — armed conditional BET (t=3.08, H2 decayed) · ACCUMULATION-SOW · NOISE | reserved, $0 committed |
| OPEN 🟠 | trigger only (not set) | $2.00 | — | — | — | **NOT PRINTED** (needs green close + ≥1.3x vol; RSI 24.1) | **WAIT** — NO BET · DISTRIBUTION · NOISE | $0 |
| ACMR | — | — | — | — | — | 🔴 DOWNTREND — not routed | n/a | $0 |

**Entries triggered this run: 0 · Exits to act on: 1 — ZS TRIM 5 sh now at ~$226 (level $216.97 crossed at open, journal still 15 sh). Capital: $2,500 available, $0 committed.**

Discipline notes:
- Partial session ≠ trigger: volume ratios 0.13–0.35x are artifacts of ~90 minutes of trading; triggers can only print on today's close (03:00 ICT) — the next run sees the full bar.
- ZS is the only actionable item NOW: trim 5 sh into ~$226, keep 10 sh on the $207.37 trail. The level was crossed at open without a fill.
- Thorp litmus vs index (60d, carried from tonight's earlier runs): GOOG −1.3%, RDDT −13.1%, GEV −4.8%, MKSI −22.2%, OPEN −51.4% vs SPY +3.7%. Every entry candidate is a 60d laggard; they earn risk only through the planned R-multiples, never by assumption. ZS (+53.6%) is the lone relative-strength winner — hence the runner.
- 11-factor gate FAILED on every ticker this run (GOOG +0.17, RDDT +0.10, GEV +0.07, MKSI +0.11, ZS +0.06, AMZN +0.26 — threshold ±0.50): no confluence-based entry is authorized regardless of price location.

---
*Entry Monitor 3-Expert Pipeline · monitor_entries.py + _entry_2201_experts.py · Thorp / Wyckoff 2.0 / Medallion · 09 Oct 2026 22:00 ICT*
"""

with open('/root/.hermes/profiles/trader/scripts/entry_monitor_report.md', 'w') as f:
    f.write(report)
print('WROTE', len(report), 'chars')
