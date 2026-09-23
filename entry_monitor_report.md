# 📡 Entry Monitor Report — Wed 23 Sep 2026 20:01 ICT

**Run:** `monitor_entries.py` exit 0 (TV feed timed out again → EOD fallback) · GOOG = only 🟢 verdict · NVDU/ZS trailing flagged · GDDY 🟡 / BCC ⚠️ / GEV ⚠️ = routine support tests, excluded.
**Change vs 04:17 ICT report:** none material — GOOG $347.35 → $347.41 (monitor still serving Sep 22 close; market opened 09:01 ET, no new bar yet). Fresh verification pull (Yahoo, 250 daily bars) confirms all levels: SMA20 338.82 vs monitor 339.06, SMA50 343.22 vs 343.33, SMA100 356.40 vs 356.67, RSI ~59–64, ROC10 +4.6%, 52w high $403.96 (18 May) → −13.1% drawdown. Analysis below re-affirms the 04:17 verdict.

---

## Actionable Entry Signals

### GOOG

**Setup — post-spring Back-Up onto the broken Creek.** GOOG's 9 Sep spring low **$325.63** (undercutting 1 Sep $329.08) printed at the 126-session **VAL ~$325.5** — shakeout into value-area low. SOS followed: 14 Sep swing high $346.45, then 18–21 Sep push to **$350.87 close = higher high** breaking the Aug–Sep resistance band (8/24 high $348.08, 9/14 $346.45 = the Creek). Price backed up to **$347.41 — inside the broken band, above 126d VPOC ~$342.5 and SMA50 $343.33, below SMA100 $356.67**. Monitor: RSI 63.6, vol 1.16x, 5d 2🔴/3🟢, regime UPTREND.

| Parameter | Value |
|---|---|
| **Entry** (buy-stop only — no limit/market) | **Trigger A:** SOS bar holding ≥ $346.50 → buy-stop above trigger candle high (fill zone $348.35–$356.25 = monitor's dip zone). **Trigger B:** daily close reclaim > **$356.67** (SMA100) → buy-stop above that bar's high |
| **Stop** | **$332.09** — below SMA200 and the 16 Sep higher-low $337.45. Structure stop (Wyckoff option 2) |
| **TP1** | **$366.00** — top of the 126d HVN band $334–366 (first overhead supply node) |
| **TP2** | **$381.81** — monitor target (Aug 5 high + HVN $381–385; path toward 52w high $404.47) |
| **R:R** | From **$348.35**: 1.09R → TP1, **2.06R → TP2** (breakeven win rate 32.7%). Zone-mid $352.30: 0.68R/1.46R (BE 40.6%). Zone-hi $356.25: 0.40R/1.06R — prefer the low end |
| **Invalidation** | Daily close back below **$337.45** = failed Back-Up; accumulation rotates to distribution → stand down |

#### 3-Expert Analysis

| Expert | Verdict | Score | Key evidence |
|---|---|---|---|
| 🔢 **Thorp Edge Evaluation** | **NO BET** (mechanical dip-buy); conditional small only on trigger | **19/40** | Forward-return event study, GOOG 2y (base n=327, +2.32% mean/10d, 62% win): **cross-under SMA20 above SMA200 — n=15, 10d −2.14%, win 40%, t = −3.25**; SMA50 cross-under n=7, 20d −2.87%, win 14%, **t = −8.10**; SMA50 tag n=17, 10d −3.19%, win 12%, **t = −6.64**. All three significantly **negative** — skill requires t > +3.0; samples « 100-trade minimum. **Kelly at zone-mid (b=1.46): p=0.40 → f=0%, p=0.45 → 7.3%, p=0.50 → 15.8%** — observed pullback win rates 12–40% → Kelly = 0. EV at p=0.40: **−$0.33/trade**; at p=0.12: **−$14.25**. Single-trade noise σ ≈ 1.2R » any measurable edge. Score <20 → *"Don't trade. Buy the index."* |
| 📊 **Wyckoff 2.0** | **ACCUMULATION — Phase E, Back-Up in progress (not yet re-confirmed)** | **4/5** | SC/Spring **$325.63** (9 Sep) = 126d VAL $325.5 → SOS 14 Sep + Creek breakout (HH $350.87 > band top $348.08) → **Back-Up into $346–348**, holding above VPOC $342.5 / SMA50 $343.33. OBV repair: 10d slope **+8.18M/day**, 20d +1.78M (50d/100d still −1.03M/−3.93M); 20d up/down volume **1.35** (>1 = absorption). Bear caveats: below SMA100 $356.67, HVN supply $334–366 overhead, 18 Sep bar rejected off $355.13 (closed $344.41), −13.1% off 52w high. Failure line **$337.45** |
| 🧬 **Medallion Pattern** | **WEAK SIGNAL** | **2/5** | ~10 supportive factors (regime, spring, HH, Creek retest, VPOC/VAL confluence, OBV 10/20d turn, up/down vol 1.35, RSI reset, 2.06R at zone low) vs 9 opposing (t = −3.25/−8.10/−6.64 event studies, n « 100, SMA100 overhead, negative 50/100d OBV, HVN supply, −13.1% off high, 1.16x non-climactic volume, zero out-of-sample forward trades). Fails **t > 3.0** (has t < −3 the wrong way), fails **cost-adjusted expectancy**, fails **out-of-sample**. Overfit risk: moderate |

**Expert Consensus: ⚠️ CONDITIONAL — NO ENTRY YET (buy-stop armed only). 0/3 BET.** Structure is a valid accumulation (Wyckoff 4/5) but the entry trigger class has *proven negative* historical expectancy (Thorp 19/40 < 20; Medallion weak). **Action: arm the buy-stop** — require a real SOS bar ≥ $346.50 or the $356.67 SMA100 reclaim before any fill. No limit entry into the dip, no anticipation.

**Budget $2,500:** 7 sh × $348.35 = **$2,438.45**; risk to $332.09 = **$113.82 = 4.6% of budget** (breaches the 1% rule). 1% risk sizing = **1 sh ($348, $16.26 risk = 0.65%)**; max acceptable 2 sh ($32.52 = 1.3%). Given NO BET → **no size until trigger prints; then 1–2 shares only.**

---

## Exit Signals (Active Positions)

| Ticker | Action | Exit Price | P&L | Notes |
|---|---|---|---|---|
| **NVDU** | 📈 TRAILING — hold, no exit triggered | $146.50 | **+62.8% (+$1,525.50)** | Trail $132.12 = price − 2×ATR $7.19 (verified). Regime uptrend, RSI 60.2, momentum STRONG (+6), 10.0% above stop, 5.9% below 3M high $155.73 — let profits run |
| **ZS** | 📈 TRAILING — hold, no exit triggered | $210.18 | **+40.1% (+$902.70)** | Trail $189.68 = price − 2×ATR $10.25 (verified). ⚠️ **At 3M-high resistance $210.73 with Stoch 98.9 / RSI 68.7** — closest of the two to triggering; trail stands −9.8% below price. Let profits run, the trail does the exit |

*Combined open P&L: **+$2,428.20** on $4,680 deployed (+51.9%).*

---

## 📋 SUMMARY — Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|
| **GOOG** | $348.35–$356.25 (buy-stop on SOS bar; alt. reclaim >$356.67) | $332.09 | $366.00 | $381.81 | 1.09R / **2.06R** | ⚠️ **CONDITIONAL — 0/3 BET**: Thorp 19/40 NO BET · Wyckoff 4/5 ACCUMULATION ✅ · Medallion 2/5 WEAK ⚠️ | 7 sh = $2,438 (risk $114 = 4.6%) · 1% rule → 1 sh · **wait for trigger** |

*Not actionable this run: GDDY 🟡 (TP $99.26 vs entry $99.04 = 0.02R, degenerate), BCC ⚠️, GEV ⚠️ (support tests only). RDDT/NVDA-adjacent watchlist silent — no conditions met.*
*Data notes: TV feed timed out (nologin + connection timeout) → monitor fell back to EOD; Yahoo 250-bar pull for this report independently matches monitor SMAs within $0.3. Event-study / OBV / volume-profile figures carried from the 04:17 ICT evidence run — underlying prices unchanged since.*
