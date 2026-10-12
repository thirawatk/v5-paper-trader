# 📡 Entry Monitor Report — Mon 12 Oct 2026 21:00 ICT

**Run:** monitor_entries.py (live) | **Routed:** 2× 🟢 structure (both conditional), 1× exit trail, 2× not routed
**Data note:** TradingView feed timed out → fallback quotes; US session only ~30 min old, so volume ratios (0.03–0.09x) are partial-session and no daily close exists yet.

---

## 🟢 Entry Triggered

**None — no confirmation triggers printed this run.**

Both 🟢 verdicts are structure-only: no SOS bar, no close, volume far below 1.0x, and GEV is still outside its band. Routed as conditional setups below.

---

## 🟡 Conditional Setup — Trigger Not Printed

### GOOG
- **Setup:** UPTREND — price $349.83 sitting exactly on SMA100 $349.98, above SMA20 $342.65 / SMA50 $343.25. Ascending lows 332.65 → 339.15 → 341.70 → 346.88 → 348.06. RSI 52.4 neutral, 5d 1🔴/4🟢, 6mo range 313.69–404.47
- **Trigger needed:** Green close ≥ $350 on volume ≥1.0x (16.3M sh) — SOS bar confirming acceptance above SMA100. Now vol 0.09x = drift, no participation. **NOT PRINTED**
- **Planned:** Entry $348.35–356.25 | Stop $332.62 | TP1 $367.00 (1.5R) | TP2 $381.81 | R:R ≈ 1.9

| Expert | Verdict | Key finding |
|---|---|---|
| 🔢 Thorp | **NO BET** (conf: medium) | R:R 1.9 → breakeven WR 34%; EV @45% WR ≈ +0.30R, half-Kelly ≈ 0.07. Economics fine — but with 0.09x volume and no close there is no signal to evaluate yet. Logical basis = trend continuation only, no structural edge. Score 22/40 → paper only |
| 📊 Wyckoff | **NEUTRAL-BULLISH** | Phase E markup out of the Oct-1 SC ($332.65), current action = Back Up into the SMA100/HVN. Acceptance above $350 with volume → $356 then $381. Loss of $341.70 → back to range, bias flips |
| 🧬 Medallion | **WEAK SIGNAL** | 4/9 factors (trend, higher lows, SMA stack, momentum +5) / dead volume, neutral RSI (no edge), mid-range position. n=1 asset, no OOS, t-stat n/a — the missing volume leg is exactly what separates signal from noise |

**Consensus: WAIT 3/3** — budget $2,500 held in reserve, $0 deployed.

### GEV
- **Setup:** UPTREND — price $999.80 is **below** the Fib band, holding SMA100 $996.86 (SMA20 $964.66 / SMA50 $968.90 below). Markup 856 → 1195.94; Oct 6 SOS bar to $1052.78 on 1.21x vol, now backing up. RSI 65.2 stretched, vol 0.05x
- **Trigger needed:** Price must first reclaim $1004.62 and print a wide-range green close ≥$1010 on ≥1.0x vol (2.1M sh). **NOT PRINTED** (price below band)
- **Planned:** Entry $1004.62–1036.80 | Stop $937.32 | TP $1140.99 | R:R = 2.03R at low band, **only 1.05R at high band** — entry placement is the whole trade

| Expert | Verdict | Key finding |
|---|---|---|
| 🔢 Thorp | **NO BET** (conf: medium) | Breakeven WR 33% at $1004.62 vs 49% at $1036.80 — same "setup", opposite expectancy. No structural edge; buying a 40% run at RSI 65 is momentum-chasing. EV +0.10R @45% at low band only, half-Kelly ≈ 0.03 — thinnest of the two. Score 21/40 |
| 📊 Wyckoff | **NEUTRAL** | Markup pullback, not accumulation. Oct 6 = SOS; today = Back Up testing broken structure + SMA100. Hold $996.86 → continuation; lose $973/$964 → deeper markdown. Cannot anticipate with a limit order |
| 🧬 Medallion | **WEAK SIGNAL** | 3/9 factors; adverse RSI 65, price outside band, 5d mixed (2🔴/3🟢), momentum fading since Oct 7, zero volume participation → no confirmation |

**Consensus: WAIT 3/3** — $0 deployed. Prefer low band only; skip if it runs to $1036 without you.

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| ZS (15 sh @ $150) | **HOLD — TRAILING** | last $231.82 (trail $212.90) | +54.5% (+$1,227.30) | Gapped to 3M high $237.22 then faded to $230.55; Stoch 89 overbought. Let run |

- **⚠️ Trail ratchet flaw:** script recomputes 2×ATR off *current* price — trail dropped $217.26 (20:35 run) → $212.90 as price pulled back. A trailing stop must never move down. **Hard floor = $217.26 → locks ≥ +$1,008.90 (+44.8%)**
- **Wyckoff:** Phase E markup, no SOW bar on the fade from $237 → distribution not confirmed. Let profits run
- **Medallion:** momentum STRONG (+5) → hold; but 0.14x volume at 3M-high resistance = do not add
- **Thorp:** giving back ~8% from peak to the trail is the cost of the trend; expectancy still positive while regime intact. No action

**Not routed this run:** OPEN (⏳ squeeze watch — RSI 14.4 at 3M low $2.11, trigger: green close + vol>1.3x), ACMR (🔴 wait — below all SMAs, needs close > $74.16). RDDT/MRVL no longer emitting 🟢 (still outside their bands per the 20:35 run — unchanged).

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|
| GOOG | $348.35–356.25 | $332.62 | $367.00 | $381.81 | 1.9 | ❌ NOT PRINTED (close ≥$350 + vol ≥1.0x needed) | WAIT 3/3 | $0 deployed |
| GEV | $1004.62–1036.80 | $937.32 | $1070.50 | $1140.99 | 2.03 (low band) | ❌ NOT PRINTED (price $999.80 below band) | WAIT 3/3 | $0 deployed |
| ZS | — (hold) | **$217.26 hard floor** (script: $212.90) | — | — | — | ✅ TRAILING ACTIVE | HOLD 3/3 | +54.5% running |

**Bottom line:** 0 entries, 0 exits. Both structures are healthy but nothing is confirmed — partial session + volume ≤0.09x. ZS floor fixed at $217.26 (locks ≥ +44.8%). Next run: GOOG close vs $350 and GEV reclaim of $1004.62, both on >1x volume.
