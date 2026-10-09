#!/usr/bin/env python3
"""Write entry_monitor_report.md for the 21:00 ICT run (terminal-only overwrite)."""

report = """# 📡 Entry Monitor Report — Fri 09 Oct 2026 21:17 ICT

Run: `monitor_entries.py` (21:09 ICT) — **regular session OPEN, 43 min in (US close 03:00 ICT).** 2 TV feed timeouts (MKSI absent from live output → pre-run 21:00 snapshot + Yahoo used).

**New vs 20:05 run:** GOOG $348.27 now **AT band low $348.35** · RDDT +2.63% → $160.59 · **GEV pre-market band touch FAILED** → back to $989 (below band AND SMA100) · MKSI $259.98 still in zone · **ZS $225.99 = new 3M high, trim still not executed** · OPEN newly flagged (RSI 24.1 squeeze watch).

⚠ **Today's volume ratios (0.03–0.23x) are PARTIAL-SESSION artifacts** — 43 minutes of trading, not a volume signal. No close exists yet ⇒ **no trigger can print this run.**

## 🟢 Entry Triggered

**None — no confirmation trigger printed this run.** The session is 43 minutes old: no close, no full-session volume. GOOG touches its band intraday and MKSI sits in its zone, but neither has a printed bar — both routed as conditional below.

---

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG — live AT the band edge, needs the close
- **Setup:** above SMA20 $342.44 / SMA50 $343.39, below SMA100 $350.33. RSI 46.9, 5d 1🔴/4🟢. 60d −1.3% vs SPY +3.7%.
- **Price:** live **$348.27 (+0.80%)** — $0.08 below band low $348.35, reclaiming toward SMA100.
- **Trigger needed (NOT printed):** regular-session **green close ≥ $348.35 into band $348.35–$356.25** (ideally reclaiming SMA100 $350.33) on **≥1.0x full-session volume**. 43-min intraday touch ≠ trigger.
- **Planned levels:** Entry $348.35–$356.25 · Stop $331.99 · TP $381.81 · R:R ≈ 2.05:1 (risk $16.36 / reward $33.46, breakeven WR 33%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — confidence HIGH | Expectancy lives in a *printed* trigger: MA-pullback is the most crowded signal class (logical basis 2/5), 60d −1.3% vs SPY +3.7% = laggard; score ~21/40. |
| 📊 Wyckoff 2.0 | **NEUTRAL → bullish on SOS** | Shallow low-vol pullback in markup, no SOW; today's bar rallies into SMA100 from below. Confirm: wide-range green bar, upper-third close, ≥1x vol, close ≥$348.35 (>$350.33 ideal). |
| 🧬 Medallion | **NOISE** | 43-min partial bar, vol 0.09x partial, single market — fails initiative test; would not lift portfolio Sharpe. |

- **Expert consensus: WAIT — trigger not printed.** Budget: 1 share = $16.36 risk = **0.65% of $2,500 ✓ ready**, $0 committed.

### RDDT — bounce strong, band still 6.5% overhead (two-move)
- **Setup:** above SMA20 $152.48 / SMA50 $154.06, below SMA100 $164.79. RSI 52.0, 5d 1🔴/4🟢 (+8.8% 5d). In Fib 61.8% zone $160–165. 60d −13.1% vs SPY +3.7%.
- **Price:** live **$160.59 (+2.63%)** — still **6.5% below band low $171.11.**
- **Trigger needed (NOT printed):** TWO-MOVE — rally **into $171.11–$179.58**, then green close / SOS bar there on ≥1.0x volume. No market-buy, no front-running the band.
- **Planned levels:** Entry $171.11–$179.58 · Stop $156.10 · TP $207.00 · R:R ≈ 2.39:1 (risk $15.01 / reward $35.89, breakeven WR 30%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — confidence HIGH | Band 6.5% away — nothing to evaluate; 60d −13.1% vs SPY = deep laggard, a 5-day bounce has no statistically distinguishable edge. |
| 📊 Wyckoff 2.0 | **NEUTRAL** (accumulation attempt) | SMA50 reclaimed = Phase D candidate, but capped under SMA100 → range, not trend. "If close >$164.79 → expect band test $171+; failure <$154 → reclaim fails." |
| 🧬 Medallion | **WEAK SIGNAL** | +8.8% 5d is one period only; below SMA100, partial volume — fails multi-period/multi-market checks. |

- **Expert consensus: WAIT — price far below band.** Budget: 1 share = $15.01 risk = **0.60% ✓ ready**, $0 committed.

### GEV ⚠ — band touch FAILED, sizing veto stands
- **Setup:** above SMA20 $957.60 / SMA50 $968.39, back **below SMA100 $996.82.** RSI 62.6, 5d 2🔴/3🟢, struct 20d HH/HL, 60d −4.8% vs SPY +3.7%.
- **Price:** pre-market **$1,008 INSIDE band → live $989.06 (−1.08%) — rejected $16 below band low $1004.62 and below SMA100.**
- **Trigger needed (NOT printed):** regular-session **close inside $1,004.62–$1,036.80 on ≥1.0x volume** + bullish test (SOS). The pre-market touch already failed — the bar must earn the band again.
- **Planned levels:** Entry $1,004.62–$1,036.80 · Stop $936.46 · TP $1,140.99 · R:R ≈ 2.00:1 (risk $68.16 / reward $136.37 from band low).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — sizing veto** — confidence MEDIUM | Best structure of group but min 1 share = $68.16 stop-risk = **2.73% of $2,500, over the 1% cap** ✗. Carried stats: GEV fib-dip n=34, WR 64.7%, +0.278R, t=1.62 (<3.0), 2026 GEV negative (PF 0.74) → decayed. Score 22/40. |
| 📊 Wyckoff 2.0 | **NEUTRAL** — rejection logged | Intraday fail at SMA100/band = supply still active up there. "If close <$996.82 → range top rejected, alternate = short-term distribution; if close ≥$1,004.62 on ≥1x vol → Back-Up resumes." |
| 🧬 Medallion | **WEAK SIGNAL** | HH/HL structure + RSI 62 are only 2 factors; failed band test + partial vol + t<3.0 on the signal itself → no deploy. |

- **Expert consensus: WAIT for close-in-band + SOS. Not sizeable within 1% risk — $0.**

### MKSI ⭐ — pre-planned swing MKSI-SW-1, in zone, no trigger
- **Setup:** −4.68% knife day (Oct 8), today −0.9% (live $259.98 / $258.02 Yahoo). RSI 50.9, Stoch 25.0 (reset), below SMA50 $273.38 / SMA100 $309.98, 5d 3🔴/2🟢 (−7.6% 5d), 60d −22.2%. Regime BOUNCE. TV feed timed out this run — values from pre-run snapshot + Yahoo.
- **Price:** **$259.98 — inside approved swing zone $255–274** (single entry full size).
- **Trigger needed (NOT printed):** Wyckoff **SOS bar + buy-stop above the trigger candle high** (never market-buy the knife) AND **11-factor confluence gate ≥ +0.50** at trigger (untested — no trigger). Alternative trigger per plan: daily close > $311. Red partial bar today = no SOS.
- **Planned levels:** single entry full size in $255–274 · SL = actual fill − $19.78 (2×ATR) · TP1 = fill +1.5R · TP2 = fill +2.5R · time stop 2–4wk · SL hit = exit, no averaging. Example at fill $260: SL $240.22 · TP1 $289.67 · TP2 $309.45.

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET — conditional/armed** — confidence MEDIUM | Pre-registered plan with fixed $19.78 risk = clean expectancy: breakeven WR 40% at 1.5R, EV +0.25R at 50% WR, Kelly 16.7% → 1% risk ≈ ⅙-Kelly. Honest flag: 60d −22.2% vs SPY +3.7% — **counter-trend**, payoff must come from the R-multiple plan. VETO: buying the red knife converts a 2.5R plan into an unforced loss. |
| 📊 Wyckoff 2.0 | **NEUTRAL → bullish on SOS** | Markup pullback into zone + Stoch reset + SMA20 test = watch-for-Spring / LPS. Oct 8 red bar = SOW, today's partial bar red = still no SOS. "If green SOS prints off $255–274 on ≥1x vol → expect SMA50 $274 retest, then $311; close <$255 → zone fails, stand down." |
| 🧬 Medallion | **WEAK SIGNAL (pre-registered)** | Plan written BEFORE the move = no curve-fitting — good process. Zone + Stoch reset = 2 factors; red close + below-SMA50 + partial vol fails confirmation. Upgrades to STRONG only on printed SOS + passing gate. |

- **Expert consensus: WAIT FOR TRIGGER — in zone, buy-stop not hit, gate untested.** Budget: reserved, $0 committed (1 sh = $19.78 risk = 0.79% ✓).

### OPEN 🟠 — squeeze watch, knife not caught
- **Setup:** DOWNTREND, below all SMAs (20/50/100 = $2.48/$3.04/$3.79), struct 20d LH/LL, at 3M low zone $2.13. RSI 24.1 (oversold), Stoch 14.7, MACD hist 0.01. 60d −51.4% vs SPY +3.7%. OI P/C 0.17, call walls $3/$4/$5 overhead.
- **Price:** live **$2.23 (−2.62%)** — no green close, vol partial 0.1x.
- **Trigger needed (NOT printed):** **green close + volume ≥1.3x (full session)** off the $2.13 low. Stop if entered: $2.00 (put wall/max pain).
- **Planned levels:** no entry until trigger · trigger-print entry ≈ $2.23–2.30 · Stop $2.00 (risk $0.23/sh → 108 sh = 0.99% of $2,500 if it ever qualifies) · TP: prior-session VPOC/first HVN — undefined until base forms.

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET** — confidence HIGH | Falling knife with no structural edge (logical basis 1/5 = mean-reversion hunch); 60d −51.4%; call walls $3/$4/$5 cap any bounce. Score ~15/40 — below the 20 floor. |
| 📊 Wyckoff 2.0 | **DISTRIBUTION / markdown — no Spring yet** | LH/LL, price hugging 3M low = Phase E markdown. Spring candidate ONLY if $2.13 holds with SOS + test. "If green close ≥1.3x vol off $2.13 → watch Spring/test; close <$2.13 → continuation, stand aside." |
| 🧬 Medallion | **NOISE** | Oversold RSI alone = 1 weak factor, partial vol, single market — would not lift portfolio Sharpe. |

- **Expert consensus: WAIT — no entry on the knife.** Budget: $0 (trigger far from printing).

---

## Not Routed This Run

- **ACMR $70.34** — 🔴 WAIT, downtrend below all SMAs, 5d 5🔴/0🟢, Stoch 8.6, at 78.6% retrace $71.02. Needs green close > SMA20 $73.97. Routine — no expert pass.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| ZS | 🚨 **TRIM 5 sh NOW** + TRAILING runner | live **$225.99** (monitor $224.90) | **+50.7% (+$1,140, 15 sh)** | **Level $216.97 crossed at open and price ran $9 higher — journal still shows 15 sh OPEN: trim NOT executed.** New 3M high intraday; Stoch 100 overbought. Trim 5 sh → ≈ +$380 realized; remaining 10 sh trail **$207.04** (2×ATR) → locked ≥ +$570; combined ≥ **+$950 locked**. Runner rides the trail only. |
| AMZN | HOLD | live $258.40 | −0.4% (entry $259.55) | Above SL $249.33, below TP1 $274.88 — no signal this run. |
| NVDU | CLOSED Oct 7 | — | +$1,903.21 lifecycle | Fully closed — no action |

**ZS expert panel on the trim (updated 21:17):**
| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET — trim** (HIGH) | Locking +50% into Stoch-100 overbought new-3M-high converts expected value into realized; ratchet discipline is the edge-gatekeeper. |
| 📊 Wyckoff 2.0 | **Phase E markup — trim into strength** | No SOW yet, but distribution risk at highs is exactly where trims pay. Keep 10 sh on the $207.04 trail as the runner. |
| 🧬 Medallion | **STRONG (risk-reducing)** | 60d **+53.6%** lone relative-strength winner; trimming cuts single-name variance — the combination, not the single asset, is the portfolio. |

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| GOOG | $348.35–356.25 | $331.99 | $381.81 | — | ~2.05:1 | **NOT PRINTED** (live $348.27 AT band edge; 43-min bar, vol 0.09x partial) | **WAIT** — NO BET · NEUTRAL→SOS · NOISE | $0 committed (1sh = 0.65% risk, ready) |
| RDDT | $171.11–179.58 | $156.10 | $207.00 | — | ~2.39:1 | **NOT PRINTED** (live $160.59, 6.5% below band; two-move) | **WAIT** — NO BET · NEUTRAL · WEAK | $0 committed (1sh = 0.60%, ready) |
| GEV ⚠ | $1,004.62–1,036.80 | $936.46 | — | $1,140.99 | ~2.00:1 | **NOT PRINTED** (pre $1,008 in band → live $989 REJECTED back below band) | **WAIT** — NO BET (1sh = 2.73% risk > 1% cap) · rejection · WEAK | not sizeable within 1% |
| MKSI ⭐ | $255–274 (buy-stop over SOS high) | fill − $19.78 | fill +1.5R (~$290) | fill +2.5R (~$309) | 1.5R / 2.5R | **NOT PRINTED** ($259.98 in zone; no SOS bar, gate untested, TV feed timeout) | **WAIT FOR TRIGGER** — armed conditional BET | reserved, $0 committed |
| OPEN 🟠 | trigger only (not set) | $2.00 | — | — | — | **NOT PRINTED** (needs green close + ≥1.3x vol; RSI 24.1) | **WAIT** — NO BET · DISTRIBUTION · NOISE | $0 |
| ACMR | — | — | — | — | — | 🔴 DOWNTREND — not routed | n/a | $0 |

**Entries triggered this run: 0 · Exits to act on: 1 — ZS TRIM 5 sh now at ~$226 (level $216.97 crossed, journal still 15 sh). Capital: $2,500 available, $0 committed.**

Discipline notes:
- Partial session ≠ trigger: volume ratios 0.03–0.23x are artifacts of 43 minutes of trading; triggers can only print on today's close (03:00 ICT) — the next run sees the full bar.
- ZS is the only actionable item NOW: trim 5 sh into ~$226, keep 10 sh on the $207.04 trail. The level was crossed at open without a fill.
- Thorp litmus vs index: 60d — GOOG −1.3%, RDDT −13.1%, GEV −4.8%, MKSI −22.2%, OPEN −51.4% vs SPY +3.7%. Every entry candidate is a 60d laggard; they earn risk only through the planned R-multiples, never by assumption. ZS (+53.6%) is the lone relative-strength winner — hence the runner.

---
*Entry Monitor 3-Expert Pipeline · monitor_entries.py · Thorp / Wyckoff 2.0 / Medallion · 09 Oct 2026 21:17 ICT*
"""

path = "/root/.hermes/profiles/trader/scripts/entry_monitor_report.md"
with open(path, "w") as f:
    f.write(report)
print("wrote %d bytes -> %s" % (len(report), path))
