# 📡 Entry Monitor Report — Thu 24 Sep 2026 21:00 ICT

**Run:** `monitor_entries.py` exit 0. No 🟢 entry verdicts. Exit/trailing signals fired on BOTH open positions → report triggered. (tvDatafeed connection timed out — data served via fallback; prices may be slightly delayed.)

---

## Actionable Entry Signals

**NONE this scan.** GDDY verdict is 🔴 WAIT (downtrend, below SMA50, structurally broken, testing SMA50 support at $96.17). No expert pipeline run for entries — none actionable.

**Budget $2,500:** no deployment this scan — 100% reserved.

---

## Changes Since 04:01 Report

- **NVDU: +58.0% → +54.2%** — price pulled back $142.17 → $138.77, now **below SMA20 ($138.94)** — trend weakening flag. Trail floor drifted down $128.75 → $125.65 (2×ATR recalculated on lower price). Momentum still STRONG (+3, was +5). Regime flipped UPTREND → **PULLBACK**, RSI 42.0 (was 49.6).
- **ZS: +43.0% → +42.1%** — price $214.45 → $213.09, still near 3M high $216.43. Trail floor $194.05 → $192.89. RSI 72.1 (was 74.9, back below the 75 gate), Stoch 94.2, momentum +3. Regime UPTREND intact.
- **GDDY:** deteriorated 🟡 PULLBACK → 🔴 WAIT. Price $96.38 → $95.81, fell through SMA20 and is now below SMA50 reclaim level. Plan bug from prior report (0.09:1 R:R TP) still unresolved — still not entry-eligible anyway.
- Combined open P&L: +$2,375.34 → **+$2,263.14** (drift −$112.20).

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|--------|--------|-----------|-----|-------|
| **NVDU** | 📉 PULLBACK — hold on trail (watch) | n/a (trail $125.65) | **+54.2% (+$1,316.79, 27 sh)** | Below SMA20 ($138.94) — trend weakening flag. Trail 2×ATR locks ≥+$963 (+40.0%). Regime flipped to PULLBACK, RSI 42.0, momentum +3. No exit hit — trail governs |
| **ZS** | 📈 TRAILING — hold | n/a (trail $192.89) | **+42.1% (+$946.35, 15 sh)** | Trail 2×ATR locks ≥+$643 (+29.9%). Near 3M high $216.43 (+1.6% away) — resistance zone. RSI 72.1 / Stoch 94.2 overbought. Momentum STRONG (+3), regime UPTREND |

*Combined open P&L: **+$2,263.14** on $4,680 deployed (+48.4%). Worst case if BOTH trails hit: **+$1,606 (+34.3%)** locked.*

---

## Expert Analysis — Exit Decisions (Active Positions)

### NVDU — 📉 PULLBACK → HOLD ON TRAIL

**Setup**
- Entry $90.00 → Current **$138.77** | P&L **+54.2% (+$1,316.79, 27 sh)**
- Trail stop **$125.65** (2×ATR) locks in **≥ +$963.45 (+40.0%)** minimum
- Risk from here to trail = −9.5%; upside unbounded while trail holds (TP3 ∞)
- RSI 42.0 (cooled from 49.6) | Stoch 47.8 | Momentum STRONG (+3) | ATR $6.56 | Regime **PULLBACK**, price below SMA20 ($138.94)

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Floor still locks +40.0% with open upside — positive-EV hold with defined ruin point. But the signal set weakened (regime → PULLBACK, momentum +5 → +3, below SMA20): the edge is decaying in real time, exactly the Phase 5 decay pattern. Trail, not conviction, is now carrying the trade. | **BET on hold via trail** (confidence: moderate) | 3/5 |
| 📊 Wyckoff | Markup Phase E pulling back to first structure (SMA20). No SOW bar, no distribution climax — a normal LPSY/test after a run. If the pullback prints a SOS at the trail/SMA100 zone, markup resumes; a sustained break below trail = distribution warning. Last shakeout direction still up. | **NEUTRAL — markup intact, pullback unconfirmed** | 3/5 |
| 🧬 Medallion | Confluence degraded: 3 aligned factors now (still-positive P&L, momentum +3, trail discipline) vs 6 this morning (uptrend, +5 momentum, RSI reset, above SMA20...). Single deterministic rule (2×ATR trail) governs — low overfit risk, but the signal flip within one session is a fragility flag, not a fresh entry-quality signal. | **WEAK SIGNAL (hold — trail governs)** | 2/5 |

**Expert Consensus: 3/3 → HOLD with trail $125.65. Weakening trend — no new averaging, exit automatically if trail hit.**

### ZS — 📈 TRAILING → HOLD

**Setup**
- Entry $150.00 → Current **$213.09** | P&L **+42.1% (+$946.35, 15 sh)**
- Trail stop **$192.89** (2×ATR) locks in **≥ +$643.35 (+29.9%)** minimum
- 3M high $216.43 only **+1.6% ($3.34)** above price (supply zone)
- RSI 72.1 (back below the 75 TP3 gate) | Stoch 94.2 | Momentum STRONG (+3) | Regime UPTREND

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Hold R:R to 3M high vs trail = $3.34 vs $20.20 ≈ **0.17:1** — poor immediate reward at an overbought extreme. But unlike this morning's flat TAKE-PROFIT call, the trail guarantees +29.9% and momentum remains +3: asymmetric hold with a hard floor is acceptable. | **MARGINAL BET on hold** (confidence: moderate) | 3/5 |
| 📊 Wyckoff | Phase E markup driving into 3M-high supply. Stoch 94.2 / RSI 72.1 = extended but no SOW bar, no confirmed distribution structure. Exiting into strength at known supply remains valid if risk appetite drops; structure says trend intact. | **NEUTRAL — supply zone ahead, markup intact** | 3/5 |
| 🧬 Medallion | Prior exit consensus weakened: RSI fell back below the 75 gate (the fragile 0.1 threshold flagged at 04:01 flipped back — confirmed noise, not signal). Real factors: overbought Stoch + 3M-high resistance vs momentum +3 + UPTREND regime = 2v2 split. Deterministic trail resolves the tie. | **WEAK SIGNAL (no fresh edge — trail governs)** | 2/5 |

**Expert Consensus: 3/3 → HOLD with trail $192.89. Prior 04:01 TAKE PROFIT call stands as the alternative if you want to realize +$946 into 3M-high resistance; trail guarantees ≥+$643 otherwise.**

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS SCAN** | **$0 deployed** |
| *(hold)* **NVDU** | $90.00 | trail **$125.65** | ✅ $99.84 | ✅ $109.68 | +54.2% actual | **HOLD ON TRAIL 3/3** (avg 2.7/5 — weakening) | unrealized **+$1,316.79** |
| *(hold)* **ZS** | $150.00 | trail **$192.89** | ✅ $165.15 | ✅ $180.30 | +42.1% actual | **HOLD ON TRAIL 3/3** (avg 2.7/5) | unrealized **+$946.35** |
| *(watch)* GDDY | — | — | — | — | — | WAIT — 🔴 downtrend, below SMA50 | $0 — hold cash |

**Action today:** HOLD NVDU (trail $125.65, trend weakening — below SMA20) and ZS (trail $192.89, at 3M-high resistance). No new entries. Optional: realize ZS +$946.35 into resistance per the standing 04:01 TP call.

---

## Appendix — Raw Monitor Output

```
**📡 Entry Monitor — Thu 24 Sep 2026 21:00 ICT**

📡 GDDY Entry Monitor
Price: $95.81 (-0.59%) | RSI: 41.4 | Vol: 0.07x
SMA 20: $98.88 | SMA 50: $96.17 | SMA 100: $90.79
5d: 4🔴/1🟢
• 📏 Testing SMA 50 support at $96.17
📍 VERDICT: 🔴 WAIT | DOWNTREND | Below SMA50 structurally broken

🚨 NVDU EXIT SIGNAL
Price: $138.77 | Entry: $90.00 | P&L: +54.2% ($+1316.79)
Regime: PULLBACK | RSI: 42.0 | Stoch: 47.8 | ATR: $6.56
Momentum: STRONG (+3) | R: $6.56
SL: $125.65 (TRAILING 2×ATR) | TP1: $99.84 | TP2: $109.68 | TP3: ∞ (letting run)
• 📈 TRAILING @ $138.77 | Trail stop: $125.65 (2×ATR below price) | P&L: +54.2% — let profits run
• 📉 Below SMA20 ($138.94) | P&L: +54.2% — trend weakening

🚨 ZS EXIT SIGNAL
Price: $213.09 | Entry: $150.00 | P&L: +42.1% ($+946.35)
Regime: UPTREND | RSI: 72.1 | Stoch: 94.2 | ATR: $10.10
Momentum: STRONG (+3) | R: $10.10
SL: $192.89 (TRAILING 2×ATR) | TP1: $165.15 | TP2: $180.3 | TP3: ∞ (letting run)
• 📈 TRAILING @ $213.09 | Trail stop: $192.89 (2×ATR below price) | P&L: +42.1% — let profits run
• 📏 Near 3M High $216.43 | P&L: +42.1% — resistance zone
```
