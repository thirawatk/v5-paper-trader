#!/usr/bin/env python3
"""Write entry_monitor_report.md for the 20:00 ICT run (terminal-only overwrite)."""

report = """# 📡 Entry Monitor Report — Fri 09 Oct 2026 20:05 ICT

Run: `monitor_entries.py` (20:01 ICT) + pre-market feed. **Pre-open briefing — US opens 20:30 ICT (09:30 ET), 25 min after this run.**

**New vs 04:00 run:** pre-market gaps across the board — SPY +0.34%, GOOG $347.96 (at band edge), RDDT +3.0%, **GEV $1,008 = inside entry band**, MKSI $265 (in zone, bouncing), **ZS $222 = above trim $216.97 AND above 3M high $218.82**. Regular session has not opened — pre-market prints are not triggers (v=0).

## 🟢 Entry Triggered

**None — no confirmation trigger printed this run.** No regular-session bar exists yet today; pre-market quotes don't count (no volume, no close). GOOG is $0.39 below its band and GEV prints *inside* its band pre-market — both can trigger at today's open, routed below as conditional.

---

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG — pre-market at the band edge
- **Setup:** above SMA20 $341.83 / SMA50 $343.11, below SMA100 $350.78. RSI 50.4 (neutral), vol 0.8x. 5d: 1🔴/4🟢.
- **Price:** $344.86 close (Oct 8) · **pre-market $347.96 (+0.90%) — $0.39 below band low $348.35.**
- **Trigger needed (NOT printed):** regular-session **green close ≥ $348.35 into band $348.35–$356.25** (ideally reclaiming SMA100 $350.78) on **≥1.0x volume**. Gap-open into the band is NOT the trigger — wait for the close.
- **Planned levels:** Entry $348.35–$356.25 · Stop $331.75 · TP $381.81 · R:R ≈ 2.0:1 (risk $16.60 / reward $33.46, breakeven WR 33%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — confidence HIGH | Pre-gap puts price at the band, but expectancy lives in a *printed* trigger: MA-pullback is the most crowded signal class (logical basis 2/5), 60d −6.9% vs SPY +2.5% = laggard — entry must prove relative strength, not assume it. |
| 📊 Wyckoff 2.0 | **NEUTRAL → bullish on SOS** | Shallow, low-volume pullback inside markup — no SOW. Pre-gap toward SMA100 = candidate SOS. Confirm: wide-range green bar, upper-third close, ≥1x vol, close ≥$348.35. |
| 🧬 Medallion | **NOISE** | Pre-market prints on zero volume, 0.8x regular vol, single market — fails initiative test; would not lift portfolio Sharpe. |

- **Expert consensus: WAIT — trigger not printed.** Budget: 1 share = $16.60 risk = **0.66% of $2,500 ✓ ready**, $0 committed.

### RDDT — strong pre-market, band still 6% overhead
- **Setup:** reclaimed SMA50 $154.41 (+2.46%), above SMA20 $152.34, below SMA100 $164.77. RSI 55.6, vol 0.98x. 5d: 2🔴/3🟢.
- **Price:** $156.47 close · **pre-market $161.10 (+2.96%) — still 6.2% below band low $171.11.**
- **Trigger needed (NOT printed):** TWO-MOVE — price must first rally **into $171.11–$179.58**, then print a green close / SOS bar there on ≥1.0x volume. No market-buy, no front-running the band.
- **Planned levels:** Entry $171.11–$179.58 · Stop $155.88 · TP $207.00 · R:R ≈ 2.4:1 (risk $15.23 / reward $35.89, breakeven WR 30%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — confidence HIGH | Band 6.2% away — nothing to evaluate yet. 20d +0.7% vs SPY +2.1% = no relative strength; a single gap has no statistically distinguishable edge. |
| 📊 Wyckoff 2.0 | **NEUTRAL** (accumulation attempt) | SMA50 reclaim = Phase D candidate, but capped under SMA100 → range, not trend. Pre-gap needs a Back-Up test of the reclaim before continuation. |
| 🧬 Medallion | **WEAK SIGNAL** | +2.96% pre on zero volume = one thin data point; fails multi-period checks. |

- **Expert consensus: WAIT — price far below band.** Budget: 1 share = $15.23 risk = **0.61% ✓ ready**, $0 committed.

### GEV ⚠ — pre-market INSIDE the band, sizing veto stands
- **Setup:** above SMA20 $956.04 / SMA50 $968.25 / SMA100 $997.05 — only setup above all three SMAs. RSI 68.1 (extended), vol 1.03x. 5d: 1🔴/4🟢.
- **Price:** $999.35 close · **pre-market $1,008.00 (+0.87%) — INSIDE band $1,004.62–$1,036.80.**
- **Trigger needed (NOT printed):** regular-session **close inside $1,004.62–$1,036.80 on ≥1.0x volume** + bullish test (SOS). Pre-market touch ≠ trigger.
- **Planned levels:** Entry $1,004.62–$1,036.80 · Stop $937.06 · TP $1,140.99 · R:R ≈ 2.0:1 (risk $67.56 / reward $136.37 from band low).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — sizing veto** — confidence MEDIUM | Best structure (20d +8.2%, RS leader) but min 1 share = $67.56 stop-risk = **2.7% of $2,500, over the 1% cap**; RSI 68 entering = negative drift premium. BET only if sizing solved (budget exception or wider structural stop). |
| 📊 Wyckoff 2.0 | **NEUTRAL → bullish on Back-Up confirm** | Trend context — pullback from $1,052.78 into Fib + SMA100 confluence is the Back-Up we wanted. "If regular close holds ≥$1,004.62 → expect continuation to $1,036+; failure <$997 → setup dead, alternate = short-term distribution." |
| 🧬 Medallion | **WEAK SIGNAL** (best of group) | 3 confluence factors (SMA alignment, vol ≥1x, Fib zone) — but RSI 68 + single market, overfit risk high. |

- **Expert consensus: WAIT for close-in-band + SOS. Not sizeable within 1% risk — $0.**

### MKSI ⭐ — pre-planned swing MKSI-SW-1, in zone, no trigger
- **Setup:** −4.68% knife day (Oct 8), RSI 56.3, Stoch 26.1 (reset), vol 1.03x, tested SMA20 $260.00. Regime BOUNCE. Down move on average volume = no climax selling.
- **Price:** $260.38 close · **pre-market $265.00 (+1.77%) — inside approved swing zone $255–274, bouncing off SMA20.**
- **Trigger needed (NOT printed):** Wyckoff **SOS bar + buy-stop above the trigger candle high** (never market-buy the knife) AND **11-factor confluence gate ≥ +0.50** at trigger (not yet evaluated — no trigger). Alternative trigger per plan: daily close > $311.
- **Planned levels:** single entry full size in $255–274 · SL = actual fill − $19.78 (2×ATR) · TP1 = fill +1.5R · TP2 = fill +2.5R · time stop 2–4wk · SL hit = exit, no averaging. Example at fill $265: SL $245.22 · TP1 $294.67 · TP2 $314.45.

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET — conditional/armed** — confidence MEDIUM | Pre-registered plan with fixed $19.78 risk = clean expectancy math: breakeven WR 40% at 1.5R, EV +0.25R at 50% WR, Kelly 16.7% → 1% risk ≈ ⅙-Kelly (conservative). Honest flag: 60d −26.4%, below SMA50/SMA100 — this is a **counter-trend bounce**, payoff must come from the R-multiple plan, not trend. VETO: buying the red knife converts a 2.5R plan into an unforced loss. |
| 📊 Wyckoff 2.0 | **NEUTRAL → bullish on SOS** | Markup pullback into zone + Stoch reset + SMA20 test = watch-for-Spring / LPS. Oct 8 red bar = SOW, not SOS. "If green SOS prints off $255–274 → expect retest of SMA50 $274, then $311." |
| 🧬 Medallion | **WEAK SIGNAL (pre-registered)** | Plan written BEFORE the move = no curve-fitting — good process. Zone + vol ≥1x + Stoch turning = 2-3 factors; red close + below-SMA50 fails confirmation. Upgrades to STRONG only on printed SOS + passing gate. |

- **Expert consensus: WAIT FOR TRIGGER — in zone, buy-stop not hit, gate untested.** Budget: reserved, $0 committed (1 sh = $19.78 risk = 0.79% ✓).

---

## Not Routed This Run

- **ACMR $70.80** — 🔴 WAIT, downtrend below all SMAs, 5d 5🔴/0🟢, pre-market $72.50. At/near 78.6% retrace $71.02 but knife; needs green close > SMA20 $74.06. Routine — no expert pass.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| ZS | 🚨 **TRIM AT OPEN** (level crossed) | pre-market **$222.00** (Oct 8 close $216.81) | **+48.0% (+$1,080, 15 sh)** | **Pre-market $222 > trim $216.97 (+$5.03) and > 3M high $218.82 — new highs.** Trim 5 sh → +$360 realized; remaining 10 sh trail ≈ $203.36 (2×ATR $9.32) → locked min +$533.60, combined ≥ +$893.60. Official script trail stays $198.17 until a regular close, ratchets to ~$203 on a ~$222 close. ⚠ Oct 8 high $218.82 crossed the trim but no fill → the level is manual; **execute the trim at/near open or place a resting limit now.** Stoch 93.5 overbought — runner rides the trail only. |
| AMZN | HOLD | — | −1.4% at pre ($256.00 vs entry $259.55) | Oct 8 close $254.06. SL $249.33 (2.6% below pre), TP1 $274.88 — no signal this run. |
| NVDU | CLOSED Oct 7 | — | +$1,903.21 lifecycle | Fully closed — no action |

**ZS expert panel on the trim:**
| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **BET — trim** (HIGH) | Locking +48% into an overbought extension at multi-month resistance converts an expected value into a realized one; ratchet discipline is the edge-gatekeeper. |
| 📊 Wyckoff 2.0 | **Phase E markup — trim into strength** | Pre-gap breakout over $218.82 = continuation, no SOW yet; but distribution risk at highs is exactly where trims pay. Keep 10 sh on the trail as the runner. |
| 🧬 Medallion | **STRONG (risk-reducing)** | 60d +46.3% relative-strength winner; trimming cuts single-name variance and improves portfolio Sharpe — the combination, not the single asset, is the portfolio. |

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| GOOG | $348.35–356.25 | $331.75 | $381.81 | — | ~2.0:1 | **NOT PRINTED** (pre $347.96, $0.39 below band; vol 0.8x) | **WAIT** — NO BET · NEUTRAL · NOISE | $0 committed (1sh = 0.66% risk, ready) |
| RDDT | $171.11–179.58 | $155.88 | $207.00 | — | ~2.4:1 | **NOT PRINTED** (pre $161.10, 6.2% below band; two-move) | **WAIT** — NO BET · NEUTRAL · WEAK | $0 committed (1sh = 0.61%, ready) |
| GEV ⚠ | $1,004.62–1,036.80 | $937.06 | — | $1,140.99 | ~2.0:1 | **NOT PRINTED** (pre $1,008 INSIDE band — needs regular close ≥1x vol) | **WAIT** — NO BET (1sh = 2.7% risk > 1% cap) · Back-Up setup · WEAK | not sizeable within 1% |
| MKSI ⭐ | $255–274 (buy-stop over SOS high) | fill − $19.78 | fill +1.5R (~$295) | fill +2.5R (~$314) | 1.5R / 2.5R | **NOT PRINTED** (pre $265 in zone; no SOS bar, gate untested) | **WAIT FOR TRIGGER** — armed conditional BET | reserved, $0 committed |
| ACMR | — | — | — | — | — | 🔴 DOWNTREND — not routed | n/a | $0 |

**Entries triggered this run: 0 · Exits to act on: 1 — ZS TRIM at open (pre $222 > $216.97). Capital fully uncommitted — $2,500 available.**

Discipline notes:
- Pre-market ≠ trigger: GEV is *inside* its band and GOOG $0.39 away, but zero regular-session confirmations. Wait for close + volume.
- ZS is the only actionable item today: trim 5 sh into the open, keep 10 sh on the ~$203 trail. The level was crossed on Oct 8 without a fill — execute or place the limit.
- Thorp litmus vs index: 60d — GOOG −6.9%, RDDT −21.0%, GEV −5.3%, MKSI −26.4% vs SPY +2.5%. Every entry candidate is a 60d laggard; they earn their risk only through the planned R-multiples, never by assumption. ZS (+46.3%) is the lone relative-strength winner — hence the runner.

---
*Entry Monitor 3-Expert Pipeline · monitor_entries.py + pre-market feed · Thorp / Wyckoff 2.0 / Medallion · 09 Oct 2026 20:05 ICT*
"""

path = "/root/.hermes/profiles/trader/scripts/entry_monitor_report.md"
with open(path, "w") as f:
    f.write(report)
print(f"wrote {len(report)} bytes -> {path}")
