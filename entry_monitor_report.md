# 📡 Entry Monitor Report — Mon 28 Sep 2026 03:00 ICT

**Run:** `monitor_entries.py` exit 0, 03:00 ICT. First scan since Friday's 22:01 report (weekend gap — prices = Friday close).
**Triggers:** no 🟢 entry verdict (GDDY = 🟡, GEV = ⚠️) → **trailing signals fired on BOTH open positions** → report.
**Data:** tvDatafeed connection timed out ×2 → fallback used (same as Fri runs).

---

## Actionable Entry Signals

**NONE this scan.** No 🟢 entry confirmation → no entry pipeline run.

- **GDDY** $97.14 (−3.64%), RSI 45.9, vol 1.0x, 5d 3🔴/2🟢 — verdict 🟡 PULLBACK, price is *below* SMA20 $99.14. Reclaim trigger $99.14. **Even if it reclaims, the printed setup is broken: TP $99.89 vs stop $90.56 = 0.09:1 R:R ($0.75 reward / $8.58 risk). Do not take as printed — re-derive targets on entry.**
- **GEV** $957.63 (+0.27%), RSI 52.8, vol 0.61x, 5d 0🔴/5🟢 — verdict ⚠️ BOUNCE (risky), still **$15.27 (1.6%) below** SMA50 $972.90 reclaim level. 5-day green streak but on low volume (0.61x) — need the reclaim with volume.

**Budget $2,500: $0 deployed this scan — 100% reserved.**

---

## Changes Since Fri 22:01 Report (weekend close data)

| | Fri 22:01 | Mon 03:00 | Δ |
|---|---|---|---|
| NVDU price | $140.54 | **$141.71** | +0.8% ↑ |
| NVDU trail | $127.94 | **$129.11** | **+$1.17 ↑ (correct direction)** |
| ZS price | $196.19 | **$193.05** | −1.6% ↓ |
| ZS trail | $174.83 | **$171.45** | **−$3.38 ↓ (ratchet bug AGAIN — 3rd erosion)** |
| Combined P&L | +$2,057.43 | **+$2,041.92** | −$15.51 |
| Locked if both trails hit | +$1,396.83 | **+$1,377.72** | −$19.11 |

- **ZS broke below the $194.36 swing low** (closed $193.05) — the level Friday's report flagged as the distribution-confirmation line. One session below, not decisive, but it is no longer "no lower-low follow-through."
- ZS now **−11.0% off the $216.97 supply high** (from −9.7%).
- NVDU recovered and is making new trail highs — trail ratchet working in the right direction for this one.
- Momentum still STRONG on both (NVDU +5, ZS +6), both regimes UPTREND.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|--------|--------|-----------|-----|-------|
| **NVDU** | 📈 TRAILING — hold | n/a (trail **$129.11**) | **+57.5% (+$1,396.17, 27 sh)** | UPTREND, momentum +5, RSI 42.0, ATR $6.30. Floor locks ≥+$1,055.97 (+43.5%). TP1 ✅ TP2 ✅, TP3 ∞ |
| **ZS** | 📈 TRAILING — hold, **floor slipping + swing low broken** | n/a (trail **$171.45**) | **+28.7% (+$645.75, 15 sh)** | UPTREND, momentum +6, RSI 62.6, ATR $10.80. Floor gives ≥+$321.75 (+14.3%) only — was +$372 Friday. −11.0% off $216.97 high |

*Combined open P&L: **+$2,041.92** on $4,680 deployed (+43.6%). Worst case if BOTH trails hit: **≈+$1,377.72 (+29.4%)** locked.*

---

## Expert Analysis — Exit Decisions (Active Positions)

### NVDU — 📈 TRAILING → HOLD ON TRAIL $129.11

**Setup:** $90.00 → **$141.71** | +57.5% (+$1,396.17, 27 sh) | Floor **$129.11** locks ≥+$1,055.97 (+43.5%) | RSI 42.0, Stoch 59.6, momentum **+5**, ATR $6.30, **UPTREND** | TP1 ✅ $99.45, TP2 ✅ $108.90

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Floor locks +43.5% with unbounded upside — positive-EV hold, zero new money at risk. Price recovered Friday's dip and pushed the trail UP $1.17 — the free-floor position improved. New-entry Kelly at $141 ≈ 0 (no fresh signal), but holding a winner on a rising floor is +EV. | **BET on hold via trail** (high) | 4/5 |
| 📊 Wyckoff | Markup Phase E intact — no SOW bar, no upthrust, no climax, trail making higher floor. 5-day drift $146.50 → $141.71 → recovery = normal markup pullback, not SOT (needs 3 thrusts). Break below $129.11 = first distribution warning. | **BULLISH — markup intact** | 4/5 |
| 🧬 Medallion | ~5 aligned factors (UPTREND, +5 momentum, cooled-then-recovered RSI, rising trail). Deterministic trail — no tuned parameters, overfit risk ≈ 0. Position management, not a fitted signal. | **MODERATE SIGNAL (hold — trail governs)** | 3/5 |

**Expert Consensus: 3/3 → HOLD with trail $129.11.** (avg 3.7/5)

### ZS — 📈 TRAILING, swing low broken → HOLD ON TRAIL $171.45 (widening stop risk)

**Setup:** $150.00 → **$193.05** | +28.7% (+$645.75, 15 sh) | Floor **$171.45** locks ≥+$321.75 (+14.3%) only | −11.0% off 3M high $216.97 | RSI 62.6, Stoch 58.6, momentum +6, ATR $10.80, **UPTREND**

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Risk to floor $21.60 (11.2%) vs unbounded reward → ≥1:1 by construction, but the floor keeps leaking: −$51 more locked profit this weekend with **zero new information** (markets closed). Locked edge now only +14.3% — marginal. New entry at $193: **NO BET** (−11% from supply high, broken swing low). | **MARGINAL BET on hold** (low-moderate) | 3/5 |
| 📊 Wyckoff | $216.97 supply event → now **closed below the $194.36 swing low for the first time** — this is the distribution-confirmation level flagged Friday. One session below is not decisive, but the alternative scenario (reclaim $214.64 = markup resumes) just got weaker. Next: reclaim $194+ = shakeout/retest; further lower-low with volume = distribution confirmed → trail handles exit. | **NEUTRAL-BEARISH — low-high structure breaking** | 2/5 |
| 🧬 Medallion | Momentum +6 while price prints lower lows vs the supply high is a scoring artifact (Stoch/RSI lag). After the 3×-volume distribution bar, fresh-entry signal quality is low; weekend drift adds no information. | **WEAK SIGNAL (no fresh edge — trail governs)** | 2/5 |

**Expert Consensus: 3/3 → HOLD with trail $171.45, but this is the weakest hold in the book.** Alternative: take ~+$645 on a bounce toward $194–$214 supply instead of watching the floor erode further. (avg 2.3/5)

---

## ⚠️ Risk Note — trail is not a ratchet (still awaiting your OK)

`monitor_entries.py` computes `trail = price − 2×ATR` fresh every run with **no persisted high-water mark**. This weekend run: NVDU's trail rose (price up), **ZS's fell again $174.83 → $171.45 — third consecutive erosion.**

| | True ratchet | Actual (03:00) |
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

**Action:** HOLD NVDU (trail $129.11) and ZS (trail $171.45). No new entries — budget $2,500 unspent. ZS watch: reclaim $194.36 = shakeout recovery, decisive break lower = distribution confirmed. GDDY: reclaim $99.14 **but only with rebuilt targets**. GEV: wait for reclaim **>$972.90 with volume**. Ratchet fix still pending your OK.

---

## Appendix — Raw Monitor Output

```
**📡 Entry Monitor — Mon 28 Sep 2026 03:00 ICT**

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
