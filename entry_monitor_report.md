# 📡 Entry Monitor Report — Fri 25 Sep 2026 04:00 ICT

**Run:** `monitor_entries.py` exit 0. No 🟢 entry verdict (GEV = ⚠️ BOUNCE, not actionable). Exit/trailing signals fired on BOTH open positions → report triggered. (tvDatafeed connection timed out — fallback data used; prices may be slightly delayed.)

---

## Actionable Entry Signals

**NONE this scan.** No 🟢 entry confirmation — no entry pipeline run.

**GEV watch:** $955.04 (+0.34%), RSI 52.4, vol 0.74x (up from 0.63x), 5d 0🔴/5🟢 — still BELOW SMA50 ($974.48), testing it as resistance from underneath. Verdict ⚠️ BOUNCE / Risky. Entry only on reclaim **>$974.48**.

**Budget $2,500:** $0 deployed this scan — 100% reserved.

---

## Changes Since 03:00 Report

- **NVDU: +56.8% → +56.7%** — price $141.16 → **$141.06**, flat drift (-$0.10). Regime UPTREND, momentum **+5** held, RSI 43.9 → 43.8. Trail floor $128.04 → **$127.94** (locks ≥+$1,024, +42.2%).
- **ZS: +43.2% → +43.1%** — price $214.74 → **$214.64**, flat drift (-$0.10). Still ~**1.1%** below 3M high $216.97. Trail floor $194.46 → **$194.36** (locks ≥+$665, +29.6%). RSI 73.4 / Stoch 96.0 overbought.
- Combined open P&L: +$2,352.34 → **+$2,348.22** (-$4.12, noise).
- GEV volume ticking up 0.63x → 0.74x — still no reclaim.

**Net: no material change in the last hour. Both positions remain HOLD-ON-TRAIL.**

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|--------|--------|-----------|-----|-------|
| **NVDU** | 📈 TRAILING — hold | n/a (trail **$127.94**) | **+56.7% (+$1,378.62, 27 sh)** | Regime UPTREND, momentum +5, RSI 43.8 neutral. Trail 2×ATR locks ≥+$1,024 (+42.2%). Room to run |
| **ZS** | 📈 TRAILING — hold at resistance | n/a (trail **$194.36**) | **+43.1% (+$969.60, 15 sh)** | 3M high $216.97 ~1.1% above — supply zone. Trail locks ≥+$665 (+29.6%). RSI 73.4 / Stoch 96.0 overbought |

*Combined open P&L: **+$2,348.22** on $4,680 deployed (+50.2%). Worst case if BOTH trails hit: **≈+$1,690 (+36.1%)** locked.*

---

## Expert Analysis — Exit Decisions (Active Positions)

### NVDU — 📈 TRAILING → HOLD ON TRAIL

**Setup**
- Entry $90.00 → Current **$141.06** | P&L **+56.7% (+$1,378.62, 27 sh)**
- Trail stop **$127.94** (2×ATR) locks in **≥ +$1,024 (+42.2%)** minimum
- RSI 43.8 | Stoch 54.8 | Momentum **STRONG (+5)** | ATR $6.56 | Regime **UPTREND**

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Floor locks +42.2% with unbounded upside — positive-EV hold with a defined ruin point. No new money at risk; RSI neutral means not chasing an extended price. New-entry Kelly at $141 ≈ 0, but holding a winner on a free floor is +EV. | **BET on hold via trail** (confidence: moderate-high) | 4/5 |
| 📊 Wyckoff | Markup Phase E — higher highs/higher lows, no SOW bar, no upthrust, no distribution climax. Last shakeout direction is up. Break below $127.94 = first distribution warning. | **BULLISH — markup intact** | 4/5 |
| 🧬 Medallion | ~5 aligned factors (UPTREND, momentum +5, RSI neutral, trail discipline). Deterministic trail — no tuned parameters, so overfit risk ≈ 0. This is position management, not a fresh fitted signal. | **MODERATE SIGNAL (hold — trail governs)** | 3/5 |

**Expert Consensus: 3/3 → HOLD with trail $127.94.**

### ZS — 📈 TRAILING, at 3M-high resistance → HOLD

**Setup**
- Entry $150.00 → Current **$214.64** | P&L **+43.1% (+$969.60, 15 sh)**
- Trail stop **$194.36** (2×ATR) locks in **≥ +$665 (+29.6%)** minimum
- 3M high **$216.97** only ~**1.1%** above price (supply zone)
- RSI 73.4 | Stoch 96.0 | Momentum STRONG (+3) | Regime UPTREND

| Expert | Key Read | Verdict | Score |
|---|---|---|---|
| 🔢 Thorp | Reward to 3M high vs risk to trail ≈ $2.33 vs $20.28 ≈ **0.12:1** — poor incremental R:R at an overbought extreme (Stoch 96.0). Trail guarantees +29.6% regardless: asymmetric hold with hard floor. Realizing into known supply stays the standing alternative. | **MARGINAL BET on hold** (confidence: moderate) | 3/5 |
| 📊 Wyckoff | Phase E markup driving into 3M-high supply. If price **closes above $216.97 with volume** → breakout, markup continues. If it **fails and prints a SOW** → potential LPSY/upthrust → distribution; trail handles the exit. No confirmed distribution structure yet. | **NEUTRAL — supply zone ahead, markup intact** | 3/5 |
| 🧬 Medallion | Factors split 2v2: overbought Stoch + 3M-high resistance vs momentum +3 + UPTREND regime. Deterministic trail resolves the tie. Low overbought-long signal quality = exactly where fitted momentum entries fail after costs — but we're holding, not entering. | **WEAK SIGNAL (no fresh edge — trail governs)** | 2/5 |

**Expert Consensus: 3/3 → HOLD with trail $194.36. Alternative: realize +$970 into $216.97 resistance per the standing TP call; trail guarantees ≥+$665 otherwise.**

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS SCAN** | **$0 deployed** |
| *(watch)* **GEV** | $974.48 on SMA50 reclaim | — | — | — | — | N/A — ⚠️ BOUNCE, not actionable | reserved |
| *(hold)* **NVDU** | $90.00 | trail **$127.94** | ✅ $99.84 | ✅ $109.68 | +56.7% actual | **HOLD ON TRAIL 3/3** (avg 3.7/5) | unrealized **+$1,378.62** |
| *(hold)* **ZS** | $150.00 | trail **$194.36** | ✅ $165.21 | ✅ $180.42 | +43.1% actual | **HOLD ON TRAIL 3/3** (avg 2.7/5) | unrealized **+$969.60** |

**Action today:** HOLD NVDU (trail $127.94) and ZS (trail $194.36). No new entries — budget $2,500 unspent. Optional: realize ZS +$970 into $216.97 resistance per standing TP call. GEV: wait for reclaim **>$974.48**.

---

## Appendix — Raw Monitor Output

```
**📡 Entry Monitor — Fri 25 Sep 2026 04:00 ICT**

🚨 NVDU EXIT SIGNAL
Price: $141.06 | Entry: $90.00 | P&L: +56.7% ($+1378.62)
Regime: UPTREND | RSI: 43.8 | Stoch: 54.8 | ATR: $6.56
Momentum: STRONG (+5) | R: $6.56
SL: $127.94 (TRAILING 2×ATR) | TP1: $99.84 | TP2: $109.68 | TP3: ∞ (letting run)
• 📈 TRAILING @ $141.06 | Trail stop: $127.94 (2×ATR below price) | P&L: +56.7% — let profits run

🚨 ZS EXIT SIGNAL
Price: $214.64 | Entry: $150.00 | P&L: +43.1% ($+969.60)
Regime: UPTREND | RSI: 73.4 | Stoch: 96.0 | ATR: $10.14
Momentum: STRONG (+3) | R: $10.14
SL: $194.36 (TRAILING 2×ATR) | TP1: $165.21 | TP2: $180.42 | TP3: ∞ (letting run)
• 📈 TRAILING @ $214.64 | Trail stop: $194.36 (2×ATR below price) | P&L: +43.1% — let profits run
• 📏 Near 3M High $216.97 | P&L: +43.1% — resistance zone

📡 GEV Entry Monitor
Price: $955.04 (+0.34%) | RSI: 52.4 | Vol: 0.74x
SMA 20: $931.17 | SMA 50: $974.48 | SMA 100: $1006.14
5d: 0🔴/5🟢
• 📏 Testing SMA 50 support at $974.48 — stronger entry
• 🟢 4d green streak, RSI 52.4 — bounce confirmed

📍 VERDICT: ⚠️ BOUNCE | Risky | Wait for SMA50 reclaim (>$974.48) | Entry then: $974.48
```
