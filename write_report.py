#!/usr/bin/env python3
"""Write the entry monitor report to entry_monitor_report.md"""
from datetime import datetime, timezone, timedelta

BKK = timezone(timedelta(hours=7))
now = datetime.now(BKK)
now_str = now.strftime("%a %d %b %Y %H:%M ICT")

report = f"""# 📡 Entry Monitor Report — {now_str}

> ⚠️ **State changes vs Mon 19 Oct 21:00 ICT:** ZS exit signal **persists** (TP2 hit at $175.78/2.5R, MACD Hist worsening to -1.12, momentum NEUTRAL +2, P&L improved +39.8%→**+41.7%**). **CRWV NEW** conditional — flipped from 🔴 WAIT to ⏳ CAPITULATION WATCH (RSI 25.0/Stoch 5.5, vol spike 2.21× at 78.6% Fib). **AMZN exit RESOLVED** — no exit signal (price $262.49 > $256.68 invalidation, position still OPEN per journal). 0 🟢 entry triggers.

---

## 🟢 Entry Triggered

**None — no confirmation triggers printed this run.** No green close above resistance, no SOS bar with >1× volume, no MACD-confirmed entries at price level. 0 🟢 triggers.

---

## 🟡 Conditional Setup — Trigger Not Printed

### CRWV (CoreWeave) — ⏳ CAPITULATION WATCH

**Setup:** AI-GPU cloud stock deep in markdown, at 78.6% Fib retracement ($71.71), 3M low $59.25, extreme oversold (RSI 25.0, Stoch 5.5), volume spike 2.21× (capitulation climax). Below all SMAs (SMA20 $81.75, SMA50 $86.44, SMA100 $89.29). Knife below structure — no market-buy.

**Trigger needed (NOT printed yet):** Green daily close above SMA20 $81.75 + volume ≥1.5× avg OR SOS bar (wide-range bullish candle, close upper-third) with >1.0× vol.

**Planned levels:**
- Entry: >$81.75 (SMA20 reclaim) — buy-stop above trigger candle high
- Stop: $53.28 (3M low $59.25, structure invalidation)
- TP1: $86.44 (SMA50 reclaim) — 1.5R
- TP2: $89.29 (SMA100) — 2.5R
- R:R: ~4:1 (if entered at ~$82)

#### 🧪 3-Expert Panel

| Expert | Verdict | Notes |
|--------|---------|-------|
| 🔢 **Thorp** | **NO BET** | Capitulation watch only. No confirmed edge: RSI 25/Stoch 5.5 oversold + vol spike 2.21× = potential climax but trigger NOT printed (needs green close > SMA20). Expected value negative without confirmation (AI-beta knife = 50%+ dump risk). Kelly ≈ 0. |
| 📊 **Wyckoff 2.0** | **CAPITULATION WATCH** | Markdown → Phase C shakeout at 78.6% Fib ($71.71). Volume spike 2.21× = climax/capitulation. Scenario: green close > SMA20 $81.75 + vol → Phase D SOS bar → enter. If < $53.28 (3M low $59.25) → Phase E breakdown, no entry. Stop: $53.28. |
| 🧬 **Medallion** | **WEAK SIGNAL** | Only 2 confluence factors (extreme oversold + vol spike). CRWV is AI-beta — noise-to-signal ratio elevated. No statistical significance without confirmation bar. Pattern risk: 50%+ dump if capitulation fails. |

**Consensus: WAIT — CAPITULATION WATCH.** CRWV deep oversold (RSI 25/Stoch 5.5) at 78.6% Fib ($71.71) with vol spike 2.21×. Trigger NOT printed — needs green close > SMA20 $81.75 + volume ≥1.5×. Stop: $53.28 (3M low $59.25). If 3M low breaks, pattern invalidated. **Budget: $0 of $2,500** — wait for trigger.

---

## 🚨 Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|--------|--------|------------|-----|-------|
| **ZS** | **Take FULL PROFITS** | market ~$212.56 | **+41.7% (+$938.40, 15 sh)** | TP2 hit at $175.78 (2.5R). Price now 6.0R above entry. MACD bearish (Hist -1.12), Stoch cooling (41.4), momentum NEUTRAL (+2). SL trailed to $165.47 (TP1 level). |
| **AMZN** | **EXIT RESOLVED — hold** | — | — | Price $262.49 > $256.68 invalidation. No exit signal. Position OPEN per journal. Re-evaluate per Oct 8 plan. |

### ZS — 3-Expert Exit Panel

| Expert | Verdict | Notes |
|--------|---------|-------|
| 🔢 **Thorp** | **EXIT (full) — lock edge** | TP2 hit $175.78 (2.5R), price 6.0R above entry ($212.56). MACD bearish (Hist -1.12, worsening), momentum NEUTRAL (+2), Stoch cooling. Edge was genuine (+$938.40, 4/4 pattern) but forward expectancy now negative. Kelly: 0% on new adds. Lock +41.7%. |
| 📊 **Wyckoff 2.0** | **SUPPLY — Phase E exhausting** | Markup $150→$212.56 complete. Price above SMA20 ($210.93) but MACD histogram strongly negative (-1.12) = bearish divergence. Back-up to SMA20 creek failing; supply stepping in at structure boundary. Phase E exhaustion — distribute into supply. |
| 🧬 **Medallion** | **EXIT (aligned)** | TP2-hit ✓ + MACD-bearish ✓ (Hist -1.12) + Stoch-cooling ✓ + momentum-NEUTRAL ✓ — unanimous trend-collapse cluster. ZS ran 6.0R, 1.4× beyond TP2. Signal family flipped bearish. Remove from book. |

**Consensus: TAKE FULL PROFITS NOW.** ZS ran 6.0R ($150→$212.56), TP2 captured at $175.78. MACD bearish + Stoch cooling + momentum NEUTRAL = trend collapse. Lock +41.7% ($938.40). Reallocate capital.

### AMZN — Exit Signal Resolved

| Expert | Verdict | Notes |
|--------|---------|-------|
| 🔢 **Thorp** | **EXIT RESOLVED — re-evaluate** | AMZN $262.49, above $256.68 invalidation. No exit signal. Position OPEN per journal (entry $259.55, 10 sh). Regime UPTREND, above SMA20 $253.43. Re-evaluate per Oct 8 plan: hard stop $249.33 no longer threatened. |
| 📊 **Wyckoff 2.0** | **REGIME NEUTRALIZED** | Invalidity line ($256.68) reclaimed → supply receded. Phase D back-up attempting, not yet confirmed as Phase E. Wait for fresh SOS bar + volume. |
| 🧬 **Medallion** | **NO SIGNAL** | Exit conditions lifted (invalidation reclaimed, hard stop clear). No active signal family. If holding: flat momentum, regime neutral. Re-assess on fresh signal (SOS bar + volume). |

**Consensus: AMZN exit signal resolved.** Price recovered above $256.68 invalidation. Position still OPEN per journal (10 sh @ $259.55, cost $2,595.55). Hold per Oct 8 plan — TP1 $274.88, TP2 $285.10, hard stop $249.33.

---

## Not Routed (🔴 class, silent)

- **ACMR** — 🔴 WAIT. Price $56.07 (+5.63%), RSI 27.0/Stoch 9.4, DOWNTREND below all SMAs. At/near 78.6% retrace $61.85 — deep support, no entry without reversal trigger. SMA20 reclaim needed ($71.86). Knife — no market-buy.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|--------|-------|------|-----|-----|-----|---------------|-----------------|---------------|
| **CRWV** | >$81.75 (SMA20 reclaim) | $53.28 (3M low $59.25) | $86.44 (SMA50) | $89.29 (SMA100) | ~4:1 | **NOT PRINTED — needs green close > SMA20 + vol ≥1.5×** | W**AIT — capitulation watch, Kelly ≈ 0** | $0 |
| **ZS** | — | — | $165.47 (TP1, 1.5R) | $175.78 (TP2 **HIT**) | — | **EXIT — TP2 hit, MACD bearish, 6.0R run** | **TAKE FULL PROFITS (+41.7%)** | $0 |
| **AMZN** | — | $249.33 (2×ATR) | $274.88 (1.5R) | $285.10 (2.5R) | 3.2:1 | **EXIT RESOLVED — above $256.68** | **HOLD — regime neutralized, per Oct 8 plan** | $0 |
| ACMR | >$71.86 (SMA20 reclaim) | $61.85 (78.6%) | — | — | — | **NOT PRINTED — knife, vol 0.69×** | **NO ENTRY (🔴 WAIT)** | $0 |

---

## Action Items

- **ZS — take FULL PROFITS NOW** at ~$212.56. 15 sh × $212.56 = $3,188.40. Realized +$938.40 (+41.7%). TP2 captured at $175.78, MACD bearish, momentum NEUTRAL + price above all TP levels. Lock the edge — reallocate capital.
- **CRWV — monitor for capitulation reversal.** Trigger: green daily close > SMA20 $81.75 + volume ≥1.5×. If triggered → route to 3-expert panel. If 3M low $59.25 breaks → pattern invalidated, drop from watch. Stop if entered: $53.28.
- **AMZN — verify position status.** Journal shows OPEN (10 sh @ $259.55). Exit signal resolved (price $262.49 > $256.68). Hold per Oct 8 plan: TP1 $274.88, TP2 $285.10, hard stop $249.33. Budget remains at $0 of $2,500 (no entries triggered this run).
- **ACMR — 0% until SMA20 reclaim + SOS bar + volume ≥1.0×.** Deep knife below all SMAs, at 78.6% retrace $61.85. No entry without reversal trigger.
"""

with open('/root/.hermes/profiles/trader/scripts/entry_monitor_report.md', 'w') as f:
    f.write(report)

print(f"Report written: {len(report)} chars")
print(f"Path: /root/.hermes/profiles/trader/scripts/entry_monitor_report.md")
