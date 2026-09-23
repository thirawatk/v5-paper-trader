# 📡 Entry Monitor Report — Wed 23 Sep 2026 21:01 ICT

**Run:** `monitor_entries.py` exit 0 (TV feed timed out → fallback data). No 🟢 entry verdicts anywhere. Exit/trailing signals fired on BOTH open positions → report triggered. Material change vs 20:01 ICT report: **GOOG armed setup broke down** — $347.41 → ~$339.5, now sitting 0.6% above its invalidation line.

---

## Actionable Entry Signals

**NONE this cycle.**

| Ticker | Verdict | Why excluded |
|---|---|---|
| GDDY | 🔴 WAIT | Downtrend, −5.09%, below SMA50 — structurally broken |
| BCC | ⚠️ BOUNCE | 📏 testing SMA50 $79.23 support; needs reclaim >$79.23 |
| GEV | ⚠️ BOUNCE | 📏 testing SMA50 $976.46; 4d green but below it |
| RDDT / FBK / AMZN | 🔴 WAIT (silent) | Downtrends, RSI 41.4 / 24.7 / 44.9 — no trigger |
| MRVL | 🟢 UPTREND (silent) | "Entry on dip $247.63–$231.45" but price $261.68 — dip hasn't come; monitor raised no alert |

### ⚠️ Status Change — GOOG (was conditional-entry at 20:01)

The armed buy-stop ($348.35–$356.25) **never triggered — price broke the other way.** $347.41 → **$339.53** (intraday low $338.04), now BELOW SMA50 $342.97, vs prior close $347.41 (−2.3%). Invalidation = daily close < **$337.45** — price is 0.6% above it, market still open.

| Expert | Verdict | Score | Evidence |
|---|---|---|---|
| 🔢 **Thorp Edge** | **NO BET** | **15/40** | Setup's trigger-side never filled; entry now = catching a falling knife 0.6% above invalidation. Prior event studies on this trigger class were t = −3.25 to −8.10 (negative edge). Kelly at this price ≈ 0. Don't trade. Buy the index. |
| 📊 **Wyckoff 2.0** | **ACCUMULATION AT RISK → NEUTRAL** | **2/5** | Back-Up failed to hold the broken Creek band ($346–348): price sliced through instead of retesting. Close < $337.45 = failed accumulation retest → rotates to distribution. Until close prints: no scenario qualifies for a 1-move/2-move entry. |
| 🧬 **Medallion** | **NOISE** | **1/5** | Signal died: no SOS bar, price broke down through trigger level, regime flipped to BOUNCE/monitor-only. Zero out-of-sample confirmations. |
| **Consensus** | **DISARM — stand down. Re-arm only on close >$346.50 SOS; kill permanently on close <$337.45** | **0/3 BET** | |

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **NVDU** | 📈 TRAILING — hold, no exit hit | $145.38 | **+61.5% (+$1,495.26)** | Trail $132.64 = 2×ATR $6.37 below price (verified). Regime UPTREND, RSI 52.5 neutral, momentum STRONG +6, 9.4% above trail, −6.3% off 3M high $154.98. **Let profits run** |
| **ZS** | 📈 TRAILING — hold, no exit hit | $212.92 | **+41.9% (+$943.80)** | Trail $192.58 = 2×ATR $10.17 (verified). UPTREND, RSI 74.5, **Stoch 95.9 + fresh 3M high $215.20 printed today** — overbought at resistance. Closest to a SOW/UT print; trail does the exit, don't add |

**Expert read (hold-vs-exit):**

| Expert | NVDU | ZS |
|---|---|---|
| 🔢 Thorp | **HOLD** — trail caps give-back at 8.8% while trend edge persists; exiting now spends the edge you paid for | **HOLD, no add** — buying new size at stoch 95.9 into 3M-high resistance = negative expectancy |
| 📊 Wyckoff | **Markup (Phase E)** — HH/HL intact, no SOW bar | **Late markup at Ice** — a wide-range SOW bar closing lower third on volume = partial-exit trigger |
| 🧬 Medallion | Momentum factor +6 confirms hold; single-factor, trail manages it | Near-3M-high + stoch >95 = mean-reversion candidate, WEAK alone — insufficient vs trend |
| **Consensus** | **HOLD @ trail $132.64** | **HOLD @ trail $192.58 — act on SOW bar** |

*Combined open P&L: **+$2,439.06** on $4,680 deployed (+52.1%).*

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **— none —** | — | — | — | — | — | **NO ACTIONABLE ENTRY THIS CYCLE (0/3 BET everywhere)** | **$0 deployed** |
| *(watch)* GOOG | stand down; re-arm >$346.50 SOS | kill < $337.45 close | — | — | — | ⚠️ DISARM — 0/3 BET | idle |
| *(watch)* BCC | $79.23 on SMA50 reclaim | — | — | — | — | not actionable (⚠️) | idle |
| *(watch)* GEV | $976.46 on SMA50 reclaim | — | — | — | — | not actionable (⚠️) | idle |
| *(hold)* NVDU | trail $132.64 | | | | | HOLD (trailing) | unrealized **+$1,495.26** |
| *(hold)* ZS | trail $192.58 | | | | | HOLD (trailing, watch SOW) | unrealized **+$943.80** |

*Data notes: TV feed timed out (nologin + connection timeout) → monitor fell back to alternate source; GOOG $339.53 (monitor) vs Yahoo $338.14 live — within intraday noise of the same bar. NVDU/ZS trail levels independently recomputed and match monitor exactly.*
