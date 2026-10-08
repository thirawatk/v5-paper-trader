# 📡 Entry Monitor Report — Thu 08 Oct 2026 20:02 ICT

*3-Expert pipeline: Thorp Edge · Wyckoff 2.0 · Medallion Pattern — run from monitor_entries.py (TV feed timed out mid-run, fallback data used — all prices clean, no NaN artifacts)*

## 🟢 Entry Triggered

### AMZN
- **Setup:** Uptrend pullback into Fib zone $256.68–263.88, riding SMA50 support ($258.01), all three SMAs stacked below price. Price $259.92 (+1.42%) | RSI 62.1 | Vol 1.01x | 5d 2🔴/3🟢
- **Entry:** $259.92 (band $256.68–263.88 — do not pay above $263.88)
- **Stop:** $244.19
- **TP1:** $287.20 (single-target plan)
- **TP2:** — (plan uses one target)
- **R:R:** 1.73 from current price (2.44 from band low, 1.18 from band top)
- **Trigger: PRINTED** — evidence: `🟢 CLOSE > SMA20 ($251.63) — entry confirmation per approved plan` + price inside Fib zone + green close on 1.01x volume

| Expert | Verdict | Key note |
|---|---|---|
| 🔢 Thorp | **BET — Medium** | R:R 1.73 → breakeven WR ~37%; round-trip costs <5% of risk; n=1 so this is forward-validation, not proven alpha vs SPY |
| 📊 Wyckoff | **ACCUMULATION CONFIRMED** | Phase E markup, green close = SOS bar; key zone $256.68–258.01 — daily close below it negates setup |
| 🧬 Medallion | **STRONG SIGNAL (6/6)** | Clears costs (0.8% of 1R) but all 6 factors are one price-derived family — crowded trend-pullback echo, n=1 |

**Expert consensus: ENTER (3/3 pass).** Budget $2,500: 4 shares ≈ **$1,040** (risk $62.92 ≈ 0.9%) — Medallion suggests half size (2 sh) until sample builds. Entry invalid if daily close < $256.68.

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG
- **Setup:** Uptrend, 4/5 green days — but price $347.37 sits BELOW entry band and vol 0.65x = rally without demand
- **Trigger needed:** daily close ≥ $351.27 (SMA100) entering the band, on volume ≥1.0x (SOS bar)
- **Planned:** entry $348.35–356.25 (mid $352.30) | stop $331.65 | TP $381.81 | R:R 1.43
- **Experts:** Thorp NO BET (High) · Wyckoff NEUTRAL · Medallion NOISE (2/6)
- **Consensus: WAIT** — Budget: $0 until trigger prints

### GEV
- **Setup:** −3.12% red day landing exactly on SMA100 $997.55, price below band $1004.62–1036.80, RSI 70.5 still hot, vol 0.9x
- **Trigger needed:** green close ≥ $1004.62 (reclaim SMA100 + band low) on vol ≥1.0x; alternative: close < $997.55 on expanding volume → stand aside
- **Planned:** entry $1004.62–1036.80 (mid $1020.71) | stop $939.14 | TP $1140.99 | R:R 1.47
- **Experts:** Thorp NO BET (High) · Wyckoff NEUTRAL · Medallion NOISE (2/6)
- **Consensus: WAIT** — Budget: $0

### MKSI *(planned swing MKSI-SW-1)*
- **Setup:** Price $273.15 IN Zone A ($255–274) at SMA50 $274 — **but RSI 75.3 violates the plan's own "RSI>70 = no entry" rule**, vol 0.83x, 11-factor gate (≥+0.50) not run, monitor verdict only ⏳ MONITOR
- **Trigger needed:** RSI ≤70 while holding $255–274 (ideally reclaim/close > $274) + 11-factor gate ≥ +0.50; OR Zone B: daily close > $311 on volume
- **Planned:** one full-size entry, zone mid $264.50 | SL 2×ATR −$19.78 → $244.72 | TP1 $294.17 (1.5R, trim half) | TP2 $313.95 (2.5R, trim half) | time stop 2–4wk | no averaging
- **Experts:** Thorp NO BET (High) · Wyckoff NEUTRAL · Medallion NOISE (1/6)
- **Consensus: WAIT — rule-blocked.** Budget: $0

### AMKR
- **Setup:** Pullback pressing SMA20/50 cluster ($51.73/$51.49) inside larger markdown — price 15.6% BELOW SMA100 $61.94; vol 0.69x
- **Trigger needed:** RSI <50 + green close at/near $51.49 (neither printed: RSI 60.8, red day −2.10%)
- **Planned:** entry $51.49 | stop $47.92 | TP1 $54.02 (R:R 0.71) | TP2 $57.53 (R:R 1.69)
- **Experts:** Thorp NO BET (High) · Wyckoff NEUTRAL · Medallion NOISE (1/6)
- **Consensus: WAIT** — Budget: $0. Flag: TP1 at 0.71R is negative expectancy after costs even if trigger fires

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| ZS | HOLD — TRAILING (no exit) | $213.55 (mark) | **+42.4% (+$953.25)**, 15 sh @ $150 | Trail SL $194.81 (2×ATR below price); near 3M high / trim zone $216.97 — resistance. Let run; first distribution warning = wide-range red bar closing lower third on heavy volume at the high |
| NVDU | — (closed Oct 7) | — | +$1,903.21 realized | No signal this run |

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| **AMZN** | $259.92 (≤$263.88) | $244.19 | $287.20 | — | 1.73 | **PRINTED** | **ENTER** (BET/ACCUM/STRONG) | ~$1,040 (4 sh) |
| GOOG | $348.35–356.25 | $331.65 | $381.81 | — | 1.43 | NOT PRINTED | WAIT (NO BET/NEUTRAL/NOISE) | $0 |
| GEV | $1004.62–1036.80 | $939.14 | $1140.99 | — | 1.47 | NOT PRINTED | WAIT (NO BET/NEUTRAL/NOISE) | $0 |
| MKSI | $255–274 (mid $264.50) | $244.72 | $294.17 | $313.95 | 1.5 / 2.5 | NOT PRINTED (RSI>70 rule) | WAIT (NO BET/NEUTRAL/NOISE) | $0 |
| AMKR | $51.49 | $47.92 | $54.02 | $57.53 | 0.71 / 1.69 | NOT PRINTED | WAIT (NO BET/NEUTRAL/NOISE) | $0 |

**Panel notes:**
- Only 1 of 5 setups has a printed trigger — the pipeline is filtering correctly; the other four are not relabeled entries.
- 4 of 5 "UPTREND" verdicts show SMA100 as the highest MA with price below it (GOOG, GEV, MKSI, AMKR) — swing-level calls inside larger 100-day declines.
- All vol ratios 0.65x–1.01x: no accumulation anywhere is volume-confirmed except AMZN (and that is only average).
- Correlation risk: AMZN fill + ZS runner + watchlist are one risk cluster — cap new concurrent entries, keep 1% hard stop (V5 lesson: positive trade-level expectancy ≠ portfolio alpha).
- Sample math (Medallion): this batch can never reach t>3 — track as one strategy line, scale only after 10+ printed-trigger samples.
