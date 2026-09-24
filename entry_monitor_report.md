# 📡 Entry Monitor Report — Thu 24 Sep 2026 22:00 ICT

**Run:** `monitor_entries.py` exit 0. No 🟢 entry verdicts. Exit/trailing signals fired on BOTH open positions → report triggered. (tvDatafeed connection timed out — data served via fallback; prices may be slightly delayed.)

---

## Actionable Entry Signals

**NONE this scan.** No 🟢 entry confirmations — no expert entry pipeline run.

**Budget $2,500:** no deployment this scan — 100% reserved.

---

## Changes Since 21:00 Report

- **NVDU: +54.2% → +52.5%** — price $138.77 → $137.23, still **below SMA20 ($138.86)** — trend weakening flag persists. Trail floor $125.65 → **$124.11** (2×ATR recalculated on lower price). Momentum STRONG (+3), RSI 42.0 → 40.8, regime PULLBACK.
- **ZS: +42.1% → +42.6%** — price $213.09 → $213.93, still near 3M high $216.43 (+1.2% away). Trail floor $192.89 → **$193.73**. RSI 72.1 → 72.8, Stoch 95.6, momentum +3, regime UPTREND.
- Combined open P&L: +$2,263.14 → **+$2,234.16** (drift −$28.98).
- GDDY no longer appears in scan output this run (previous 🔴 WAIT).

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|--------|--------|-----------|-----|-------|
| **NVDU** | 📈 TRAILING + 📉 below-SMA20 — hold on trail (watch) | n/a (trail $124.11) | **+52.5% (+$1,275.21, 27 sh)** | Below SMA20 ($138.86) — trend weakening. Trail 2×ATR locks ≥+$921 (+37.9%). Regime PULLBACK, RSI 40.8, momentum +3. No exit hit — trail governs |
| **ZS** | 📈 TRAILING — hold | n/a (trail $193.73) | **+42.6% (+$963.00–958.95, 15 sh)** | Trail 2×ATR locks ≥+$656 (+31.1%). Near 3M high $216.43 (+1.2% away) — resistance zone. RSI 72.8 / Stoch 95.6 overbought. Momentum STRONG (+3), regime UPTREND |

*Combined open P&L: **+$2,234.16** on $4,680 deployed (+47.7%). Worst case if BOTH trails hit: **≈+$1,577 (+33.7%)** locked.*

---

## Expert Analysis — Exit Decisions (Active Positions)

### NVDU — 📈 TRAILING / below SMA20 → HOLD ON TRAIL

**Setup**
- Entry $90.00 → Current **$137.23** | P&L **+52.5% (+$1,275.21, 27 sh)**
- Trail stop **$124.11** (2×ATR) locks in **≥ +$921 (+37.9%)** minimum
- RSI 40.8 (cooled further from 42.0) | Stoch 43.0 | Momentum STRONG (+3) | ATR $6.56 | Regime **PULLBACK**, price below SMA20 ($138.86)

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Floor still locks +37.9% with unbounded upside — positive-EV hold with a defined ruin point. But signal set continues to decay (2nd consecutive session: below SMA20, RSI sliding 49.6→42.0→40.8) — classic Phase 5 edge-decay pattern. Trail, not conviction, carries the trade. | **BET on hold via trail** (confidence: moderate) | 3/5 |
| 📊 Wyckoff | Markup Phase E pulling back toward first structure. No SOW bar, no distribution climax — normal test after a run. Last shakeout direction still up. A sustained break below trail = distribution warning; SOS at trail/SMA zone = markup resumes. | **NEUTRAL — markup intact, pullback deepening** | 3/5 |
| 🧬 Medallion | Confluence degraded further: ~3 aligned factors (positive P&L, momentum +3, trail discipline) vs 6 at 04:01. Single deterministic rule (2×ATR trail) governs — low overfit risk, but signal flip within one session remains a fragility flag, not entry-quality. | **WEAK SIGNAL (hold — trail governs)** | 2/5 |

**Expert Consensus: 3/3 → HOLD with trail $124.11. Weakening trend — no averaging, exit automatically if trail hit.**

### ZS — 📈 TRAILING → HOLD

**Setup**
- Entry $150.00 → Current **$213.93** | P&L **+42.6% (+$958.95, 15 sh)**
- Trail stop **$193.73** (2×ATR) locks in **≥ +$656 (+31.1%)** minimum
- 3M high $216.43 only **+1.2% ($2.50)** above price (supply zone)
- RSI 72.8 | Stoch 95.6 | Momentum STRONG (+3) | Regime UPTREND

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Hold R:R to 3M high vs trail = $2.50 vs $20.20 ≈ **0.12:1** — poor immediate reward at an overbought extreme (Stoch 95.6). But trail guarantees +31.1% and momentum +3: asymmetric hold with a hard floor. Realizing into known supply remains the standing alternative. | **MARGINAL BET on hold** (confidence: moderate) | 3/5 |
| 📊 Wyckoff | Phase E markup driving into 3M-high supply. Stoch 95.6 / RSI 72.8 extended but no SOW bar, no confirmed distribution structure. Structure says trend intact; exiting into strength at known supply is valid if risk appetite drops. | **NEUTRAL — supply zone ahead, markup intact** | 3/5 |
| 🧬 Medallion | Factors: overbought Stoch + 3M-high resistance vs momentum +3 + UPTREND regime = 2v2 split. Deterministic trail resolves the tie. RSI gate flicker at 21:00 confirmed as noise, not signal — no fresh edge either way. | **WEAK SIGNAL (no fresh edge — trail governs)** | 2/5 |

**Expert Consensus: 3/3 → HOLD with trail $193.73. Alternative: realize +$958.95 into 3M-high resistance per standing TP call; trail guarantees ≥+$656 otherwise.**

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS SCAN** | **$0 deployed** |
| *(hold)* **NVDU** | $90.00 | trail **$124.11** | ✅ $99.84 | ✅ $109.68 | +52.5% actual | **HOLD ON TRAIL 3/3** (avg 2.7/5 — weakening) | unrealized **+$1,275.21** |
| *(hold)* **ZS** | $150.00 | trail **$193.73** | ✅ $165.15 | ✅ $180.30 | +42.6% actual | **HOLD ON TRAIL 3/3** (avg 2.7/5) | unrealized **+$958.95** |

**Action today:** HOLD NVDU (trail $124.11, trend weakening — below SMA20) and ZS (trail $193.73, at 3M-high resistance). No new entries. Optional: realize ZS +$958.95 into resistance per the standing TP call.

---

## Appendix — Raw Monitor Output

```
**📡 Entry Monitor — Thu 24 Sep 2026 22:00 ICT**

🚨 NVDU EXIT SIGNAL
Price: $137.23 | Entry: $90.00 | P&L: +52.5% ($+1275.21)
Regime: PULLBACK | RSI: 40.8 | Stoch: 43.0 | ATR: $6.56
Momentum: STRONG (+3) | R: $6.56
SL: $124.11 (TRAILING 2×ATR) | TP1: $99.84 | TP2: $109.68 | TP3: ∞ (letting run)
• 📈 TRAILING @ $137.23 | Trail stop: $124.11 (2×ATR below price) | P&L: +52.5% — let profits run
• 📉 Below SMA20 ($138.86) | P&L: +52.5% — trend weakening

🚨 ZS EXIT SIGNAL
Price: $213.93 | Entry: $150.00 | P&L: +42.6% ($+958.95)
Regime: UPTREND | RSI: 72.8 | Stoch: 95.6 | ATR: $10.10
Momentum: STRONG (+3) | R: $10.10
SL: $193.73 (TRAILING 2×ATR) | TP1: $165.15 | TP2: $180.3 | TP3: ∞ (letting run)
• 📈 TRAILING @ $213.93 | Trail stop: $193.73 (2×ATR below price) | P&L: +42.6% — let profits run
• 📏 Near 3M High $216.43 | P&L: +42.6% — resistance zone
```
