# 📡 Entry Monitor Report — Mon 05 Oct 2026 03:00 ICT

> **vs 02 Oct 22:00 ICT report:** ① **GEV closed Fri $988.70 — now *inside* the ±2% tolerance of the fib50 band the backtest actually tests** (−1.6% under $1,004.62), so the signal technically fires at this close; **Medallion composite +0.5 → +1.5** (vol 0.36x→1.02x, RSI 57.8 neutral). ② Thorp re-run **identical: n=833, WR 51.9%, +0.116R, t=2.86 (<3.0)**, and **2026 still negative (pooled PF 0.94, GEV PF 0.74)** — decay flag intact. ③ **NVDU 3rd consecutive exit alert, ZS 7th** — both printed "SL" floors are *entry-anchored* ($99.31 / $163.88), i.e. **35% and 17% below market = no real protection**. ④ Data: tvDatafeed timed out again → Yahoo fallback, last bar **Fri 02 Oct** (market shut until Mon 16:00 ICT).

## Actionable Entry Signals

### GEV — 🟢 UPTREND (fib-dip verdict · price inside band tolerance · gate not fired)

**Setup:** Regime UPTREND, **$988.70 (+0.13%)** = **+4.7% over SMA20 $944.66, +2.5% over SMA50 $965.04, −1.1% under SMA100 $999.52**. Retrace of the $868.25 → $1,140.99 leg = **55.8%** (deep). Short-term **stoch 86.8 / simple-14d RSI 87.0 = exhausted** vs **Wilder RSI 57.8 = neutral** — conflicting reads, which is why the monitor still prints 🟢 while warning "do not chase".

| Level | Value |
|---|---|
| Entry (only on trigger) | **$1,004.62 – $1,036.80** (fib50 → fib38.2) |
| Gate | **close > $1,004.62 on >1.2× volume + SOS bar**, buy-stop above that bar's high |
| Stop | **$940.01** (monitor) · **$935.50** (expert: fib618 $972.44 − ATR $36.94) — backed by HVN **$930–943** ✅ |
| TP1 | **$1,072.60** (3m VPOC / VAH = first HVN) |
| TP2 | **$1,140.99** (3m high / monitor TP) |
| R:R | **2.86:1 at market** (BE WR 25.9%) · **1.97:1 band bottom** (33.6%) · **1.03:1 band top** (49.3%) — band top is a coin flip |

⚠️ The entry band sits under an **overhead HVN wall $1,005 / $1,018 / $1,030 / $1,043 / $1,056** — supply has to be chewed through, which is exactly why an SOS-on-volume gate, not a market buy, is the rule.

### Expert Panel — GEV

| Expert | Verdict | Score / Key numbers |
|---|---|---|
| 🔢 **Thorp Edge** | ❌ **NO BET** at full size — paper-only, medium confidence | Scorecard **21/40** (paper band). Exact signal re-run (5y, 9 tickers, net 10bp RT): **n=833, WR 51.9%, exp +0.116R, PF 1.24, t=2.86 (< 3.0 bar), Kelly 9.9%, maxConsecLoss 24**. GEV-only: **n=31, WR 64.5%, +0.307R, PF 1.86, t=1.65, Kelly 29.8%**. **Decay: 2026 pooled PF 0.94 (exp −0.031R) · GEV 2026 PF 0.74 (exp −0.143R) · GEV H1 PF 3.22 → H2 PF 1.08 · 2022 PF 0.46.** H2 pooled does carry t=3.71 / PF 1.47. Portfolio sim: **24.9% CAGR vs SPY 14.1% same 4.57y window — but maxDD 53.6%** |
| 📊 **Wyckoff 2.0** | ⚠️ **NEUTRAL** — accumulation forming, Phase D NOT started | HH/HL off the Sep 14 shock low $868 (10d H/L 1,006/921.53 vs prior 983.34/868.25); pivots H983 → L868 → H971 → L922 → new HH = markup. Price **−1.1% under SMA100, −7.8% under 3m VPOC $1,072.60**, inside 1y value area. Footprint mixed: 30d up/down volume **1.59** ✅, 3 distribution days/25 ✅, MFI 59.8 — but **CMF20 −0.071, OBV 60d slope −26k/day falling ✗, vol 1.02× = no initiative volume ✗**. Stop is HVN-protected ($930–943); needs an **SOS close > $1,004.62 on volume** to begin Phase D |
| 🧬 **Medallion** | ⚠️ **WEAK SIGNAL** — composite **+1.5 / ±10** (up from +0.5) | ✓ regime uptrend +1 · ✓ inside fib band +1 · ✓ +71% over 1y VPOC +1 · ✓ RSI 57.8 +0.5 · ✓ 5d 2R/3G +0.5 · ✗ SMA stack bearish (945 < 965) −1 · ✗ below SMA100 −1 · ✗ 56% deep retrace −0.5 · ○ vol 1.02× · ○ in value area. **t=2.86 < 3.0 bar**, GEV t=1.65 (n=31). Cross-market spread **ZS PF 2.69 / RDDT 2.27 / GEV 1.86 vs FBK 0.91 / GDDY 0.69 / MRVL 0.50** → non-uniform = data-mining risk. 2026 expectancy negative pooled **and** GEV = live decay |

**Expert Consensus: ⏳ WAIT — NO ENTRY (0 of 3 green).** This is the closest GEV has been (inside the tested band, composite +1.5, stop HVN-backed), but the same three gates hold: **SOS close > $1,004.62 on >1.2× volume**, Thorp capped at paper-only (21/40, t=2.86), Wyckoff Phase D unconfirmed (OBV falling, below SMA100 and 3m VPOC). **2026 says this exact signal loses money (pooled PF 0.94 / GEV PF 0.74) — Thorp kill rule #1 applies to live size.**

**Budget $2,500: $0 deployed.** Post-trigger at band bottom $1,004.62 with expert stop $935.50: 1% risk = $25 ÷ 6.9% ≈ **$363 notional ≈ 0.36 sh** (fractional required — 1 whole share risks $69 = 2.8% of budget, violates the 1% rule).

---

## Exit Signals (Active Positions)

| Ticker | Action | Price | Entry | P&L | Stop: monitor floor → **recommended** | Notes |
|---|---|---|---|---|---|---|
| **NVDU** | 🎯 **TRIM ⅓ + RAISE TRAIL** (3rd consecutive exit alert) | $152.61 | $90.00 | **+69.6% ($+1,690.47)** | $99.31 (1.5R lock, **35% below market**) → **$138.36** (2×ATR, just under SMA20 $140.43) | TP2 $108.63 (3.0R) delivered long ago; price **+41% past TP2**, 3.1% under 3M high **$157.50**; monitor simple-RSI **82.5** + Stoch 84.5 exhaustion (Wilder RSI 62.6); momentum **STRONG (+3)**; ATR $6.21 monitor / $7.12 Yahoo |
| **ZS** | 🎯 **EXIT FULL** *(7th consecutive alert)* | $196.60 | $150.00 | **+31.1% ($+699.00)** | $163.88 (1.5R lock, 17% below) → minimum **$177.75** (2×ATR) | TP2 $173.12 (2.5R) hit Sep 30, price **13.6% past target**; **MACD bearish hist −0.96**; momentum NEUTRAL (+2), stoch 31 cooling; 9.4% under 3M high $216.97 |

Combined open P&L: **+$2,389.47**. Neither exit has been executed yet — the monitor's printed "SL" lines are entry-anchored floors, **not** trailing stops.

### 3-Expert Read (exits)

- **🔢 Thorp:** system expectancy is only **+0.116R/trade** — giving a +69.6% winner back toward a stop floor 35% below market is exactly where winners become losers → realize ⅓, trail the rest. ZS at 7 alerts past a hit 2.5R target with negative MACD = **negative-EV hold** → exit. **Both actions correct.**
- **📊 Wyckoff 2.0:** NVDU sitting just under the 3M high = upthrust/distribution test, RSI/Stoch exhausted but **no SOW bar yet** → **trim, not full exit; markup intact above $138–140**. ZS stalled with MACD rolling over = **SOW forming → distribute into strength**.
- **🧬 Medallion:** NVDU confluence still STRONG (+3) but stoch 84.5 + simple-RSI 82.5 = **weakening; hold-case only for a reduced runner**. ZS +2 with negative MACD = **WEAK SIGNAL**, no statistical reason to keep full size.

**Expert Consensus: NVDU → sell 9 sh now (~$1,373), trail 18 sh under $138.36 · ZS → EXIT full (7th alert, no longer waitable).**

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **GEV** | $1,004.62–$1,036.80 **only after SOS close > $1,004.62 on >1.2× vol** | $940.01 (monitor) / $935.50 (expert) | $1,072.60 | $1,140.99 | 1.97:1 band bottom · 1.03:1 band top · 2.86:1 market | ⏳ **WAIT** (Thorp NO BET 21/40 · Wyckoff NEUTRAL · Medallion WEAK +1.5) | **$0 — not deployed** |
| GDDY | — | — | — | — | — | 🟡 PULLBACK — testing SMA20 $97.93, not actionable | $0 |
| MKSI | $275.90 cooldown (SMA50/VWAP) | $260.78 | $286.54 | $304.48 | — | 🔴 WAIT — overbought RSI 78.0 / Stoch 90.3, do NOT chase | $0 |
| **ZS** | held @ $150.00 | exit now (min trail $177.75) | ✓ $163.88 | ✓ $173.12 | TP2 hit, +31.1% open | **EXIT — take profit (7th alert)** | Frees ~$2,949 |
| **NVDU** | held @ $90.00 | trail **$138.36** | ✓ $99.31 | ✓ $108.63 | runner, +69.6% | **TRIM ⅓ + raise trail** | 27 → 18 sh, ~$1,373 back |

GOOG, RDDT, BCC, FBK, AMZN, MRVL: no signal this run.

**Action:** No new capital deployed. **Close ZS** (7th scan this exit has been live). **Trim NVDU — sell 9 sh at market, trail 18 sh under $138.36** (the $99.31 floor the monitor prints is not a real stop). GEV gate unchanged: one close above **$1,004.62** on volume triggers the paper entry — until then it stays a WAIT.
**Capital release if both executed:** ZS ≈ $2,949 + NVDU trim ≈ $1,373 ≈ **$4,322** for the next qualified entry.

---
*Backtest: `_gev_experts.py` → `_gev_expert_out.txt` re-run 03:00 ICT (last bar Fri 2026-10-02, Yahoo close $988.70; 5y max / GEV 2.5y, 9 monitor tickers + SPY, net 10bp RT; signal replicated exactly as the monitor emits it: UPTREND + fib38.2–50% ±2% band, stop = fib618 − ATR, TP = 3m high). RSI cross-check: monitor's "RSI 87.0" = simple 14-day average (verified exact), Wilder RSI14 = 57.8 — methodology conflict noted, not a data error. Monitor prices 03:00 ICT: GEV $988.70 · NVDU $152.61 · ZS $196.60 · GDDY $97.21 · MKSI $279.15. tvDatafeed timed out → Yahoo fallback.*
