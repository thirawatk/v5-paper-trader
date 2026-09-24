# 📡 Entry Monitor Report — Fri 25 Sep 2026 03:00 ICT

**Run:** `monitor_entries.py` exit 0. No 🟢 entry verdicts (GEV = ⚠️ BOUNCE, not actionable). Exit/trailing signals fired on BOTH open positions → report triggered. (tvDatafeed connection timed out — data served via fallback; prices may be slightly delayed.)

---

## Actionable Entry Signals

**NONE this scan.** No 🟢 entry confirmations — no expert entry pipeline run.

**GEV watch:** $954.99 (+0.33%), RSI 52.4, vol 0.63x — still BELOW SMA 50 ($974.48), testing support. Verdict ⚠️ BOUNCE / Risky. Entry only on reclaim >$974.48.

**Budget $2,500:** no deployment this scan — 100% reserved.

---

## Changes Since 22:00 Report

- **NVDU: +52.5% → +56.8%** — price $137.23 → **$141.16**, RECLAIMED SMA20 — trend-weakening flag cleared. Regime PULLBACK → **UPTREND**, momentum +3 → **+5**, RSI 40.8 → 43.9. Trail floor $124.11 → **$128.04** (locks ≥+$1,027, +42.3%).
- **ZS: +42.6% → +43.2%** — price $213.93 → **$214.74**, now only **+1.06% ($2.23)** below 3M high $216.97. Trail floor $193.73 → **$194.46** (locks ≥+$667, +29.6%). RSI 72.8 → 73.4, Stoch 96.1, momentum +3, regime UPTREND.
- Combined open P&L: +$2,234.16 → **+$2,352.34** (+$118.18 improvement).

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|--------|--------|-----------|-----|-------|
| **NVDU** | 📈 TRAILING — hold, trend recovered | n/a (trail $128.04) | **+56.8% (+$1,381.32, 27 sh)** | Back above SMA20, regime UPTREND, momentum +5. Trail 2×ATR locks ≥+$1,027 (+42.3%). RSI 43.9 — room to run |
| **ZS** | 📈 TRAILING — hold at resistance | n/a (trail $194.46) | **+43.2% (+$971.02, 15 sh)** | 3M high $216.97 only +1.06% above — supply zone. Trail locks ≥+$667 (+29.6%). RSI 73.4 / Stoch 96.1 overbought |

*Combined open P&L: **+$2,352.34** on $4,680 deployed (+50.3%). Worst case if BOTH trails hit: **≈+$1,694 (+36.2%)** locked.*

---

## Expert Analysis — Exit Decisions (Active Positions)

### NVDU — 📈 TRAILING, trend recovered → HOLD ON TRAIL

**Setup**
- Entry $90.00 → Current **$141.16** | P&L **+56.8% (+$1,381.32, 27 sh)**
- Trail stop **$128.04** (2×ATR) locks in **≥ +$1,027 (+42.3%)** minimum
- RSI 43.9 | Stoch 55.1 | Momentum **STRONG (+5)** | ATR $6.56 | Regime **UPTREND** (reclaimed SMA20)

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Floor locks +42.3% with unbounded upside — positive-EV hold, defined ruin point. Trend-weakening signal from 22:00 cleared (back above SMA20, momentum +3→+5). Edge carried by trail, but structure improved: conviction and trail now align. | **BET on hold via trail** (confidence: moderate-high) | 4/5 |
| 📊 Wyckoff | Markup Phase E resumed after a one-session test — reclaim of SMA20 reads as Back Up / test of broken structure holding. No SOW bar, no distribution climax. Last shakeout direction still up. Break below $128.04 = distribution warning. | **NEUTRAL-LEAN BULLISH — markup intact** | 4/5 |
| 🧬 Medallion | Confluence rebuilt: ~5 aligned factors (UPTREND regime, momentum +5, RSI recovery, SMA20 reclaim, trail discipline) vs 3 at 22:00. Deterministic trail, no tuned parameters — low overfit risk. Signal flip back within one session shows fragility, but current alignment is genuine. | **MODERATE SIGNAL (hold — trail governs)** | 3/5 |

**Expert Consensus: 3/3 → HOLD with trail $128.04. Trend recovered — strongest NVDU read since 22:00.**

### ZS — 📈 TRAILING, at 3M-high resistance → HOLD

**Setup**
- Entry $150.00 → Current **$214.74** | P&L **+43.2% (+$971.02, 15 sh)**
- Trail stop **$194.46** (2×ATR) locks in **≥ +$667 (+29.6%)** minimum
- 3M high $216.97 only **+1.06% ($2.23)** above price (supply zone)
- RSI 73.4 | Stoch 96.1 | Momentum STRONG (+3) | Regime UPTREND

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Hold R:R to 3M high vs trail = $2.23 vs $20.28 ≈ **0.11:1** — poor immediate reward at overbought extreme (Stoch 96.1). Trail guarantees +29.6% regardless: asymmetric hold with hard floor. Realizing into known supply remains the standing alternative. | **MARGINAL BET on hold** (confidence: moderate) | 3/5 |
| 📊 Wyckoff | Phase E markup driving into 3M-high supply. RSI 73.4 / Stoch 96.1 extended but no SOW bar, no confirmed distribution structure. Structure says trend intact; exiting into strength at known supply is valid if risk appetite drops. | **NEUTRAL — supply zone ahead, markup intact** | 3/5 |
| 🧬 Medallion | Factors: overbought Stoch + 3M-high resistance vs momentum +3 + UPTREND regime = 2v2 split. Deterministic trail resolves the tie. No fresh edge either way — riding a mature trend, not a new signal. | **WEAK SIGNAL (no fresh edge — trail governs)** | 2/5 |

**Expert Consensus: 3/3 → HOLD with trail $194.46. Alternative: realize +$971 into 3M-high resistance per standing TP call; trail guarantees ≥+$667 otherwise.**

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS SCAN** | **$0 deployed** |
| *(watch)* **GEV** | $974.48 on SMA50 reclaim | — | — | — | — | N/A — ⚠️ BOUNCE, not actionable | reserved |
| *(hold)* **NVDU** | $90.00 | trail **$128.04** | ✅ $99.84 | ✅ $109.68 | +56.8% actual | **HOLD ON TRAIL 3/3** (avg 3.7/5) | unrealized **+$1,381.32** |
| *(hold)* **ZS** | $150.00 | trail **$194.46** | ✅ $165.21 | ✅ $180.42 | +43.2% actual | **HOLD ON TRAIL 3/3** (avg 2.7/5) | unrealized **+$971.02** |

**Action today:** HOLD NVDU (trail $128.04, uptrend recovered, momentum +5) and ZS (trail $194.46, 1.06% from 3M high). No new entries. Optional: realize ZS +$971 into $216.97 resistance per the standing TP call. GEV: wait for reclaim >$974.48.

---

## Appendix — Raw Monitor Output

```
**📡 Entry Monitor — Fri 25 Sep 2026 03:00 ICT**

🚨 NVDU EXIT SIGNAL
Price: $141.16 | Entry: $90.00 | P&L: +56.8% ($+1381.32)
Regime: UPTREND | RSI: 43.9 | Stoch: 55.1 | ATR: $6.56
Momentum: STRONG (+5) | R: $6.56
SL: $128.04 (TRAILING 2×ATR) | TP1: $99.84 | TP2: $109.68 | TP3: ∞ (letting run)
• 📈 TRAILING @ $141.16 | Trail stop: $128.04 (2×ATR below price) | P&L: +56.8% — let profits run

🚨 ZS EXIT SIGNAL
Price: $214.74 | Entry: $150.00 | P&L: +43.2% ($+971.02)
Regime: UPTREND | RSI: 73.4 | Stoch: 96.1 | ATR: $10.14
Momentum: STRONG (+3) | R: $10.14
SL: $194.46 (TRAILING 2×ATR) | TP1: $165.21 | TP2: $180.42 | TP3: ∞ (letting run)
• 📈 TRAILING @ $214.74 | Trail stop: $194.46 (2×ATR below price) | P&L: +43.2% — let profits run
• 📏 Near 3M High $216.97 | P&L: +43.2% — resistance zone

📡 GEV Entry Monitor
Price: $954.99 (+0.33%) | RSI: 52.4 | Vol: 0.63x
SMA 20: $931.17 | SMA 50: $974.48 | SMA 100: $1006.14
5d: 0🔴/5🟢
• 📏 Testing SMA 50 support at $974.48 — stronger entry
• 🟢 4d green streak, RSI 52.4 — bounce confirmed

📍 VERDICT: ⚠️ BOUNCE | Risky | Wait for SMA50 reclaim (>$974.48) | Entry then: $974.48
```
