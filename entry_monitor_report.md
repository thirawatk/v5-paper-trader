# 📡 Entry Monitor Report — Tue 06 Oct 2026 22:00 ICT

Run: `monitor_entries.py` (22:00 ICT, US session live — partial-session volume bars). Change vs 21:05 run: **GOOG verdict flipped to 🟢 UPTREND (now routed)**, **GEV pulled back INTO its dip band**, AMZN still below SMA50. Expert backtests refreshed on Oct-6 data: `_goog_experts.py`, `_gev_experts.py`, new `_amzn_experts.py` (5y, 9 monitor tickers, net 10bp RT costs).

## 🟢 Entry Triggered

**None — no confirmation triggers printed this run.**

---

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG — verdict flipped 🟢, but price is BELOW the entry band (two-move scenario)

- **Setup:** $344.32 (+0.14%), RSI 54.4, vol 0.22x, 5d 1🔴/4🟢. Above SMA20 $340.14 / SMA50 $342.62, but **2.0% BELOW SMA100 $351.76** — the monitor's "testing SMA100 support" line is stale, price already lost it and SMA100 is now overhead. 45% retrace of the 30d leg $325.63→$359.98; 55% of the 3m range.
- **Trigger needed (NOT printed):** price must first rally **into $348.35–$356.25**, then print an SOS bar (wide-range green, close upper third) on **>1.0x volume** → buy-stop above its high. Current vol 0.22x, no SOS bar.
- **Planned levels:** Entry zone $348.35–$356.25 · Stop $331.73 · TP $381.81 (3m high ≈ 1y VAH $380.76) · R:R **1.06:1 band top → 2.07:1 band bottom** (script economics, monitor stop/TP ≈ identical).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** — **24/40** (paper-only band); on print → small size only | Fib-dip signal backtested 5y/9 tickers net 10bp: **n=836, WR 52.2%, +0.122R, PF 1.25, t=3.02** (first run clearing the 3.0 bar; was 2.91 Sep-30), Kelly 10.5%, maxConsecLoss 24. GOOG-only: n=95, WR 54.7%, +0.169R, PF 1.40, t=1.46, Kelly 15.5%. **2026 GOOG negative** (n=17, PF 0.73, −0.125R); pooled 2026 flat (PF 1.01). Portfolio sim **26.4% CAGR vs SPY 14.4%** same window — beats the index — but **maxDD 53.6%** (over the 25% cap) |
| 📊 Wyckoff 2.0 | **NEUTRAL** — markup intact, no trigger | Above 1y VPOC $332.26 (+3.6%), inside value area. But OBV 60d **falling** (−224k/day), CMF20 −0.057, 4 distribution days/25, structure LH/HL mixed, −2.0% under SMA100, vol 0.22x = **no SOS on this pullback**. Profile: HVN $339–345 (172–262M) supports below; **LVN $348 (68M) = band bottom is thin**, price can slice it; $355 HVN (206M) = first resistance |
| 🧬 Medallion | **WEAK SIGNAL** | Composite **+2.0/10** (✓ regime, ✓ band touch, ✓ above VPOC, RSI neutral; ✗ SMA stack 20<50, ✗ vol 0.22x, ✗ no momentum burst). Pooled t=3.02 ✓ but GOOG t=1.46 ✗. **Cross-market NOT uniform** — ZS PF 2.69 / RDDT 2.27 / GEV 2.02 vs MRVL 0.51 / GDDY 0.69 / FBK 0.91 → data-mining risk; GOOG 2026 negative = decay |

- **Expert consensus: WAIT — no entry.** Trend label is green, but price is outside the band, SMA100 is lost, and no SOS printed.
- **Budget $2,500:** $0 now. On trigger at band bottom $348.12: 1% risk = $25 → **1 share** ($16.6 = 0.7%) ✓ — 2 shares = 1.3% ✗.

### AMZN — bounce under SMA50 supply; the trigger itself has no edge

- **Setup:** $255.10 (+1.47%), RSI 62.5 (monitor), vol 0.31x, 5d 2🔴/3🟢. Above SMA20 $251.19 / SMA100 $252.93 (close > SMA20 = per-plan confirmation ✓) but **still below SMA50 $257.40** — that reclaim is the trigger.
- **Trigger needed (NOT printed):** daily close **> $257.40 (SMA50) on >1.0x volume**.
- **Planned levels:** Entry $257.40 · Stop $246.45 (prior 10-bar swing low, 2×ATR cap) · risk $10.96/sh (4.3%) · TP1 $267.56 (30d high, **0.93R**) · TP2 $280.41 (2.1R).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — 19/40** (below 20 = don't trade), even if the trigger prints | Exact SMA50-reclaim trigger backtested 5y/9 tickers: **Variant B (+vol>1x): n=85, WR 37.6%, +0.071R, PF 1.10, t=0.43**, Kelly 3.6%. Variant A (no vol): n=185, −0.023R, PF 0.97, t=−0.21. AMZN-only B: n=14, +0.422R/PF 1.74 but t=0.97, **2026 0/3 wins (PF 0.00)**, recent half PF 0.77. Portfolio B: **+6.9% total (1.5% CAGR) over 4.5y vs SPY +86.6%** → fails the ultimate question decisively |
| 📊 Wyckoff 2.0 | **ACCUMULATION — NOT CONFIRMED** (range context) | 47% of the 60d range $226.16–$287.20 = balance, not trend. HH/HL off the $226 low, but 10d LH (255.73 vs 259.49). Price +9.9% over 1y VPOC $232.03 / +2.5% over 3m VPOC $248.88 = acceptance, **under SMA50 supply**. OBV 60d falling (−7.6M/day), CMF20 −0.035, 30d up/down vol 0.77, vol 0.31x → **no initiative buying**. Needs real SOS close >$257.40 >1x vol, then Back-Up. Alternative: loss of $244.73 (10d low) → failed accumulation → range short side |
| 🧬 Medallion | **NOISE** | Composite **0.0/10** (✓ above SMA100, RSI neutral, above VPOC; ✗ below SMA50, ✗ SMA stack bearish, ✗ vol 0.33x; mid-range balance). Pooled t=0.43 ≪ 3.0 bar; cross-time H1 43% vs H2 33% deteriorating. Single-name textbook pattern = highest overfit risk |

- **Expert consensus: WAIT — trigger not printed, and the trigger has no demonstrated edge.**
- **Budget $2,500:** risk-compliant size = 2 shares ($514.80 notional, $21.9 = 0.9% risk) ✓ — but verdict NO BET → **$0 deployed**.

### GEV — pulled back INTO the band; best confluence of the three, still WAIT

- **Setup:** $1,036.95 (+4.74%) — now **inside the dip band top** ($1,036.80; at 21:05 it was $1,050.76 above it). 5d 1🔴/4🟢, above SMA20/50/100 ($950.35/$965.35/$998.56), 37% retrace of $868.25→$1,140.99. **RSI 86.8 / Stoch ~97 extreme** and **vol 0.47x on a +4.7% day** = big move on thin demand.
- **Trigger needed (NOT printed):** a completed **test of the band** — hold $1,004.62–$1,036.80 and print a bullish test/SOS bar. Price only touched the top edge intraday; no test bar, no volume.
- **Planned levels:** Entry $1,004.62–$1,036.80 · Stop $939.24 (monitor; script fib618−ATR $934.60) · TP $1,140.99 · R:R **1.07:1 band top → 2.09:1 band bottom** (breakeven WR 49.5% vs 33.9%).

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — 19/40** at market; only band-bottom could ever size | Pooled signal n=836, t=3.02 (same fib-dip signal as GOOG). GEV-only: n=33, WR 66.7%, +0.344R, PF 2.02, t=1.94, Kelly 33.7% — but **2026 GEV flat** (n=15, PF 1.00, −0.001R) and **H2 decayed** (PF 1.23 vs H1 3.41). At band top R:R 1.02–1.07:1 ≈ coin flip. **Not sizeable under the 1% cap:** 1 share stop-risk = $97.56 (3.9%) at top / $65.38 (2.6%) at bottom |
| 📊 Wyckoff 2.0 | **ACCUMULATION CONFIRMED (Phase E markup)** — buy the Back-Up, never the chase | OBV 60d **rising** (+48.8k/day), 30d up/down vol **2.01**, HH/HL (10d 921→1052 / 868), only 2 distribution days/25, price +9.4/+7.7/+4.1% over SMA20/50/100. Caveats: averages still in bearish order (SMA100 998 > SMA50 965 > SMA20 950 = lagging stack), running into prior 30d high **$1,052.78 on 0.47x volume with RSI 86.8 → Upthrust risk** if it stalls. 3m VPOC $985.88 (+5.4%) / 3m VAH $1,072.60 overhead; HVN $980 (32M) under band bottom; stop shelf $930–943 HVN = structural. Primary: test into $1,004–$1,037. Alternative: clean break of $1,052.78 on >1x vol → wait for retest. Failure < $998.48 (SMA100) kills setup |
| 🧬 Medallion | **WEAK SIGNAL** (best of the three) | Composite **+3.5/10** — only positive one (✓ regime, ✓ band, ✓ above SMA100, ✓ above VPOC, ✓ shallow 37% retrace; ✗ vol 0.50x, ✗ SMA stack, RSI neutral in daily terms / 86.8 on the monitor tape). But **GEV t=1.94 < 3.0 bar** and 2026 PF 1.00 → not statistically deployable |

- **Expert consensus: WAIT for the test/Back-Up. Never chase an RSI-86 tape with R:R 1.07:1.**
- **Budget $2,500:** not sizeable within the 1% risk rule → **$0 deployed**.

---

## Not Routed This Run

- **MKSI $279.72** — 🔴 WAIT overbought (RSI 86.0 / Stoch 86.1), cooldown entry $274.21 (SMA50). Routine, not routed.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **NVDU** (27 sh) | **TAKE PARTIAL + TRAIL** | ~$163.55 (sell 1/3–1/2 now) | **+81.7%** ($+1,985.85) | RSI 85.2 + Stoch 95.7 overbought, sitting at 3M high $164.90 resistance, momentum NEUTRAL (+2), volume fading. Trail the remainder with stop **$153.74** (price − 1.5×ATR $6.54). Monitor SL $99.81 / TP2 $106.35 are entry-based and stale — do not use |
| **ZS** (15 sh) | **TAKE PARTIAL + TRAIL** | ~$211.53 (sell 1/3–1/2 now) | **+41.0%** ($+922.95) | TP2 long exceeded; overhead 3M high $216.97; **MACD hist −0.3 bearish**; momentum NEUTRAL (+1). Trail the remainder with stop **$192.31** (price − 2.0×ATR $9.61). Monitor SL $164.41 stale |

Combined open P&L: **+$2,908.80**. One action each: realize a third-to-half into strength, trail the rest.

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| GOOG | $348.35–$356.25 **after SOS bar >1x vol** | $331.73 | — | $381.81 | 1.06 – 2.07 | **NOT PRINTED** — price $344.32 below band, vol 0.22x, SMA100 lost | **WAIT** — Thorp NO BET (24/40, t pooled 3.02 but 2026 decay) · Wyckoff NEUTRAL · Medallion WEAK | $0 now; on print 1 sh = $16.6 risk (0.7%) ✓ |
| AMZN | $257.40 (SMA50 reclaim, >1x vol) | $246.45 | $267.56 | $280.41 | 0.93 / 2.10 | **NOT PRINTED** — price $255.10 < $257.40, vol 0.31x | **WAIT** — Thorp NO BET (19/40, trigger t=0.43, 1.5% CAGR vs SPY 86.6%) · Wyckoff accum. unconfirmed · Medallion NOISE | $0 (2 sh would be 0.9% risk ✓) |
| GEV | $1,004.62–$1,036.80 on test/SOS bar | $939.24 | — | $1,140.99 | 1.07 – 2.09 | **NOT PRINTED** — top edge touched only, vol 0.47x, RSI 86.8 | **WAIT** — Thorp NO BET (19/40) · Wyckoff ACCUMULATION CONFIRMED (buy Back-Up) · Medallion WEAK (+3.5) | $0 — 1 sh = 2.6–3.9% risk > cap ✗ |

**Entries triggered this run: 0 · Conditional: 3 (GOOG, AMZN, GEV) · Exits to act on: NVDU, ZS.**

---
*Entry Monitor 3-Expert Pipeline · monitor_entries.py + Thorp / Wyckoff 2.0 / Medallion · backtests: `_goog_experts.py` + `_gev_experts.py` + `_amzn_experts.py` → `_expert_out.txt` (5y, 9 monitor tickers, net 10bp RT) · 06 Oct 2026 22:00 ICT*
