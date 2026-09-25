# 📡 Entry Monitor Report — Fri 25 Sep 2026 22:01 ICT

**Run:** `monitor_entries.py` exit 0, 22:01 ICT.
**Triggers:** no 🟢 entry verdict (GEV = ⚠️ testing SMA50) → **exit/trailing signals fired on BOTH open positions** → report.
**Data:** tvDatafeed connection timed out → Yahoo fallback used (same as 21:00 run).

---

## Actionable Entry Signals

**NONE this scan.** No 🟢 entry confirmation → no entry pipeline run.

- **GEV** $949.77 (−0.55%), RSI 51.4, vol 0.14x, 5d 1🔴/4🟢 — still **below** SMA50 $972.75, verdict ⚠️ BOUNCE (risky). Entry only on reclaim **>$972.75**. Price slipped $6.6 vs 21:00 scan.

**Budget $2,500: $0 deployed this scan — 100% reserved.**

---

## Changes Since 21:00 Report

- **Both trails slipped DOWN this run — the ratchet bug now hits NVDU too.**
  - NVDU trail $129.25 → **$127.94** (price −0.8%, 141.63 → 140.54). Previous report explicitly noted NVDU "working correctly" — not anymore.
  - ZS trail $179.11 → **$174.83** (price −1.8%, 199.71 → 196.19). Locked floor keeps eroding after the −7.7% supply bar.
- Combined open P&L: +$2,139.59 → **+$2,057.43** (−$82).
- Guaranteed-if-both-trails-hit: +$1,496 → **+$1,396.83** (−$99) — second consecutive hour of give-back with **zero new adverse news**, purely trail recomputation.
- ZS now −9.7% off the $216.97 supply high (two sessions). NVDU −4.1% off $146.50 5-day high, RSI cooled to 40.8 (no longer overbought).
- Momentum still STRONG on both (NVDU +5, ZS +6), both regimes UPTREND.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|--------|--------|-----------|-----|-------|
| **NVDU** | 📈 TRAILING — hold | n/a (trail **$127.94**) | **+56.2% (+$1,364.58, 27 sh)** | UPTREND, momentum +5, RSI 40.8. Floor locks ≥+$1,024 (+42.2%) — slipped $35 since 21:00 |
| **ZS** | 📈 TRAILING — hold, **floor slipping** | n/a (trail **$174.83**) | **+30.8% (+$692.85, 15 sh)** | UPTREND, momentum +6, RSI 64.8. Floor gives ≥+$372 (+16.6%) only — was +$437 at 21:00, +$665 at 04:00 |

*Combined open P&L: **+$2,057.43** on $4,680 deployed (+43.9%). Worst case if BOTH trails hit: **≈+$1,396.83 (+29.8%)** locked.*

---

## Expert Analysis — Exit Decisions (Active Positions)

### NVDU — 📈 TRAILING → HOLD ON TRAIL $127.94

**Setup:** $90.00 → **$140.54** | +56.2% (+$1,364.58, 27 sh) | Floor **$127.94** locks ≥+$1,024 (+42.2%) | RSI 40.8, Stoch 55.8, momentum **+5**, ATR $6.30, **UPTREND** | TP1 ✅ $99.45, TP2 ✅ $108.90

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Floor locks +42.2% with unbounded upside — positive-EV hold, zero new money at risk. RSI 40.8 after −4% drift = cooled, not distribution. New-entry Kelly at $140 ≈ 0 (no fresh signal), but a winner on a free floor is +EV. | **BET on hold via trail** (moderate-high) | 4/5 |
| 📊 Wyckoff | Markup Phase E intact — no SOW bar, no upthrust, no climax. 4-day drift $146.50 → $140.54 = mild pullback within markup (single move, not SOT — needs 3 thrusts). Break below $127.94 = first distribution warning. | **BULLISH — markup intact** | 4/5 |
| 🧬 Medallion | ~5 aligned factors (UPTREND, +5 momentum, neutral RSI, trail discipline). Deterministic trail — no tuned parameters, overfit risk ≈ 0. Position management, not a fresh fitted signal. | **MODERATE SIGNAL (hold — trail governs)** | 3/5 |

**Expert Consensus: 3/3 → HOLD with trail $127.94.** (avg 3.7/5)

### ZS — 📈 TRAILING, second bar lower after supply event → HOLD ON TRAIL $174.83

**Setup:** $150.00 → **$196.19** | +30.8% (+$692.85, 15 sh) | Floor **$174.83** locks ≥+$372 (+16.6%) | 3M high **$216.97** above, now −9.7% from it | RSI 64.8, Stoch 64.0, momentum +6, ATR $10.68, **UPTREND**

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Risk to floor $21.36 (10.9%) vs unbounded reward → ≥1:1 by construction, but the floor is a leaking bucket: gave back another $64 today with no new adverse information. −9.7% over two sessions from supply = volatility event; edge at the hold level is marginal but positive. New entry: **NO BET**. | **MARGINAL BET on hold** (moderate) | 3/5 |
| 📊 Wyckoff | $164.54 → $214.64 markup (+30%) into prior supply, then high-volume −7.7% bar = **SOW candidate**, now a second lower session (196.19) but **no lower-low follow-through below $194.36 yet** — not confirmed LPSY/UTAD. Reclaim $214.64 → markup resumes; decisive break of $194 → distribution confirmed, trail handles exit. | **NEUTRAL — supply event unresolved** | 3/5 |
| 🧬 Medallion | Momentum +6 on a −9.7% two-day move remains an artifact (RSI/Stoch "cooling" scoring). After a 3×-volume distribution bar, fresh-entry signal quality is low; no new information from this hour's drift. | **WEAK SIGNAL (no fresh edge — trail governs)** | 2/5 |

**Expert Consensus: 3/3 → HOLD with trail $174.83.** Alternative: realize ~+$660 on any bounce toward $214.64 supply. (avg 2.7/5)

---

## ⚠️ Risk Note — trail is not a ratchet (still awaiting your OK)

`monitor_entries.py` computes `trail = price − 2×ATR` fresh every run with **no persisted high-water mark**, so the floor moves DOWN whenever price is below the prior computation. At 21:00 this had hit ZS only; **this run hit NVDU too** ($129.25 → $127.94).

| | True ratchet | Actual (22:01) |
|---|---|---|
| NVDU floor | $129.25 | **$127.94** (−$1.31) |
| ZS floor | $194.36 (04:00 level) | **$174.83** (−$19.53) |
| Locked profit | +$1,725 | **+$1,396.83** (−$328) |

**Recommended fix:** persist `entry_monitor_trail.json` and use `trail = max(prev_trail, price − 2×ATR)`. **Not applied** — exit-logic/risk change, waits for your confirmation.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS SCAN** | **$0 deployed** |
| *(watch)* **GEV** | $972.75 on SMA50 reclaim | — | — | — | — | N/A — ⚠️ BOUNCE, not actionable | reserved |
| *(hold)* **NVDU** | $90.00 | trail **$127.94** | ✅ $99.45 | ✅ $108.90 | +56.2% actual | **HOLD ON TRAIL 3/3** (avg 3.7/5) | unrealized **+$1,364.58** |
| *(hold)* **ZS** | $150.00 | trail **$174.83** | ✅ $166.02 | ✅ $182.04 | +30.8% actual | **HOLD ON TRAIL 3/3** (avg 2.7/5) | unrealized **+$692.85** |

**Action:** HOLD NVDU (trail $127.94) and ZS (trail $174.83). No new entries — budget $2,500 unspent. ZS watch: reclaim $214.64 = markup resumes, break below $194.36 = distribution confirmed. GEV: wait for reclaim **>$972.75**.

---

## Appendix — Raw Monitor Output

```
**📡 Entry Monitor — Fri 25 Sep 2026 22:01 ICT**

🚨 NVDU EXIT SIGNAL
Price: $140.54 | Entry: $90.00 | P&L: +56.2% ($+1364.58)
Regime: UPTREND | RSI: 40.8 | Stoch: 55.8 | ATR: $6.30
Momentum: STRONG (+5) | R: $6.30
SL: $127.94 (TRAILING 2×ATR) | TP1: $99.45 | TP2: $108.9 | TP3: ∞
• 📈 TRAILING @ $140.54 | Trail stop: $127.94 | P&L: +56.2% — let profits run

🚨 ZS EXIT SIGNAL
Price: $196.19 | Entry: $150.00 | P&L: +30.8% ($+692.85)
Regime: UPTREND | RSI: 64.8 | Stoch: 64.0 | ATR: $10.68
Momentum: STRONG (+6) | R: $10.68
SL: $174.83 (TRAILING 2×ATR) | TP1: $166.02 | TP2: $182.04 | TP3: ∞
• 📈 TRAILING @ $196.19 | Trail stop: $174.83 | P&L: +30.8% — let profits run

📡 GEV Entry Monitor
Price: $949.77 (-0.55%) | RSI: 51.4 | Vol: 0.14x
SMA 20: $930.97 | SMA 50: $972.75 | SMA 100: $1004.9
5d: 1🔴/4🟢
• 📏 Testing SMA 50 support at $972.75 — stronger entry
📍 VERDICT: ⚠️ BOUNCE | Risky | Wait for SMA50 reclaim (>$972.75) | Entry then: $972.75
```
