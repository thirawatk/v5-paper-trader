# 📡 Entry Monitor Report — Fri 25 Sep 2026 21:00 ICT

**Run:** `monitor_entries.py` exit 0, 21:00 ICT (US session +30 min).
**Triggers:** no 🟢 entry verdict (GDDY = 🟡, GEV = ⚠️) → **exit/trailing signals fired on BOTH open positions** → report.
**Data:** tvDatafeed connection timed out → Yahoo fallback used. Independently verified: ZS live $198.04 vs monitor $199.71, NVDU live $141.53 vs monitor $141.63 → fallback accurate within ~0.2%.

---

## Actionable Entry Signals

**NONE this scan.** No 🟢 entry confirmation → no entry pipeline run.

- **GDDY** $98.47 (−2.32%), RSI 47.1 — price is **below** SMA20 $99.20, verdict 🟡 PULLBACK. Monitor TP $100.02 vs stop $90.59 = **0.20:1 R:R**. Not actionable.
- **GEV** $956.34, RSI 52.6, 5d 0🔴/5🟢 — still **below** SMA50 $972.88, verdict ⚠️ BOUNCE (risky). Entry only on reclaim **>$972.88**.

**Budget $2,500: $0 deployed this scan — 100% reserved.**

---

## Changes Since 04:00 Report (the material move)

- **ZS: −7.7% today.** $214.64 (Sep 24 close = 3M-high area) → **$198.04 live**. P&L **+43.1% → +32.0%** (−$249 unrealized). Volume 1.33M in the first ~45 min vs ~2.5M typical **full day** → ~3× pace. No confirmed catalyst in a quick news scan; the drop printed directly into the 3M-high supply zone ($216.97) after a +30% run from $164.54 in early Sep.
- **ZS trail FLOOR SLIPPED $194.36 → $179.11** — locked profit fell from **+$665 (+29.6%) to +$437 (+19.4%)**. Cause is a real implementation gap (see Risk Note): the trail is recomputed as `price − 2×ATR` every run with **no persisted high-water mark**, so it moves DOWN with price.
- **NVDU: flat.** $141.06 → **$141.63**, P&L +56.7% → **+57.4% (+$1,394)**. Trail tightened up $127.94 → **$129.25** (correct direction). Drifted −3.7% off the $146.50 5-day high; RSI cooled 43.8 → 41.9.
- Combined open P&L: +$2,348 → **+$2,140** (−$208). Guaranteed-if-both-trails-hit: +$1,690 → **+$1,496**.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|--------|--------|-----------|-----|-------|
| **NVDU** | 📈 TRAILING — hold | n/a (trail **$129.25**) | **+57.4% (+$1,394.01, 27 sh)** | UPTREND, momentum +5, RSI 41.9 neutral. Floor locks ≥+$1,060 (+43.6%). Room to run |
| **ZS** | 📈 TRAILING — hold, **floor slipped** | n/a (trail **$179.11**) | **+33.1% (+$745.58, 15 sh)** | −7.7% today into 3M-high supply, volume ~3× pace. Floor gives ≥+$437 (+19.4%) only — was +$665 yesterday |

*Combined open P&L: **+$2,139.59** on $4,680 deployed (+45.7%). Worst case if BOTH trails hit: **≈+$1,496 (+32.0%)** locked.*

---

## Expert Analysis — Exit Decisions (Active Positions)

### NVDU — 📈 TRAILING → HOLD ON TRAIL $129.25

**Setup:** $90.00 → **$141.63** | +57.4% (+$1,394, 27 sh) | Floor **$129.25** locks ≥+$1,060 (+43.6%) | RSI 41.9, Stoch 59.3, momentum **+5**, ATR $6.19, **UPTREND** | TP1 ✅ $99.28, TP2 ✅ $108.57

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Floor locks +43.6% with unbounded upside — positive-EV hold, zero new money at risk. RSI 41.9 = not chasing an extended price. New-entry Kelly at $141 ≈ 0 (no fresh signal), but holding a winner on a free floor is +EV. | **BET on hold via trail** (moderate-high) | 4/5 |
| 📊 Wyckoff | Markup Phase E intact — no SOW bar, no upthrust, no distribution climax. 3-day drift $146.50→$141.20 is a mild pullback within markup, not SOT (single thrust). Break below $129.25 = first distribution warning. | **BULLISH — markup intact** | 4/5 |
| 🧬 Medallion | ~5 aligned factors (UPTREND, +5 momentum, neutral RSI, trail discipline). Deterministic trail — no tuned parameters, overfit risk ≈ 0. This is position management, not a fresh fitted signal. | **MODERATE SIGNAL (hold — trail governs)** | 3/5 |

**Expert Consensus: 3/3 → HOLD with trail $129.25.** (avg 3.7/5)

### ZS — 📈 TRAILING after −7.7% supply-bar day → HOLD ON TRAIL $179.11

**Setup:** $150.00 → **$199.71** | +33.1% (+$745.58, 15 sh) | Floor **$179.11** locks ≥+$437 (+19.4%) | 3M high **$216.97** above, 52w high $336.99 | RSI 67.5, Stoch 70.1, momentum +6, ATR $10.30, **UPTREND**

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Risk to floor $20.60 (10.3%) vs unbounded reward → ≥1:1 by construction, but the floor itself gave back $229 today because it isn't a true ratchet. A −7.7% single-day move on 3× volume is a volatility event, not proof the edge is gone. New entry after that bar: **NO BET** — no edge evidence. | **MARGINAL BET on hold** (moderate) | 3/5 |
| 📊 Wyckoff | $164.54 → $214.64 markup (+30%) driving into prior supply, then a high-volume open print −7.7% = **first genuine SOW candidate**. One bar ≠ structure: not yet LPSY/UTAD. Reclaim $214.64 → markup resumes; lower-low follow-through tomorrow → distribution risk, and the trail handles the exit. | **NEUTRAL — supply event at range top** | 3/5 |
| 🧬 Medallion | Momentum score **rose +3 → +6 on a −7% day** — an artifact: RSI re-entering 50-70 (+1) and Stoch leaving >90 (+1) reward "cooling off". The score is mean-reversion flavored and **does not de-risk on sharp pullbacks**. Fresh-entry signal quality after a 3×-volume distribution bar: low. | **WEAK SIGNAL (no fresh edge — trail governs)** | 2/5 |

**Expert Consensus: 3/3 → HOLD with trail $179.11.** Alternative: realize +$720 on any bounce toward $214.64 supply. (avg 2.7/5)

---

## ⚠️ Risk Note — trail is not a ratchet (needs your OK to change)

`monitor_entries.py:1264` computes `trail_stop = price − 2×ATR` fresh on every run, and `stop_loss = max(stop_loss, trail_stop)` only ratchets against **entry-based** levels (line 1175-1183). The script persists **no state file**, so the trail has no memory of its own prior high.

| | True ratchet | Actual behaviour today |
|---|---|---|
| ZS floor | would stay **$194.36** | fell to **$179.11** |
| Locked profit | **+$665 (+29.6%)** | **+$437 (+19.4%)** |
| Give-back on a −7% day | $0 | **−$228.75** |

**Recommended fix:** persist a per-ticker high-water trail (e.g. `entry_monitor_trail.json`) and use `trail = max(prev_trail, price − 2×ATR)`. **Not applied** — it's an exit-logic/risk change, so it waits for your confirmation.

*Side note: `NVDU` is working correctly — its floor only moved UP today ($127.94 → $129.25) because price was flat.*

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS SCAN** | **$0 deployed** |
| *(watch)* **GDDY** | $99.20 on SMA20 reclaim | $90.59 | $100.02 | — | 0.20:1 ❌ | N/A — 🟡 PULLBACK, not actionable | reserved |
| *(watch)* **GEV** | $972.88 on SMA50 reclaim | — | — | — | — | N/A — ⚠️ BOUNCE, not actionable | reserved |
| *(hold)* **NVDU** | $90.00 | trail **$129.25** | ✅ $99.28 | ✅ $108.57 | +57.4% actual | **HOLD ON TRAIL 3/3** (avg 3.7/5) | unrealized **+$1,394.01** |
| *(hold)* **ZS** | $150.00 | trail **$179.11** | ✅ $165.45 | ✅ $180.90 | +33.1% actual | **HOLD ON TRAIL 3/3** (avg 2.7/5) | unrealized **+$745.58** |

**Action today:** HOLD NVDU (trail $129.25) and ZS (trail $179.11). No new entries — budget $2,500 unspent. Watch ZS tomorrow for follow-through after the −7.7% supply bar: lower-low = distribution risk, reclaim $214.64 = markup resumes. GEV: wait for reclaim **>$972.88**. GDDY: 🟡, R:R too thin.

---

## Appendix — Raw Monitor Output

```
**📡 Entry Monitor — Fri 25 Sep 2026 21:00 ICT**

📡 GDDY Entry Monitor
Price: $98.47 (-2.32%) | RSI: 47.1 | Vol: 0.1x
SMA 20: $99.2 | SMA 50: $96.31 | SMA 100: $90.94
5d: 3🔴/2🟢
• 📏 Testing SMA 20 support at $99.20
📍 VERDICT: 🟡 PULLBACK | Entry: $99.2 (SMA20) | Stop: $90.59 | TP: $100.02

🚨 NVDU EXIT SIGNAL
Price: $141.63 | Entry: $90.00 | P&L: +57.4% ($+1394.01)
Regime: UPTREND | RSI: 41.9 | Stoch: 59.3 | ATR: $6.19
Momentum: STRONG (+5) | R: $6.19
SL: $129.25 (TRAILING 2×ATR) | TP1: $99.28 | TP2: $108.57 | TP3: ∞
• 📈 TRAILING @ $141.63 | Trail stop: $129.25 | P&L: +57.4% — let profits run

🚨 ZS EXIT SIGNAL
Price: $199.71 | Entry: $150.00 | P&L: +33.1% ($+745.58)
Regime: UPTREND | RSI: 67.5 | Stoch: 70.1 | ATR: $10.30
Momentum: STRONG (+6) | R: $10.30
SL: $179.11 (TRAILING 2×ATR) | TP1: $165.45 | TP2: $180.9 | TP3: ∞
• 📈 TRAILING @ $199.71 | Trail stop: $179.11 | P&L: +33.1% — let profits run

📡 GEV Entry Monitor
Price: $956.34 (+0.14%) | RSI: 52.6 | Vol: 0.06x
SMA 20: $931.29 | SMA 50: $972.88 | SMA 100: $1004.97
5d: 0🔴/5🟢
• 📏 Testing SMA 50 support at $972.88 — stronger entry
• 🟢 4d green streak, RSI 52.6 — bounce confirmed
📍 VERDICT: ⚠️ BOUNCE | Risky | Wait for SMA50 reclaim (>$972.88) | Entry then: $972.88
```
