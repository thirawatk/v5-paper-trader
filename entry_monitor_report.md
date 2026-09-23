# 📡 Entry Monitor Report — Thu 24 Sep 2026 03:00 ICT

**Run:** `monitor_entries.py` exit 0. No 🟢 entry verdicts. Exit/trailing signals fired on BOTH open positions → report triggered.

---

## Actionable Entry Signals

**NONE this scan.** GDDY is 🟡 PULLBACK, BCC and GEV are ⚠️ BOUNCE (awaiting SMA50 reclaim). No expert pipeline run for entries — none actionable.

⚠️ **GDDY plan bug:** Entry $98.87 / Stop $91.23 / TP $99.54 → reward $0.67 vs risk $7.64 = **0.09:1 R:R**. TP looks wrong in the monitor — must be fixed before any GDDY entry is taken.

**Budget $2,500:** no deployment this scan — 100% reserved. ZS exit would free ~$3,218.

---

## Expert Analysis — Exit Decisions (Active Positions)

### ZS — 🎯 TP2 HIT → TAKE PROFITS

**Setup**
- Entry $150.00 → Current **$214.52** | P&L **+43.0% (+$967.80, 15 sh)**
- TP2 $180.60 (3.0R) **exceeded by +18.8%** — trade at **+6.3R** (R = $10.20)
- RSI 75.0 | Stoch 97.9 | ATR $10.20 | Momentum STRONG (+3) | Regime UPTREND
- 3M high $215.73 sits only **+0.6% above** price (resistance zone)
- Trail/SL $165.30 (1.5×ATR) = **−22.8% give-back** from current price

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Immediate hold R:R to 3M high vs trail = $1.21 vs $49.22 ≈ **0.03:1**. Certain +$64.52/sh beats a negative-EV hold at overbought extreme. | **NO BET on holding → TAKE PROFIT** (confidence: high) | 4/5 |
| 📊 Wyckoff | Phase E markup driving into 3M-high supply. Stoch 97.9 / RSI 75 = potential LPSY / buying-climax zone. No confirmed distribution structure yet — no SOW bar on record. | **NEUTRAL — distribution warning** at resistance | 3/5 |
| 🧬 Medallion | Exit is a pre-committed TP2 rule (deterministic, zero curve-fit). Confluence: TP2 overshoot + Stoch 97.9 + RSI 75 + 3M-high resistance = 4 factors vs 1 for holding (momentum). | **STRONG SIGNAL (exit)** | 4/5 |

**Expert Consensus: 3/3 → TAKE PROFITS @ ~$214.52.** Re-entry only on pullback to $180.60 (prior TP2 → new support) if uptrend holds.

### NVDU — 📈 TRAILING → HOLD

**Setup**
- Entry $90.00 → Current **$142.31** | P&L **+58.1% (+$1,412.37, 27 sh)**
- Trail stop **$128.89** (2×ATR) locks in **≥ +$1,050 (+43.2%)** minimum
- Risk from here to trail = **−9.4%**; upside unbounded while trend intact
- RSI 49.7 (neutral — reset, not overbought) | Stoch 58.7 | Momentum STRONG (+5) | ATR $6.71 | Regime UPTREND

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Floor locked at +43.2%, open upside, RSI neutral. Positive-EV hold with defined ruin point. | **BET on hold** (confidence: high) | 5/5 |
| 📊 Wyckoff | Markup Phase E, momentum +5, no SOW, no distribution footprints, RSI reset mid-range after run. | **NEUTRAL — markup intact, no distribution** | 3/5 |
| 🧬 Medallion | 2×ATR trailing = deterministic trend-following rule; confluence: uptrend + strong momentum + RSI reset. Low overfit risk. | **STRONG SIGNAL (hold/trail)** | 4/5 |

**Expert Consensus: 3/3 → HOLD with trail $128.89. Let profits run; exit only if trail is hit.**

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **ZS** | 🎯 **TAKE PROFIT — TP2 +19% overshoot** | ~$214.52 | **+43.0% (+$967.80)** | Stoch 97.9, 0.6% below 3M high $215.73; TP2 discipline says realize. Frees ~$3,218 |
| **NVDU** | 📈 TRAILING — hold | n/a | **+58.1% (+$1,412.37)** | Trail $128.89 (2×ATR) locks ≥+43.2%; auto-exit when hit |

*Combined open P&L: **+$2,380.17** on $4,680 deployed (+50.9%).*

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS SCAN** | **$0 deployed** |
| *(exit)* **ZS** | — | floor $165.3 | — | ✅ $180.6 hit | 3.0R done (+6.3R actual) | **TAKE PROFIT 3/3** (avg 3.7/5) | realize **+$967.80** → frees ~$3,218 |
| *(hold)* NVDU | — | trail $128.89 | — | — | — | **HOLD 3/3** (avg 4.0/5) | unrealized **+$1,412.37** |
| *(watch)* GDDY | $98.87 (SMA20) | $91.23 | — | $99.54 ⚠️ | 0.09:1 ⚠️ | WAIT — 🟡 not actionable; fix TP | $0 — hold cash |
| *(watch)* BCC | $79.22 on SMA50 reclaim | — | — | — | — | WAIT — ⚠️ reclaim first | $0 — hold cash |
| *(watch)* GEV | $976.48 on SMA50 reclaim | — | — | — | — | WAIT — ⚠️ reclaim first | $0 — hold cash |

**Action today:** EXIT ZS near $214.52 (TP2 done, +43.0%). HOLD NVDU on trail $128.89 (+58.1%). No new entries.

---

## Appendix — Raw Monitor Output

```
**📡 Entry Monitor — Thu 24 Sep 2026 03:00 ICT**

📡 GDDY Entry Monitor
Price: $96.42 (-1.85%) | RSI: 44.2 | Vol: 1.31x
SMA 20: $98.87 | SMA 50: $96.08 | SMA 100: $90.7
5d: 4🔴/1🟢
• 📏 Testing SMA 20 support at $98.87
📍 VERDICT: 🟡 PULLBACK | Entry: $98.87 (SMA20) | Stop: $91.23 | TP: $99.54

🚨 NVDU EXIT SIGNAL
Price: $142.31 | Entry: $90.00 | P&L: +58.1% ($+1412.37)
Regime: UPTREND | RSI: 49.7 | Stoch: 58.7 | ATR: $6.71
Momentum: STRONG (+5) | R: $6.71
SL: $128.89 (TRAILING 2×ATR) | TP1: $100.06 | TP2: $110.13 | TP3: ∞ (letting run)
• 📈 TRAILING @ $142.31 | Trail stop: $128.89 (2×ATR below price) | P&L: +58.1% — let profits run

🚨 ZS EXIT SIGNAL
Price: $214.52 | Entry: $150.00 | P&L: +43.0% ($+967.80)
Regime: UPTREND | RSI: 75.0 | Stoch: 97.9 | ATR: $10.20
Momentum: STRONG (+3) | R: $10.20
SL: $165.3 (1.5×ATR) | TP1: $165.3 (1.5R) | TP2: $180.6 (3.0R)
• 🎯 TP2 HIT $180.6 (3.0R) | P&L: +43.0% — take profits, momentum: STRONG
• 📏 Near 3M High $215.73 | P&L: +43.0% — resistance zone

📡 BCC Entry Monitor
Price: $77.78 (-1.54%) | RSI: 55.3 | Vol: 0.37x
SMA 20: $76.87 | SMA 50: $79.22 | SMA 100: $75.43
5d: 2🔴/3🟢
• 📏 Testing SMA 50 support at $79.22 — stronger entry
📍 VERDICT: ⚠️ BOUNCE | Risky | Wait for SMA50 reclaim (>$79.22) | Entry then: $79.22

📡 GEV Entry Monitor
Price: $951.65 (+0.14%) | RSI: 55.1 | Vol: 0.61x
SMA 20: $931.06 | SMA 50: $976.48 | SMA 100: $1007.22
5d: 1🔴/4🟢
• 📏 Testing SMA 50 support at $976.48 — stronger entry
• 🟢 4d green streak, RSI 55.1 — bounce confirmed
📍 VERDICT: ⚠️ BOUNCE | Risky | Wait for SMA50 reclaim (>$976.48) | Entry then: $976.48
```
