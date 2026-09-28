# 📡 Entry Monitor Report — Mon 28 Sep 2026 20:01 ICT

**Run:** `monitor_entries.py` exit 0, 20:01 ICT (pre-open — US cash opens 20:30 ICT).
**Triggers:** no 🟢 entry verdict (GDDY = 🟡, GEV = ⚠️) → **trailing signals fired on BOTH open positions** → report.
**Data:** tvDatafeed connection timed out ×2 → fallback used. **Every number is byte-identical to the 03:00 ICT report — markets have not traded since Friday close.** Zero new information this run.

---

## Actionable Entry Signals

**NONE this scan.** No 🟢 entry confirmation → no entry pipeline run.

- **GDDY** $97.14 (−3.64%), RSI 45.9, vol 1.0x, 5d 3🔴/2🟢 — verdict 🟡 PULLBACK, price *below* SMA20 $99.14. Reclaim trigger $99.14. **Printed setup is broken: TP $99.89 vs stop $90.56 = 0.09:1 R:R ($0.75 reward / $8.58 risk). Do not take as printed — re-derive targets on entry.**
- **GEV** $957.63 (+0.27%), RSI 52.8, vol 0.61x, 5d 0🔴/5🟢 — verdict ⚠️ BOUNCE (risky), still **$15.27 (1.6%) below** SMA50 $972.90 reclaim level. 4-day green streak but on 0.61x volume — need the reclaim *with* volume.

**Budget $2,500: $0 deployed this scan — 100% reserved.**

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|--------|--------|-----------|-----|-------|
| **NVDU** | 📈 TRAILING — hold | n/a (trail **$129.11**) | **+57.5% (+$1,396.17, 27 sh)** | UPTREND, momentum +5, RSI 42.0, ATR $6.30. Floor locks ≥+$1,055.97 (+43.5%). TP1 ✅ TP2 ✅, TP3 ∞ |
| **ZS** | 📈 TRAILING — hold, **floor eroding + swing low broken** | n/a (trail **$171.45**) | **+28.7% (+$645.75, 15 sh)** | UPTREND, momentum +6, RSI 62.6, ATR $10.80. Floor gives ≥+$321.75 (+14.3%) only — was +$372 Fri. −11.0% off $216.97 high |

*Combined open P&L: **+$2,041.92** on $4,680 deployed (+43.6%). Worst case if BOTH trails hit: **≈+$1,377.72 (+29.4%)** locked.*

**No change vs 03:00 ICT run** — same prices, same trails, same P&L. Pre-open duplicate; verdicts carry over unchanged (NVDU 3/3 HOLD avg 3.7/5, ZS 3/3 HOLD avg 2.3/5 — weakest hold in the book).

---

## ⚠️ Risk Note — trail is not a ratchet (still awaiting your OK)

`monitor_entries.py` computes `trail = price − 2×ATR` fresh every run with **no persisted high-water mark**. ZS's floor has now eroded **3 consecutive runs** ($194.36 → $171.45, −$22.91 cumulative) with markets *closed* — pure recompute drift, no market information.

| | True ratchet | Actual (20:01) |
|---|---|---|
| ZS floor | $194.36 (Fri 04:00 level) | **$171.45** (−$22.91 cumulative) |
| Locked profit | +$665 (at $194.36 floor) | **+$321.75** (−$343 given back) |

**Recommended fix:** persist `entry_monitor_trail.json` and use `trail = max(prev_trail, price − 2×ATR)`. **Not applied** — exit-logic/risk change, waits for your confirmation.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS SCAN** | **$0 deployed** |
| *(watch)* **GDDY** | $99.14 on SMA20 reclaim | $90.56 | $99.89 | — | 0.09:1 ⚠️ | 🟡 not actionable — broken R:R, re-derive targets | reserved |
| *(watch)* **GEV** | $972.90 on SMA50 reclaim | — | — | — | — | ⚠️ not actionable — 1.6% below trigger | reserved |
| *(hold)* **NVDU** | $90.00 | trail **$129.11** | ✅ $99.45 | ✅ $108.90 | +57.5% actual | **HOLD ON TRAIL 3/3** (avg 3.7/5) | unrealized **+$1,396.17** |
| *(hold)* **ZS** | $150.00 | trail **$171.45** | ✅ $166.20 | ✅ $182.40 | +28.7% actual | **HOLD ON TRAIL 3/3** (avg 2.3/5) — weakest hold | unrealized **+$645.75** |

**Action:** HOLD NVDU (trail $129.11) and ZS (trail $171.45). No new entries — budget $2,500 unspent. ZS watch: reclaim $194.36 = shakeout recovery, decisive break lower = distribution confirmed. GDDY: reclaim $99.14 **but only with rebuilt targets**. GEV: wait for reclaim **>$972.90 with volume**. Ratchet fix still pending your OK. **Next fresh information: cash open 20:30 ICT.**

---

## Appendix — Raw Monitor Output

```
**📡 Entry Monitor — Mon 28 Sep 2026 20:01 ICT**

📡 **GDDY Entry Monitor**
Price: $97.14 (-3.64%) | RSI: 45.9 | Vol: 1.0x
SMA 20: $99.14 | SMA 50: $96.28 | SMA 100: $90.93
5d: 3🔴/2🟢
• 📏 Testing SMA 20 support at $99.14
📍 **VERDICT: 🟡 PULLBACK** | Entry: $99.14 (SMA20) | Stop: $90.56 | TP: $99.89

🚨 **NVDU EXIT SIGNAL**
Price: $141.71 | Entry: $90.00 | P&L: +57.5% ($+1396.17)
Regime: UPTREND | RSI: 42.0 | Stoch: 59.6 | ATR: $6.30
Momentum: STRONG (+5) | R: $6.30
SL: $129.11 (TRAILING 2×ATR) | TP1: $99.45 | TP2: $108.9 | TP3: ∞ (letting run)
• 📈 **TRAILING** @ $141.71 | Trail stop: $129.11 (2×ATR below price) | P&L: +57.5% — let profits run

🚨 **ZS EXIT SIGNAL**
Price: $193.05 | Entry: $150.00 | P&L: +28.7% ($+645.75)
Regime: UPTREND | RSI: 62.6 | Stoch: 58.6 | ATR: $10.80
Momentum: STRONG (+6) | R: $10.80
SL: $171.45 (TRAILING 2×ATR) | TP1: $166.2 | TP2: $182.4 | TP3: ∞ (letting run)
• 📈 **TRAILING** @ $193.05 | Trail stop: $171.45 (2×ATR below price) | P&L: +28.7% — let profits run

📡 **GEV Entry Monitor**
Price: $957.63 (+0.27%) | RSI: 52.8 | Vol: 0.61x
SMA 20: $931.36 | SMA 50: $972.9 | SMA 100: $1004.98
5d: 0🔴/5🟢
• 📏 Testing SMA 50 support at $972.90 — stronger entry
• 🟢 4d green streak, RSI 52.8 — bounce confirmed
📍 **VERDICT: ⚠️ BOUNCE** | Risky | Wait for SMA50 reclaim (>$972.9) | Entry then: $972.9
```
