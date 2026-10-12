# 📡 Entry Monitor Report — Mon 12 Oct 2026 20:35 ICT

**Run:** monitor_entries.py (live) | **Routed:** 4× 🟢 structure (all conditional), 1× exit trail, 2× not routed
**Data note:** TradingView feed timed out → Google Finance fallback for 2 symbols; intraday volume ratios session-adjusted.

---

## 🟢 Entry Triggered

**None — no confirmation triggers printed this run.**

All four 🟢 verdicts are structure-only: volume 0.00–0.05x across the board (confirmation requires >1x), no SOS bar, and three of four prices sit outside their entry bands. Routed to experts as conditional setups below.

---

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG
- **Setup:** Uptrend — price $348.74 sitting on SMA100 $349.97, 1.8% above 60d VPOC $341.60, SMA20 rising ($339.7 → $342.6)
- **Trigger needed:** Green close ≥ $349.97 on volume >1x (SOS bar). Volume now 0.01x — drift, no participation
- **Planned:** Entry $348.35–356.25 | Stop $332.88 | TP $381.81 | R:R ≈ 2.0

| Expert | Verdict | Key finding |
|---|---|---|
| 🔢 Thorp | **NO BET** (conf: high) | R:R 2.08 → breakeven WR 33%. EV @45% WR = +0.39R, half-Kelly ≈ 0.09 — economics fine, but 0.01x volume means there is no signal to evaluate yet |
| 📊 Wyckoff | **NEUTRAL** | Phase E markup pullback (Back Up) into SMA100/VPOC confluence — textbook test, but no SOS bar. Wait for the test to hold |
| 🧬 Medallion | **WEAK SIGNAL** | 3/9 factors aligned (trend, SMA stack, momentum); volume factor dead. Single-ticker n=1 → no statistical significance |

**Consensus: WAIT 3/3** — budget $2,500 held in reserve, $0 deployed.

### RDDT
- **Setup:** +6.9% 5d bounce off $142–145 base, reclaimed SMA50 $154.44, now at Fib 61.8% zone $160–165 (60d VPOC $158 = acceptance)
- **Trigger needed:** Green close > SMA100 $164.84 on >1x volume, THEN price must reach band $171.11–179.58. Price $160.62 still below band
- **Planned:** Entry $171.11–179.58 | Stop $156.69 | TP $207.00 | R:R ≈ 1.7

| Expert | Verdict | Key finding |
|---|---|---|
| 🔢 Thorp | **NO BET** (conf: medium) | R:R 1.70 → breakeven WR 37%. EV @45% = +0.22R, half-Kelly ≈ 0.06. Decent economics — but price hasn't reached the band, so no trade exists |
| 📊 Wyckoff | **NEUTRAL (accumulation lean)** | Higher lows from $140 base = potential Phase D; 61.8% retrace = overhead supply. Needs SOS above $164.84 to confirm |
| 🧬 Medallion | **WEAK SIGNAL** | 4/9 factors (trend, reclaim, momentum, Fib) but below SMA100 + 0.02x volume. +6.9% in 5d on dead volume = thin move |

**Consensus: WAIT 3/3** — $0 deployed.

### MRVL
- **Setup:** +23.7% 20d markup, 87% of 3m range, 2d green streak — but price $275.33 is **~20% above 60d VPOC $229.02** and $27 above the band top
- **Trigger needed:** Pullback INTO band $232.08–248.41 (value area). No chase above the band
- **Planned:** Entry $232.08–248.41 | Stop $202.62 | TP $301.27 | R:R ≈ 1.6

| Expert | Verdict | Key finding |
|---|---|---|
| 🔢 Thorp | **NO BET** (conf: high) | Chasing 20% above value destroys the edge. In-band entry: R:R 1.62, EV +0.18R @45%, half-Kelly ≈ 0.06 — marginal even at plan levels |
| 📊 Wyckoff | **NEUTRAL** | Late Phase E markup; last 10 sessions stall below 3m high $286.95 = possible Shortening of Thrust. Don't buy extension |
| 🧬 Medallion | **WEAK SIGNAL** | Momentum strong but extension above VPOC is mean-reversion risk, not trend edge. Overfit risk high on 1 hot stretch |

**Consensus: WAIT 3/3** — $0 deployed.

### GEV
- **Setup:** +13.4% 20d uptrend pulling into SMA50 $968.82 + 60d VPOC $971.95 + SMA100 $996.82 confluence; Fib zone $1004.62–1036.80
- **Trigger needed:** Price must first RISE into band $1004.62–1036.80 and print a green close on >1x volume. Now $995.99 (below band), vol 0.00x
- **Planned:** Entry $1004.62–1036.80 | Stop $937.39 | TP $1140.99 | R:R ≈ 1.4

| Expert | Verdict | Key finding |
|---|---|---|
| 🔢 Thorp | **NO BET** (conf: medium) | R:R 1.44 → breakeven WR 41%. EV +0.10R @45% — thinnest of the four, half-Kelly ≈ 0.03. Fails Thorp's "better than the index?" bar without a trigger |
| 📊 Wyckoff | **NEUTRAL** | Pullback to value (VPOC/SMA50) = healthy Back Up in markup, but today's bar is a low-volume lower-high test — no SOS |
| 🧬 Medallion | **WEAK SIGNAL** | 3/9 factors; good confluence zone, zero volume participation → no confirmation |

**Consensus: WAIT 3/3** — $0 deployed.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| ZS (15 sh @ $150) | **HOLD — TRAILING** | $235.66 (trail stop $217.26) | +57.1% (+$1,284.90) | 2×ATR trail. New 3M high $235.02, Stoch 98.8 / RSI 66.7 overbought. Floor if stopped: **+$1,008.90 (+44.8%)** |

- **Wyckoff:** Phase E markup, no SOW bar → no distribution evidence. Let profits run
- **Medallion:** momentum STRONG (+4), +16.5% 5d → hold. But 0.04x volume + 3M-high resistance $236.26 = do not add
- **Thorp:** giving back ~7.8% to the trail is the cost of the trend; expectancy positive while regime intact. No action

**Not routed this run:** OPEN (⏳ squeeze watch — downtrend at 3M low; trigger: green close + vol>1.3x), ACMR (🔴 wait — below all SMAs; needs close > $74.16).

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| GOOG | $348.35–356.25 | $332.88 | $381.81 | — | 2.0 | ❌ NOT PRINTED (vol 0.01x) | WAIT 3/3 | $0 deployed |
| RDDT | $171.11–179.58 | $156.69 | $207.00 | — | 1.7 | ❌ NOT PRINTED (price below band) | WAIT 3/3 | $0 deployed |
| MRVL | $232.08–248.41 | $202.62 | $301.27 | — | 1.6 | ❌ NOT PRINTED (price above band) | WAIT 3/3 | $0 deployed |
| GEV | $1004.62–1036.80 | $937.39 | $1140.99 | — | 1.4 | ❌ NOT PRINTED (vol 0.00x) | WAIT 3/3 | $0 deployed |
| ZS | — (hold) | $217.26 trail | — | — | — | ✅ TRAILING ACTIVE | HOLD 3/3 | +57.1% running |

**Bottom line:** 0 entries, 0 exits. Four structures are healthy but every volume reading is ≤0.05x — the market is not confirming anything today. ZS trail holds at $217.26 (locks ≥ +44.8%). Next run: GOOG close vs $349.97 and RDDT close vs $164.84, both on >1x volume.
