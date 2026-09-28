# 📡 Entry Monitor Report — Mon 28 Sep 2026 21:01 ICT

**Run:** `monitor_entries.py` exit 0, 21:01 ICT (US cash session live, open 20:30 ICT).
**Triggers:** no 🟢 entry verdict (GDDY = 🔴, GEV = ⚠️) → **trailing signals fired on BOTH open positions** → report.
**Data:** tvDatafeed connection timed out ×2 → fallback quote source used. Prices now moving with the live session.

---

## Actionable Entry Signals

**NONE this scan.** No 🟢 verdict → 3-expert entry pipeline not run.

- **GDDY** $94.96 (−2.24%), RSI 52.3, vol 0.06x, 5d 4🔴/1🟢 — verdict **🔴 WAIT / DOWNTREND**, price below SMA50 $96.30, structurally broken. Not an entry.
- **GEV** $952.14 (−0.57%), RSI 46.2, vol 0.07x, 5d 1🔴/4🟢 — verdict **⚠️ BOUNCE (risky)**, still **$18.65 (1.9%) below** the SMA50 $970.79 reclaim level. Trigger only on reclaim >$970.79 **with volume** (0.07x is dead).

**Budget $2,500: $0 deployed this scan — 100% reserved.**

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|--------|--------|-----------|-----|-------|
| **NVDU** | 📈 TRAILING — hold | n/a (trail **$137.95**) | **+67.0% (+$1,628.91, 27 sh)** | UPTREND, momentum +4, RSI 55.8, Stoch 95.4 (overbought), ATR $6.19. Floor locks ≥+$1,294.65 (+53.3%). TP1 ✅ TP2 ✅, TP3 ∞ |
| **ZS** | 📈 TRAILING — hold | n/a (trail **$177.31**) | **+32.8% (+$737.55, 15 sh)** | UPTREND, momentum +5, RSI 70.5 (hot), ATR $10.93. Floor locks ≥+$409.65 (+18.2%). −8.2% off $216.97 high |

*Combined open P&L: **+$2,366.46** on $4,680 deployed (+50.6%). Worst case if BOTH trails hit: **≈+$1,704.30 (+36.4%)** locked.*

**vs 20:01 ICT run:** NVDU flat ($150.33), ZS rebounded $196 → $199.17, P&L +28.7% → +32.8%. Trails recompute with price; no exit triggered. Prior 3-expert HOLD verdicts carry over (NVDU 3/3 HOLD avg 3.7/5, ZS 3/3 HOLD avg 2.3/5).

---

## ⚠️ Risk Note — trail is not a ratchet (still awaiting your OK)

`monitor_entries.py` computes `trail = price − 2×ATR` fresh every run with **no persisted high-water mark**. The 2×ATR gap itself is exact (verified: NVDU 150.33−137.95 = 12.38 = 2×6.19; ZS 199.17−177.31 = 21.86 = 2×10.93) — but the floor still *falls* when price falls.

| | True ratchet | Actual (21:01) |
|---|---|---|
| ZS floor | $194.36 (Fri 04:00 level) | **$177.31** (−$17.05 cumulative) |
| Locked profit | +$665.40 (at $194.36 floor) | **+$409.65** (−$255.75 given back) |

**Recommended fix:** persist `entry_monitor_trail.json` and use `trail = max(prev_trail, price − 2×ATR)`. **Not applied** — exit-logic/risk change, waits for your confirmation.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS SCAN** | **$0 deployed** |

**Positions:** NVDU trail $137.95 / ZS trail $177.31 — both TRAILING, hold.
