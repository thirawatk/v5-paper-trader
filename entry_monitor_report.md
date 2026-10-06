# 📡 Entry Monitor Report — Tue 06 Oct 2026, 21:05 ICT

Run: `monitor_entries.py` (live 21:01 ICT). Context: US session opened 21:00 ICT — today's volume bars are partial-session. Structure data: Yahoo 4mo daily (84 bars).

## 🟢 Entry Triggered

**None — no confirmation triggers printed this run.**

---

## 🟡 Conditional Setup — Trigger Not Printed

### AMZN — bounce inside range, waiting for SMA50 reclaim

- **Setup:** recovery bounce inside the post-markdown range (60d high $287.20 → low $225.55 → now $253.34). Close above SMA20 ($251.11) and SMA100 ($252.91), still **below SMA50 ($257.37)**. RSI 60.6, volume 0.15x session / 0.79x 5-day avg. 5d: 2🔴/3🟢 with HH/HL intact; 20d: −1.6% (range, not trend).
- **Trigger needed (NOT printed):** daily close **> $257.37 (SMA50) on >1.0x volume**.
- **Planned levels:** Entry $257.37 · Stop $247.80 (below Oct-1 swing low) · TP1 $267.56 (30d high, 1.07R) · TP2 $277.43 (2.1R) · Risk $9.57/sh.

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET now** (confidence: medium-high); on print → small bet only · **22/40** (paper-only band) | Edge = textbook SMA50-reclaim momentum, logical basis 2/5. Assumed 45% WR @ 1.4R avg win → EV ≈ **+0.06R/trade** — thin. ¼-Kelly ≈ 1–2 shares. No backtest of this trigger (integrity 2), zero paper trades (validation 1). Liquid mega-cap: costs 4/5, capacity 5/5. |
| 📊 Wyckoff 2.0 | **ACCUMULATION — NOT CONFIRMED** (Phase B→D range) | HH/HL off the $225 low, price mid-range above the SMA20/100 "creek" but under SMA50 supply. Today's close >SMA20 is a mini-SOS, but 0.15x volume = no initiative buying. Needs a real SOS bar: close >$257.37 with >1x volume, then Back-Up test. Alternative: loss of $248 → failed accumulation → range short side. |
| 🧬 Medallion | **WEAK SIGNAL** | Confluence 4/9 positive (>SMA20, >SMA100, 5d HH/HL, RSI>50) vs 3 negative (<SMA50, volume 0.15x/0.79x, 20d −1.6%). Single-name textbook pattern, no t-stat, no multi-market validation → high overfit/data-mining risk. Below the 11-factor bar. |

- **Expert consensus: WAIT — trigger not printed. No entry.**
- **Budget $2,500:** risk-compliant size = **2 shares** ($515 committed, stop-risk $19 = 0.8%). Full-budget 9 shares = $86 risk (3.4%) — violates the 1% rule.

### GEV — vertical markup, do not chase; buy the Back-Up

- **Setup:** +6.14% to $1,050.76, 5d +8.65%, above SMA20/50/100 (951/966/999), 1🔴/4🟢. **RSI 87.9 / Stoch ~97 = extreme.** 5-day volume 0.79x avg and declining (Oct-1 2.95M → Oct-5 1.67M) — rally on thinning demand.
- **Trigger needed (NOT printed):** pullback **into** the dip zone **$1,004.62–$1,036.80**, then a bullish test/SOS. Price at $1,050.76 is **above the zone** — the monitor's "in Fib pullback zone" label is stale.
- **Planned levels (monitor plan):** Entry $1,004.62–$1,036.80 · Stop $939.25 · TP $1,140.99 · R:R **2.09R from zone bottom / 1.07R from zone top**.

| Expert | Verdict | Key Evidence |
|---|---|---|
| 🔢 Thorp Edge | **NO BET — 18/40** (below 20 = don't trade) | No backtest of the Fib-pullback entry (integrity 1), zero paper trades (validation 1). Chasing RSI 88 has structurally negative expectancy. Even at zone-bottom entry (2.09R), minimum size = 1 share → stop-risk $65 = **2.6% of budget, over the 1% cap** — the strategy cannot be sized within the risk rule. |
| 📊 Wyckoff 2.0 | **ACCUMULATION CONFIRMED (Phase E markup)** — buy the Back-Up, never the chase | Markup $855 → $1,050, HH/HL, full bullish SMA stack. But running into the prior 30d high $1,052.78 on fading volume = **Upthrust risk** if it stalls. Primary plan: Back-Up into $1,004–$1,037 (Fib + broken-structure confluence). Alternative: clean break of $1,052.78 on >1x volume → wait for the retest, don't enter mid-bar. Failure back under $999 (SMA100) kills the setup. |
| 🧬 Medallion | **WEAK SIGNAL** | 6/9 positive confluence (regime uptrend, full SMA stack, HH/HL, 4/5 green days, Fib proximity) but negated by RSI 87.9 extreme, declining volume, single-name, no out-of-sample evidence. Momentum is real; entry timing is statistically unproven. |

- **Expert consensus: WAIT for the dip. No entry at $1,050.**
- **Budget $2,500:** 2 shares in zone ≈ $2,040; stop-risk 2 × $65 = $131 (5.2%) > 1% rule; 1 share alone = 2.6%. **Not sizeable under the risk cap.**

---

## Not Routed This Run

- **GOOG $342.79** — below SMA100 ($351.75) and below its own "entry-on-dip" band ($348.35–$356.25); pre-run verdict MONITOR / entry unclear. 📏 testing-support, no trigger, no clean setup.
- **MKSI $285.10** — 🔴 WAIT overbought (RSI 88.0 / Stoch 97.3), cooldown entry $274.31. Routine, not routed.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| NVDU | **TAKE PARTIAL + TRAIL** | ~$163.50 (sell 1/3–1/2 now) | **+81.7%** ($+1,984.50) | TP2 long since hit; RSI 85.2 + Stoch 95.6; sitting at 3M high $164.90 resistance; 5d volume 0.76x (fading). Trail the remainder with stop **$153.69** (price − 1.5×ATR $6.54). Monitor's SL $99.81 is entry-based/stale — do not use. |
| ZS | **TAKE PARTIAL + TRAIL** | ~$211.30 (sell 1/3–1/2 now) | **+40.9%** ($+919.80) | TP2 hit; overhead 3M high $216.97; MACD hist −0.31 bearish; 5d volume 0.64x (fading), momentum NEUTRAL. Trail the remainder with stop **$192.10** (price − 2.0×ATR $9.61). Monitor's SL $164.41 is stale. |

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| AMZN | $257.37 | $247.80 | $267.56 | $277.43 | 1 : 2.1 (TP2) | **NOT PRINTED** — needs close >$257.37 on >1x volume | **WAIT** — Thorp NO BET (22/40) · Wyckoff accum. unconfirmed · Medallion WEAK | 2 sh = $19 risk (0.8%) ✓ / 9 sh = 3.4% ✗ |
| GEV | $1,004.62–$1,036.80 | $939.25 | — | $1,140.99 | 1.07 – 2.09 | **NOT PRINTED** — price $1,050.76 above zone | **WAIT** — Thorp NO BET (18/40) · Wyckoff buy Back-Up · Medallion WEAK | not sizeable within 1% risk |

**Entries triggered this run: 0 · Exits to act on: NVDU, ZS (take partial into strength, trail the rest).**

---
*Entry Monitor 3-Expert Pipeline · monitor_entries.py + Thorp / Wyckoff 2.0 / Medallion · 06 Oct 2026 21:05 ICT*
