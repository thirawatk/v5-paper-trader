# 📡 Entry Monitor Report — Thu 24 Sep 2026 04:01 ICT

**Run:** `monitor_entries.py` exit 0. No 🟢 entry verdicts. Exit/trailing signals fired on BOTH open positions → report triggered.

---

## Actionable Entry Signals

**NONE this scan.** GDDY is 🟡 PULLBACK, BCC and GEV are ⚠️ BOUNCE (both still below SMA50 reclaim levels). No expert pipeline run for entries — none actionable.

⚠️ **GDDY plan bug (unchanged):** Entry $98.87 / Stop $91.23 / TP $99.54 → reward $0.67 vs risk $7.64 = **0.09:1 R:R**. TP looks wrong in the monitor — must be fixed before any GDDY entry is taken.

**Budget $2,500:** no deployment this scan — 100% reserved. A ZS exit would free ~$3,216.75.

---

## Changes Since 03:00 Report

- **ZS trail floor RAISED $165.30 → $194.05** (2×ATR trailing now active). Monitor flipped from "TP2 HIT" to "TRAILING / TP3 ∞" mode.
- **Cause of the flip:** RSI ticked 75.0 → 74.9, crossing the script's `RSI < 75` TP3 gate by 0.1. Mode change hinged on noise-level data — noted as a fragile threshold, not a real signal change.
- NVDU: unchanged (trail $128.89 → $128.75, price drift only).
- Entries: unchanged, all below triggers.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **ZS** | 🎯 **TAKE PROFIT** (TP1+TP2 done, at 3M-high resistance) | ~$214.45 | **+43.0% (+$966.75)** | Stoch 97.7, only +0.6% below 3M high $215.73; new trail $194.05 locks ≥+29.4% if held. Frees ~$3,216.75 |
| **NVDU** | 📈 TRAILING — hold | n/a | **+58.0% (+$1,408.59)** | Trail $128.75 (2×ATR) locks ≥+$1,046 (+43.1%); RSI 49.6 reset, momentum +5; auto-exit when hit |

*Combined open P&L: **+$2,375.34** on $4,680 deployed (+50.8%). Worst case if BOTH trails hit: **+$1,707.00 (+36.5%)** locked.*

---

## Expert Analysis — Exit Decisions (Active Positions)

### ZS — 🎯 TP1+TP2 EXCEEDED → TAKE PROFITS

**Setup**
- Entry $150.00 → Current **$214.45** | P&L **+43.0% (+$966.75, 15 sh)**
- TP2 $180.60 (3.0R) **exceeded by +18.8%** — trade at **+6.3R** (R = $10.20)
- RSI 74.9 | Stoch 97.7 | ATR $10.20 | Momentum STRONG (+3) | Regime UPTREND
- 3M high $215.73 only **+0.6% ($1.28)** above price (supply/resistance zone)
- Trail $194.05 (2×ATR) = **−9.5% ($20.40)** give-back from current price

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Hold R:R to 3M high vs trail = $1.28 vs $20.40 ≈ **0.06:1** — negative immediate EV at an overbought extreme. Realizing +$64.52/sh beats a 0.06:1 hold. | **NO BET on holding → TAKE PROFIT** (confidence: high) | 4/5 |
| 📊 Wyckoff | Phase E markup driving into 3M-high supply. Stoch 97.7 / RSI 74.9 = potential LPSY / buying-climax zone. No SOW bar, no confirmed distribution structure — but exiting into strength at known supply is the textbook LPSY action. | **NEUTRAL — distribution warning, exit into strength favored** | 3/5 |
| 🧬 Medallion | TP2-overshoot + Stoch 97.7 + RSI ~75 + 3M-high resistance = **4 factors** vs 1 for holding (momentum +3). Red flag: monitor's mode flip keyed on RSI 75.0→74.9 (0.1) — classic fragile single-parameter threshold; deterministic TP rule is more trustworthy. | **STRONG SIGNAL (exit)** | 4/5 |

**Expert Consensus: 3/3 → TAKE PROFITS @ ~$214.45.** If electing to let TP3/∞ run instead, the raised floor $194.05 now guarantees ≥ +$660.75 (+29.4%). Re-entry only on pullback to $180.60 (prior TP2 → new support) if uptrend holds.

### NVDU — 📈 TRAILING → HOLD

**Setup**
- Entry $90.00 → Current **$142.17** | P&L **+58.0% (+$1,408.59, 27 sh)**
- Trail stop **$128.75** (2×ATR) locks in **≥ +$1,046.25 (+43.1%)** minimum
- Risk from here to trail = **−9.4%**; upside unbounded while trend intact (TP3 ∞)
- RSI 49.6 (neutral — reset, not overbought) | Stoch 58.2 | Momentum STRONG (+5) | ATR $6.71 | Regime UPTREND

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Floor locked at +43.1%, open upside, RSI neutral mid-range. Positive-EV hold with defined ruin point. | **BET on hold** (confidence: high) | 5/5 |
| 📊 Wyckoff | Markup Phase E, momentum +5, no SOW, no distribution footprints, RSI/Stoch cooled mid-range after the run — healthy, not climactic. | **NEUTRAL — markup intact, no distribution** | 3/5 |
| 🧬 Medallion | 2×ATR trailing = deterministic trend-following rule; confluence: uptrend + strong momentum +5 + RSI reset = 3 aligned factors, low overfit risk. | **STRONG SIGNAL (hold/trail)** | 4/5 |

**Expert Consensus: 3/3 → HOLD with trail $128.75. Let profits run; exit only if trail is hit.**

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS SCAN** | **$0 deployed** |
| *(exit)* **ZS** | $150.00 | floor now **$194.05** (was $165.30) | ✅ $165.30 | ✅ $180.60 (+18.8%) | +6.3R actual | **TAKE PROFIT 3/3** (avg 3.7/5) | realize **+$966.75** → frees ~$3,216.75 |
| *(hold)* **NVDU** | $90.00 | trail **$128.75** | ✅ $100.06 | ✅ $110.13 | +58.0% actual | **HOLD 3/3** (avg 4.0/5) | unrealized **+$1,408.59** |
| *(watch)* GDDY | $98.87 (SMA20) | $91.23 | — | $99.54 ⚠️ | 0.09:1 ⚠️ | WAIT — 🟡 not actionable; fix TP | $0 — hold cash |
| *(watch)* BCC | $79.22 on SMA50 reclaim | — | — | — | — | WAIT — ⚠️ reclaim first | $0 — hold cash |
| *(watch)* GEV | $976.48 on SMA50 reclaim | — | — | — | — | WAIT — ⚠️ reclaim first | $0 — hold cash |

**Action today:** EXIT ZS near $214.45 (TP1+TP2 done, +43.0%, at 3M-high resistance — or hold on the raised $194.05 floor). HOLD NVDU on trail $128.75 (+58.0%). No new entries.

---

## Appendix — Raw Monitor Output

```
**📡 Entry Monitor — Thu 24 Sep 2026 04:01 ICT**

📡 GDDY Entry Monitor
Price: $96.38 (-1.89%) | RSI: 44.1 | Vol: 1.62x
SMA 20: $98.87 | SMA 50: $96.08 | SMA 100: $90.7
5d: 4🔴/1🟢
• 📏 Testing SMA 20 support at $98.87
📍 VERDICT: 🟡 PULLBACK | Entry: $98.87 (SMA20) | Stop: $91.23 | TP: $99.54

🚨 NVDU EXIT SIGNAL
Price: $142.17 | Entry: $90.00 | P&L: +58.0% ($+1408.59)
Regime: UPTREND | RSI: 49.6 | Stoch: 58.2 | ATR: $6.71
Momentum: STRONG (+5) | R: $6.71
SL: $128.75 (TRAILING 2×ATR) | TP1: $100.06 | TP2: $110.13 | TP3: ∞ (letting run)
• 📈 TRAILING @ $142.17 | Trail stop: $128.75 (2×ATR below price) | P&L: +58.0% — let profits run

🚨 ZS EXIT SIGNAL
Price: $214.45 | Entry: $150.00 | P&L: +43.0% ($+966.75)
Regime: UPTREND | RSI: 74.9 | Stoch: 97.7 | ATR: $10.20
Momentum: STRONG (+3) | R: $10.20
SL: $194.05 (TRAILING 2×ATR) | TP1: $165.3 | TP2: $180.6 | TP3: ∞ (letting run)
• 📈 TRAILING @ $214.45 | Trail stop: $194.05 (2×ATR below price) | P&L: +43.0% — let profits run
• 📏 Near 3M High $215.73 | P&L: +43.0% — resistance zone

📡 BCC Entry Monitor
Price: $77.76 (-1.57%) | RSI: 55.2 | Vol: 0.61x
SMA 20: $76.87 | SMA 50: $79.22 | SMA 100: $75.43
5d: 2🔴/3🟢
• 📏 Testing SMA 50 support at $79.22 — stronger entry
📍 VERDICT: ⚠️ BOUNCE | Risky | Wait for SMA50 reclaim (>$79.22) | Entry then: $79.22

📡 GEV Entry Monitor
Price: $951.82 (+0.16%) | RSI: 55.2 | Vol: 0.73x
SMA 20: $931.07 | SMA 50: $976.48 | SMA 100: $1007.22
5d: 1🔴/4🟢
• 📏 Testing SMA 50 support at $976.48 — stronger entry
• 🟢 4d green streak, RSI 55.2 — bounce confirmed
📍 VERDICT: ⚠️ BOUNCE | Risky | Wait for SMA50 reclaim (>$976.48) | Entry then: $976.48
```
