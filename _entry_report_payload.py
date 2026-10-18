report = r'''# 📡 Entry Monitor Report — Mon 19 Oct 2026 03:00 ICT

> ⚠️ **State changes vs Fri 16 Oct 22:00 report:** Both exit signals persist **unexecuted** (still OPEN in journal). Conditional state genuinely shifted:
> - **RDDT dropped out of the monitor entirely** (was 🟡 conditional, below band).
> - **BCC verdict flipped** WAIT → ⚠️BOUNCE (SMA50 gap narrowed $1.30 → $0.50).
> - **CRWV deepened** 🔴 knife → ⏳ CAPITULATION WATCH (2.41× vol spike, Stoch 5.6/RSI 26.4).
> No 🟢 confirmation triggers printed this run.

---

## 🟢 Entry Triggered

**None — no confirmation triggers printed this run.** RDDT carries a bounce label but is not in the current snapshot; all live alerts are exit/regime warnings (ZS, AMZN) and capitulation knives (OPEN, ACMR). BCC/CRWV remain conditional (triggers absent).

---

## 🟡 Conditional Setup — Trigger Not Printed

### BCC — ⚠️ BOUNCE (gap narrowing to SMA50)

- **Setup:** Bounce regime. Price $76.13 (+0.86%), RSI 48.0, 2d green streak, above SMA20 ($75.31) + SMA100 ($76.33), **$0.50 below SMA50 ($77.85)**, vol 0.8x.
- **Trigger needed:** daily close **>$77.85 (SMA50 reclaim)** on **≥1.0× volume** + green SOS bar (wide-range bullish close, upper third) → buy-stop above trigger candle high. **NOT printed — still below SMA50, 0.8× vol, no initiative.**
- **Planned levels (only on trigger):** Entry ~$78.36 (reclaim bar high) | Stop $75.33 (SMA20/Fib) | risk ~$3.03 | TP1 1.5R ≈ $82.9. Invalidate: close <$75.33.

| Expert | Verdict | Score | Notes |
|---|---|---|---|
| Thorp | **NO BET (conf: high)** | — | SMA50 reclaim is a trend filter, not a structural edge; n=0 sampled trades → expectancy/Kelly undefined. ~0.1% slip vs ~$3.03 risk = dangerous. **0% now.** Size only after BOTH halves print (close + ≥1.0× vol + SOS). |
| Wyckoff | **NEUTRAL — pre-SOS, weakened** | — | Testing SMA50 from below on 0.8× volume = no initiative buying; the SMA50 is acting as supply, not demand. Phase D back-up failing, not strengthening. Scenario: reclaim >$77.85 on ≥1.0× vol → SOS confirmed; alt: reject → retest SMA20 $75.31. |
| Medallion | **WEAK SIGNAL 2/6** | 2/6 | Structure ✗ (below SMA50), trend ✓ (above SMA20/100), momentum ✓-neutral (RSI 48), volume ✗ (0.8×), MA-unconfirmed ✗ (below SMA50). n=0, textbook bounce, no t-stat → won't lift portfolio Sharpe. |

**Consensus: WAIT — 0%.** Trigger = close >$77.85 on ≥1.0× vol + SOS bar → buy-stop above it. Below $75.33 setup dead.
**Budget $2,500 → $0.** On trigger: $25 risk ÷ $3.03 ≈ 8 sh ≈ $630, 1.0% risk.

### CRWV — ⏳ CAPITULATION WATCH (deeper, vol spike)

- **Setup:** AI-beta knife. Price $61.39 (−11.91%), RSI 26.4 / Stoch 5.6 (deep oversold), **vol 2.41×**, below all SMAs (SMA20 $82.96). 5d: 4🔴/1🟢. 3M low $59.51, 78.6% fib $71.92.
- **Trigger needed:** green daily close + ≥1.5× volume **above SMA20 ($82.96)** → buy-stop above trigger candle. **NOT printed — still in selling climax, no SOS.**
- **Planned levels (only on trigger):** Entry ~$83-84 (SMA20 reclaim) | Stop $53.63 (3M low zone) | risk ~$3.40/sh (knife risk) | TP1 1.5R ≈ $88.3.

| Expert | Verdict | Score | Notes |
|---|---|---|---|
| Thorp | **NO BET (conf: med-high)** | — | Capitulation = behavioral pattern, n=0, no structural edge. Falling-knife risk: thin-name, 2.41× vol = real climax but slippage on thin liquidity can exceed the 1×ATR stop. **0% until SOS + volume confirm.** |
| Wyckoff | **CLIMAX / NEUTRAL — capitulation watch** | — | Selling climax 2.41× vol = Phase A breakdown / potential shakeout. Price pressing 3M low $59.51. Needs SOS bar (green close, upper-third, initiative vol) to flip to accumulation watch — currently still markdown; lose $53.63 and next shelf is far below. |
| Medallion | **WEAK 2/6** | 2/6 | Momentum ✓-oversold (RSI 26.4, Stoch 5.6), volume ✓-capitulation (2.41×), but trend ✗ (below all SMAs), structure ✗ (downtrend), regime ✗. n=0, single high-beta asset, no cross-market validation. Knife dominates. |

**Consensus: WAIT — 0%.** Trigger = green close + ≥1.5× vol above SMA20 $82.96. Stop zone $53.63.
**Budget $2,500 → $0 pending SOS + volume confirmation.**

---

## Not routed (🔴 class, carried)

- **OPEN** — 🔴 WAIT. Capitulation (−8.84%, 1.89× vol), RSI 36.8 / Stoch 30.8, below SMA20/50/100 ($2.36/$2.87/$3.67). NO ENTRY — Phase A range gate absent (per Fri plan, re-arm only on AR→ST holding ≥$2.00). 3M low $1.93. Carried unchanged.
- **ACMR** — 🔴 WAIT. Knife (−8.59%), RSI 21.4 / Stoch 0.4 (deepest oversold), below all SMAs, at 78.6% fib $62.04. Needs green close > SMA20 ($72.69). Knife — no market-buy. Carried unchanged.

---

## 🚨 Exit Signals (Active Positions)

Both carry forward unexecuted from Fri 16 Oct's recommendations (journal confirms still OPEN).

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **ZS** | **Take partial profits / tighten trail** | live **$207.38** | **+38.3% (+$860.70, 15 sh)** | TP2 hit ($170.46, 2.0R). MACD bearish (hist −0.57), **below SMA20 ($210.66)**, momentum WEAK (+0). Monitor dynamic SL trailed to $165.34 (TP1 level, locks +10%). Journal trim $216.97 / trail $193.09 — price now below both. |
| **AMZN** | **EXIT per plan** | live **$250.00** | **−3.7% (−$95.50, 10 sh)** | **Invalidation breached**: $250.00 ≤ $256.68 (Oct 8 plan: "daily close below $256.68 → exit all"). 4th session below. Hard stop $247.75 (live 2×ATR $5.90; journal $249.33). |

### ZS — 3-expert exit panel

| Expert | Verdict |
|---|---|
| Thorp | **EXIT (partial) — lock the realized edge.** TP2 (2.0R) already captured, momentum score flipped WEAK (+0), MACD crossed bearish, price below SMA20 = regime shift. Forward expectancy now negative (momentum collapse). Kelly: 0% on new adds; size the exit to lock +38%. |
| Wyckoff | **SUPPLY — Phase E exhausting.** Markup $150 → $207 faded under SMA20; MACD histogram turning negative = failed back-up, sellers stepping in at the creek. Protect into supply: trim now, trail remainder. |
| Medallion | **EXIT (aligned).** TP2-hit ✓ + MACD-bearish ✓ + below-SMA20 ✓ + momentum-WEAK ✓ — one-family trend-collapse cluster, unanimous. No positive signal family supports hold. |

**Consensus: TAKE PARTIAL PROFITS now** (journal "partial profit candidate"). Trim ~50% ($216.97 target missed — momentum fading, take now), trail remainder at $193.09 (journal) / $165.34 (monitor floor). Do not chase back above SMA20.

### AMZN — 3-expert exit panel

| Expert | Verdict |
|---|---|
| Thorp | **EXIT = the trade.** Edge never established: entry $259.55, TP1 $274.88 never approached. Invalidation line $256.68 breached 4x; expected value of waiting is negative vs a hard 2×ATR stop. Cut at −3.7% rather than risk the full −4.5% ($247.75). |
| Wyckoff | **CAPPING SUPPLY.** Pinned under invalidation $256.68 with lower highs; regime DOWNTREND. BOUNCE label hollow — structure is distributional under the line. Until daily close reclaims $256.68, supply controls. |
| Medallion | **REMOVE.** No signal family supports hold: below-entry + below-SMA + invalidation-breached (correlated ~1.5 families, not 4) → unanimous exit read. Momentum NEUTRAL (+2) is a single-family reading inside a failed structure. |

**Consensus: EXIT at market** (~$250). Hard stop $247.75 (journal $249.33) underneath. Log fill to trade_journal.json. Frees ~$2,500 cash.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State (PRINTED/NOT) | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| (none) | — | — | — | — | — | **0 🟢 triggers printed** | — | $0 |
| **BCC** | ~$78.36 (SMA50 reclaim) | $75.33 (SMA20) | ~$82.9 (1.5R) | — | ~1.5R | **NOT PRINTED — $0.50 below SMA50, 0.8× vol** | WAIT — Thorp NO BET (high) / Wyckoff pre-SOS / Medallion weak 2/6 | $0 |
| **CRWV** | ~$83-84 (SMA20 reclaim) | $53.63 (3M low) | ~$88.3 (1.5R) | — | ~1.0R knife | **NOT PRINTED — capitulation, 2.41× vol, no SOS** | WAIT — Thorp NO BET / Wyckoff climax / Medallion weak 2/6 | $0 |
| OPEN | $2.15-2.25 (range) | $2.00 | $2.45 | $3.00 | 0.8-5.7R | NOT PRINTED — knife, range gate absent | carried: NO ENTRY | $0 |
| ACMR | >$72.69 (SMA20 reclaim) | $62.04 (78.6%) | — | — | — | NOT PRINTED — knife below all SMAs | NO BET / NO ENTRY | $0 |
| **ZS** | — | $165.34 (trail/TP1) | $170.46 (2.0R **hit**) | — | — | **EXIT — TP2 hit, MACD bearish, <SMA20** | TAKE PARTIAL profits (+38.3%) | — |
| **AMZN** | — | $247.75 (hard 2×ATR) | $274.88 (1.5R) | $285.10 (2.5R) | — | **EXIT — <$256.68 invalidation, 4th sess** | EXIT @ ~$250 (−3.7%) | — |

**Run verdict: 0 entry triggers. 2 exit signals firing (ZS take-partial / AMZN plan-exit — both OPEN, unexecuted since Fri). Conditional state changed: RDDT dropped out, BCC flipped to ⚠️BOUNCE (SMA50 gap narrowed to $0.50), CRWV deepened to capitulation watch (2.41× vol, Stoch 5.6). OPEN/ACMR remain 🔴 knives, not routed.**

**Action items:**
- **ZS — take partial profits now** (~50% trim, lock +38%), trail remainder at $193.09 / $165.34. Momentum WEAK + MACD bearish + below SMA20 = regime-shift exit.
- **AMZN — exit at market (~$250)** per Oct 8 invalidation plan (daily close <$256.68 → exit all). Hard stop $247.75. Frees ~$2,500.
- **BCC/CRWV — 0% until SMA50 reclaim / SOS + volume print.** Budget stays at $0 of $2,500.
'''

with open('/root/.hermes/profiles/trader/scripts/entry_monitor_report.md', 'w') as f:
    f.write(report)
print("Report written:", len(report), "chars")
