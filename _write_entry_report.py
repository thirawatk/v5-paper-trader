#!/usr/bin/env python3
REPORT = r'''# 📡 Entry Monitor Report — Wed 07 Oct 2026 03:00 ICT

Run: `monitor_entries.py` at 03:00 ICT = 16:00 ET Oct 6 — **full-session close data** (22:00 run was mid-session). Changes vs 22:00: **GEV's band test bar PRINTED** (green close inside the dip band on 1.19x volume after holding a $995 dip) → moved to 🟢 Entry Triggered; **GOOG still below its band** (flat doji, 0.61x vol, SMA100 still overhead); **AMZN closed $1.14 under the SMA50 gate** on 0.83x vol. All three expert backtests re-run on the completed Oct-6 bar: `_goog_experts.py`, `_amzn_experts.py`, `_gev_experts.py`.

## 🟢 Entry Triggered

### GEV — test bar printed inside the band, but the panel says NO BET (sizing + the $1,052.78 gate)

- **Setup:** $1,029.34 (+3.97%) · O 1,001.35 / H 1,052.78 / L 995.05 / C 1,029.34 · vol 1.19x 20d · 5d 1🔴/4🟢. Opened below the band, dipped to **$995.05** (held well above the $939 stop shelf), rallied to tag **$1,052.78 = the prior 10d/30d high exactly**, then faded to close mid-band (59% of range). RSI 86.1 on the monitor tape / RSI14 65.0 on the daily calc.
- **Entry:** $1,029.34 at market, or band retest $1,004.62–$1,036.80
- **Stop:** $939.24 (monitor; fib618−ATR $934.60) · structure stop = below test low $995.05
- **TP1:** — · **TP2:** $1,140.99 (3m high)
- **R:R:** **1.18:1 at market** · 1.02:1 band top · 1.95:1 band bottom (breakeven WR 45.9% at market)
- **Trigger: PRINTED** — evidence: green +3.97% close $1,029.34 **inside** the $1,004.62–$1,036.80 dip band, volume **1.19x (>1x)**, after the intraday test to $995.05 was bought back.

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — 19/40** (unchanged vs 22:00) | GEV-only fib-dip signal: **n=33, WR 66.7%, +0.333R, PF 1.99, t=1.89** — below the 3.0 bar, Kelly 33.2%. **2026 GEV negative** (n=15, PF 0.94, −0.026R); H2 decayed hard (PF 1.18 vs H1 3.41). Pooled signal n=836, t=3.03 ✓ — but cross-market is NOT uniform (ZS 2.69 / RDDT 2.27 vs MRVL 0.51 / GDDY 0.69 / FBK 0.91) → data-mining risk. At market R:R 1.18 ≈ coin flip. **Not sizeable:** 1 sh with monitor stop = $90.10 risk = **3.6% of $2,500** (cap 1%) ✗; even the structure stop ($995.05) = 1.4% ✗; only a band-bottom stop ($24.72 = 0.99%) squeaks in |
| 📊 Wyckoff 2.0 | **ACCUMULATION CONFIRMED (Phase E) — but the gate rejected price** | OBV 60d **rising +50.8k/day**, 30d up/down vol **2.07**, HH/HL (10d 921→1052 / 868), only 2 distribution days/25, price +8.4/+6.6/+3.1% over SMA20/50/100. Today was the textbook test: dip below the band bought back, close in band on 1.19x vol. **BUT H=$1,052.78 tagged to the tick and faded $23 → rejection at the breakout gate (Upthrust risk).** Primary: close **> $1,052.78** on >1x vol → wait for retest. Alternative: band-bottom retest $1,004.62. Failure < $998.38 (SMA100) kills the setup. 3m VPOC $985.88 supports below; 3m VAH $1,072.60 overhead |
| 🧬 Medallion | **STRONG SIGNAL of the three — but underpowered** | Composite **+5.0/10** (was +3.5 at 22:00): ✓ regime, ✓ inside band, ✓ above SMA100, ✓ above 1y VPOC (+78%), ✓ shallow 41% retrace, ✓ vol now 1.06–1.19x. ✗ SMA stack lagging (20<50<100), ✗ gate rejection. **GEV t=1.89 < 3.0 bar** and 2026 PF 0.94 → positive confluence, not statistically deployable |

- **Expert consensus: NO BET even with the trigger printed.** The trigger is real, but (1) the position cannot be sized inside the 1% risk cap, and (2) price just failed the $1,052.78 gate on the same bar. The trade worth taking is the **retest after a close >$1,052.78**, or the **band-bottom $1,004.62** with a structural stop — not market, not band top.
- **Budget $2,500:** **$0 deployed** (1 sh at market with a valid stop = 3.6% risk > cap).

---

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG — inside neither the band nor the SMA100; two-move scenario unchanged

- **Setup:** $344.64 (+0.24%) · bar O 344.64 / H 345.66 / L 341.70 / C 344.59 — flat doji (body −0.01%, closed 73% up the range), vol 0.61x, 5d 1🔴/4🟢. Above SMA20 $340.16 / SMA50 $342.63 but **2.0% BELOW SMA100 $351.77** — the monitor's "testing SMA100 support" line is stale: SMA100 is overhead supply, not support. 44.8% retrace of the $325.63→$359.98 leg.
- **Trigger needed (NOT printed):** price must first rally **into $348.35–$356.25**, then print an SOS bar (wide-range green, upper-third close) on **>1.0x volume** → buy-stop above its high. Currently below the band, vol 0.61x, no SOS.
- **Planned levels:** Entry band $348.35–$356.25 · Stop $331.73 · TP $381.81 (3m high ≈ 1y VAH $380.76) · R:R **1.06:1 band top → 2.07:1 band bottom** (at market 2.93:1, but there is no signal at market).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now — 24/40** (paper-only band); on print → small size only | Pooled fib-dip signal 5y/9 tickers net 10bp: **n=836, WR 52.2%, +0.122R, PF 1.25, t=3.03** (clears the 3.0 bar), Kelly 10.5%, maxConsecLoss 24. GOOG-only: n=95, WR 54.7%, +0.171R, PF 1.40, t=1.47, Kelly 15.7%. **2026 GOOG negative** (n=17, WR 35.3%, PF 0.74, −0.119R). Portfolio sim **26.4% CAGR vs SPY ≈14.4%/yr** same window — beats the index — but **maxDD 53.6%** blows the 25% cap |
| 📊 Wyckoff 2.0 | **NEUTRAL** — markup intact, no trigger | Above 1y VPOC $332.26 (+3.7%), inside value area. But OBV 60d **falling (−213k/day)**, CMF20 −0.048, 4 distribution days/25, LH/HL mixed, −2.0% under SMA100, vol 0.61x = **no SOS on this pullback**. Profile: HVN $339–345 supports below; **LVN $348 (68M) = band bottom is thin** (price can slice it); $355 HVN (206M) = first resistance |
| 🧬 Medallion | **WEAK SIGNAL** | Composite **+2.0/10** (✓ regime, ✓ near band, ✓ above VPOC, RSI 53.6 neutral; ✗ SMA stack 20<50, ✗ vol 0.61x, ✗ no momentum burst). Pooled t=3.03 ✓ but GOOG t=1.47 ✗. Cross-market NOT uniform → data-mining risk; GOOG 2026 negative = decay in progress |

- **Expert consensus: WAIT — no entry.** Green label, but price is outside the band, SMA100 is lost overhead, and no SOS printed.
- **Budget $2,500:** $0 now. On print at band bottom $348.12: 1% risk = $25 → **1 share** ($16.4 = 0.66%) ✓ — 2 shares = 1.3% ✗.

### AMZN — closed $1.14 under the SMA50 gate; strong close, no volume

- **Setup:** $256.27 (+1.94%) · bar O 253.40 / H 256.67 / L 251.08 / C 256.29, closed on the highs (93% of range), vol 0.83x 20d (monitor 0.69x), 5d 2🔴/3🟢. Above SMA20 $251.25 (per-plan partial confirmation ✓) and SMA100 $252.94, but **below SMA50 $257.43 by $1.14 → reclaim NOT printed**.
- **Trigger needed (NOT printed):** daily close **> $257.43 (SMA50) on >1.0x volume**.
- **Planned levels:** Entry $257.43 · Stop $246.33 (prior swing low / 2×ATR cap) · risk $11.10/sh (4.3%) · TP1 $267.56 (30d high, **0.91R**) · TP2 $280.72 (2.10R).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — 19/40** (below 20 = don't trade), even if the trigger prints | Exact SMA50-reclaim trigger backtested 5y/9 tickers: **Variant B (+vol>1x): n=85, WR 37.6%, +0.070R, PF 1.10, t=0.42**, Kelly 3.5%. Variant A (no vol): n=185, −0.025R, PF 0.96, t=−0.23. AMZN-only B: n=14, +0.422R/PF 1.74 but t=0.97, **2026 0/3 (PF 0.00)**, recent half PF 0.77. Portfolio B: **+6.8% total (1.5% CAGR) over 4.5y vs SPY +86.2%** → fails the ultimate question decisively |
| 📊 Wyckoff 2.0 | **ACCUMULATION — NOT CONFIRMED** (range context) | 49% of the 60d range $226.16–$287.20 = balance, not trend. Green close on the session highs, but still **under SMA50 supply**. OBV 60d falling (−7.6M/day), 30d up/down vol 0.80, CMF20 −0.009, vol 0.83x → **no initiative buying**. Needs a real SOS close >$257.43 >1x vol, then a Back-Up. Alternative: loss of $244.73 (10d low) → failed accumulation → range short side |
| 🧬 Medallion | **NOISE** | Composite **+1.0/10** (✓ above SMA100, ✓ above VPOC, RSI neutral, green close; ✗ below SMA50, ✗ stack 20<50, ✗ vol 0.83x, mid-range 49% = balance). t=0.42 ≪ 3.0 bar; cross-time H1 43% vs H2 33% deteriorating. Single-name textbook pattern = highest overfit risk |

- **Expert consensus: WAIT — trigger not printed, and the trigger itself has no demonstrated edge.**
- **Budget $2,500:** risk-compliant size = 2 shares ($512.58 notional, $22.2 = 0.9% risk) ✓ — but verdict NO BET → **$0 deployed**.

---

## Not Routed This Run

- **MKSI $281.35** — 🔴 WAIT overbought (RSI 87.3 / Stoch 89.5), cooldown entry $274.24 (SMA50). Routine.
- **RDDT, GDDY, BCC, FBK, MRVL** — no signals this run.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **NVDU** (13 sh runner) | **HOLD + TRAIL** | $159.54 | **+77.3%** ($+904.02 open) | Monitor TP2 printed long ago (entry-based levels stale — ignore $99.83/$109.65). **14 sh already trimmed @ $163.20 Oct 6 → +$1,024.80 realized.** Today's bar: opened 163.20, **tagged the 3M high $164.90 to the tick, closed at the lows (6% of range, body −2.2%)** = first SOW-style fade. RSI 83.9, momentum STRONG (+3). **Keep trail $153.74 (1.5×ATR) — never lower it.** Runner only |
| **ZS** (15 sh) | **TRIM 1/3–1/2 + TRAIL** | $212.25 | **+41.5%** ($+933.30) | TP2 ($174.03) exceeded by 21%. +5.18% on **1.52x volume** into the 3M high **$216.97** resistance, **MACD hist −0.25 bearish**, momentum NEUTRAL (+1). Realize 5–8 sh now (~$311–$498); **ratchet trail $192.31 → $193.03** (2×ATR $9.61) on the rest |

Combined open P&L: **+$1,837.32** (NVDU runner + ZS) · realized Oct 6 NVDU trim: **+$1,024.80**.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| **GEV** | $1,029.34 mkt / band $1,004.62–$1,036.80 on retest | $939.24 (structure $995.05) | — | $1,140.99 | 1.18 (mkt) / 1.02–1.95 | **PRINTED** — green +3.97% close inside band, vol 1.19x, $995 test bought back; but $1,052.78 gate rejected | **NO BET** — Thorp 19/40 (t=1.89<3, 2026 PF 0.94, 1 sh = 3.6% risk > cap) · Wyckoff ACCUMULATION CONFIRMED but gate rejected · Medallion STRONGEST +5.0 yet underpowered | **$0** — take only the >$1,052.78 retest or band-bottom entry |
| **GOOG** | $348.35–$356.25 **after SOS bar >1x vol** | $331.73 | — | $381.81 | 1.06 – 2.07 | **NOT PRINTED** — price $344.64 below band, vol 0.61x, SMA100 lost overhead | **WAIT** — Thorp NO BET (24/40; pooled t=3.03 ✓ but 2026 PF 0.74, maxDD 53.6%) · Wyckoff NEUTRAL · Medallion WEAK +2.0 | $0 now; on print 1 sh = $16.4 risk (0.66%) ✓ |
| **AMZN** | $257.43 (SMA50 reclaim, >1x vol) | $246.33 | $267.56 | $280.72 | 0.91 / 2.10 | **NOT PRINTED** — close $256.29 < $257.43, vol 0.83x | **WAIT** — Thorp NO BET (19/40, trigger t=0.42, 1.5% CAGR vs SPY 86.2%) · Wyckoff accum. unconfirmed · Medallion NOISE +1.0 | $0 (2 sh = 0.9% risk ✓, but NO BET) |

**Entries triggered: 1 (GEV — panel rejects on sizing + gate) · Conditional: 2 (GOOG, AMZN) · Exits to act on: ZS trim + trail, NVDU trail only. New capital deployed: $0.**

---
*Entry Monitor 3-Expert Pipeline · monitor_entries.py + Thorp / Wyckoff 2.0 / Medallion · backtests refreshed on completed Oct-6 bar: `_goog_experts.py` → `_goog_expert_out.txt`, `_amzn_experts.py` → `_amzn_expert_out.txt`, `_gev_experts.py` → `_gev_expert_out.txt` (5y, 9 monitor tickers, net 10bp RT) · bar probe `_probe_ohlc.py` · 07 Oct 2026 03:00 ICT*
'''
with open('/root/.hermes/profiles/trader/scripts/entry_monitor_report.md', 'w') as f:
    f.write(REPORT)
print('WROTE', len(REPORT), 'chars')
