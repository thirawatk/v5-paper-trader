# 📊 Daily Entry Report — Thu 29 Oct 2026 ICT

**Tape:** VIX 16.9 · 11 of 15 watchlist names in DOWNTREND · scan 1,343/1,463 analyzed · **1 qualifier** at score ≥ 7.0
**Two positions report earnings TODAY (Oct 29, after close): AMZN — which I hold — and GDDY**

## 🔍 Full Scan Results

Scanned: **1,343 of 1,463** stocks (server-side liquidity floor: mcap > $500M, vol > 200k) | Candidates: **1**

| Ticker | Score | Price | %Δ | Setup reason |
|---|---|---|---|---|
| GME | 7.25 | $23.33 | -0.13% | PULLBACK into VPOC $23.70 + SMA50 $22.66 · Stoch 2.6 · vol 0.47× (dry) · CMF +0.037 |

**Near-misses (below 7.0 floor):** MAT 5.75 · CNXN 5.50 · DINO 4.75 · (nothing else above 4.75)

> ⚠️ **Scanner was silently covering 37% of the universe until today.** The old `name match |TICKER|LIST` filter is *substring*-based on TradingView (`BA` returns BAC, BABA, ABAT…). 1,463 tickers produced 4,389 rows against a capped response, so only **539** exact names survived — and which ones survived depended on truncation order. Rebuilt as a paginated full-market pull + exact intersection: **1,343** analyzed, deterministic. Fix is live in `daily_market_scan.py` (backup: `.bak`).

## ⚡ Intra-Day Watchlist Snapshot (Entry Monitor, 03:00 ICT)

| Ticker | Price | %Δ | RSI | Vol | SMA 20 | SMA 50 | SMA 100 | Regime | 5d |
|---|---|---|---|---|---|---|---|---|---|
| GOOG | $322.29 | +1.72% | 30.2 | 1.16× | $336.33 | $338.12 | $344.69 | DOWNTREND | 3🔴/2🟢 |
| RDDT | $134.49 | -1.45% | 28.6 | 1.12× | $150.66 | $151.98 | $163.16 | DOWNTREND | 5🔴/0🟢 |
| GDDY | $106.38 | +0.16% | 55.7 | 0.71× | $104.62 | $100.87 | $94.43 | UPTREND | 3🔴/2🟢 |
| NVDU | $127.77 | -2.27% | 33.6 | 1.03× | $139.18 | $138.57 | $132.48 | DOWNTREND | 3🔴/2🟢 |
| ZS | $255.83 | -1.66% | 68.3 | 0.76× | $225.21 | $201.67 | $174.61 | UPTREND | 2🔴/3🟢 |
| BCC | $74.61 | -1.85% | 51.4 | 0.78× | $75.14 | $76.62 | $76.89 | DOWNTREND | 3🔴/2🟢 |
| FBK | $53.01 | -0.86% | 50.6 | 0.41× | $52.44 | $54.18 | $55.98 | BOUNCE | 3🔴/2🟢 |
| AMZN | $254.67 | +0.62% | 50.5 | 0.76× | $255.17 | $255.12 | $251.85 | DOWNTREND | 2🔴/3🟢 |
| MRVL | $251.68 | +3.33% | 40.4 | 0.53× | $254.27 | $244.08 | $239.80 | PULLBACK | 1🔴/4🟢 |
| GEV | $877.90 | -1.92% | 33.9 | 1.99× | $939.10 | $939.16 | $985.21 | DOWNTREND | 3🔴/2🟢 |
| MKSI | $218.21 | +2.85% | 30.1 | 0.56× | $237.68 | $250.96 | $296.80 | DOWNTREND | 1🔴/4🟢 |
| OPEN | $1.90 | -0.52% | 34.4 | 0.73× | $2.13 | $2.62 | $3.43 | DOWNTREND | 4🔴/1🟢 |
| ACMR | $53.08 | +2.14% | 23.0 | 1.02× | $63.00 | $69.71 | $80.25 | DOWNTREND | 1🔴/4🟢 |
| AMKR | $42.21 | +5.68% | 31.9 | 1.25× | $46.02 | $48.39 | $57.96 | DOWNTREND | 2🔴/3🟢 |
| CRWV | $63.93 | +7.32% | 31.6 | 0.96× | $71.90 | $80.75 | $85.61 | DOWNTREND | 2🔴/3🟢 |

## 📍 Entry Verdicts & Levels

| Ticker | Verdict | Regime | Entry Zone | Stop | TP | Trigger / Notes |
|---|---|---|---|---|---|---|
| GDDY | 🟢 **BEST** (blocked by earnings) | UPTREND | $107.10 buy-stop | $104.40 | $110.61 / $114.77 | Confluence **+0.62** (only gate pass) · **reports TODAY after close — do not enter pre-print** |
| MRVL | 🟡 WAIT | PULLBACK | $244.00–246.00 | $237.90 | $254.27 / $261.43 | Confluence +0.38 (<0.50) · needs retest of HVN $244.65, not a +3.3% chase |
| GME | 🟡 WATCH (no trade) | PULLBACK | $23.85 | $22.35 | $25.58 / $26.30 | Scan hit but confluence **-0.06** · no SOS bar, no stopping volume |
| CRWV | 🔴 WAIT | DOWNTREND | — | — | — | Confluence -0.04 · -45.6% from high · needs reclaim $71.90 |
| ACMR | 🔴 WAIT | DOWNTREND | — | — | — | Confluence **-0.73** (worst) · knife, RSI 22.8 is not a buy signal alone |
| MKSI | ⏸ NOT TRIGGERED | DOWNTREND | $255–274 (plan) | — | — | Spot 14% below zone · confluence -0.27 · plan dormant |
| ZS | ✅ HOLD / trail up | UPTREND | — | $241.91 (raised) | open | +70.5% · weak close at range top |
| AMZN | 🚨 **EXIT** | DOWNTREND | — | — | — | Setup failed + earnings **tonight** → close before the print |

## 🧠 3-Expert Analysis

### GDDY | Entry $107.10 | Stop $104.40 | TP1 $110.61 | TP2 $114.77 | R:R 1.30 / 2.84 | Trigger: **NOT PRINTED** — Oct 22 SOS bar (O $109.25 → C $114.73, close on high, 2.09M vs ~1.4M avg), pullback to $104.86 retested VWAP20 $104.57 + SMA20 $104.63 confluence, Oct 28 reclaimed $106.54 (86% of range). Price is 0.31% under VAH $106.87.

| Expert | Verdict | Conf | Action |
|---|---|---|---|
| 🔢 Thorp | **BET** | MED | Edge = post-SOS back-up in an uptrend with 3 independent factor families agreeing (trend, flow, structure). Base rates thin — one name only, no cross-sectional confirmation. Kelly-sized 1.6% of $2,500. |
| 📊 Wyckoff | **ACCUMULATION** | MED | Phase D: SOS printed Oct 22, BUEC in progress. VPOC $97.27 well below = value built lower. VAH $106.87 is the gate; a rejection there = failed BUEC → flip bearish. |
| 🧬 Medallion | **STRONG** | MED | 8/11 factors positive (Trend, VWAP, OBV, CMF, Candle, Wyckoff, VPOC, Mom). Not a tuned pattern — broad agreement across uncorrelated inputs. t-statistic not computable on one ticker; treat as 1 of 1 candidate, not a portfolio of signals. |

**Consensus:** the best technical setup on the board and the only one clearing the +0.50 gate — **and it is uninvestable today** because GoDaddy reports Q3 after the close (IR-confirmed Oct 29). Do NOT enter pre-print. Entry only after the reaction, on a close that holds above $104.63 (SMA20/VWAP), buy-stop $107.10, stop $104.40, size 15 sh = $1,606 notional, risk $40.50.

### MRVL | Entry $245.00 | Stop $237.90 | TP1 $254.27 | TP2 $261.43 | R:R 1.31 / 2.31 | Trigger: **NOT PRINTED** — selling climax Oct 22 at $220.21 on 24.96M sh (1.6× avg), then 5 consecutive higher closes ($223.47 → $251.65), last close at 73% of range. Price sits 1.04% under the SMA20 $254.27 / VWAP20 $256.89 decision cluster.

| Expert | Verdict | Conf | Action |
|---|---|---|---|
| 🔢 Thorp | **NO BET at $251.65** | MED | Chasing +3.3% into resistance with a 6.55% ATR leaves no viable stop (tight stop = noise, wide stop = 0.5R risk). Edge only exists on the retest. |
| 📊 Wyckoff | **ACCUMULATION (early)** | LOW | SC + AR only — Phase A/B. No spring, no ST test. Down-volume still exceeds up-volume (22.7M vs 18.7M over 20d) = supply not fully absorbed. |
| 🧬 Medallion | **WEAK** | MED | 5/11 factors. VWAP and Wyckoff both negative; volume profile shows VPOC $219.49 far below price = price is away from value, not in it. |

**Consensus:** WAIT. Real trigger is a back-up to the reclaimed HVN $244.65 with a bullish rejection bar; then 10 sh, risk $71 (2.8% of budget — trim to 7 sh to stay ≤2%). Catalysts clear: earnings Dec 1.

### GME | Entry $23.85 | Stop $22.35 | TP1 $25.58 | TP2 $26.30 | R:R 1.15 / 1.63 | Trigger: **NOT PRINTED** — six straight lower closes, last bar closed at 33% of range, Stoch 2.6, volume 0.46× (no stopping volume, no SOS). Price is sitting ON VPOC $23.70, i.e. accepted at value, not shaken out.

| Expert | Verdict | Conf | Action |
|---|---|---|---|
| 🔢 Thorp | **NO BET** | HIGH | 1.15R to first resistance, no structural edge, and meme-float tail risk is unbounded both ways. Expectancy is negative after a realistic stop. |
| 📊 Wyckoff | **NEUTRAL** | MED | No spring, no climax, no SOS — Phase B drift. A high-volume flush under $23.10 followed by a reclaim would be the first real setup. |
| 🧬 Medallion | **NOISE** | HIGH | 4/11. The scan score (7.25) rewards oversold + dry volume, but OBV (-0.173), VWAP and momentum (ROC-10 -14.1%) all contradict. Textbook false positive from a single-factor-heavy score. |

**Consensus:** NO TRADE. This is the case that proves the scan needs the confluence gate — a 7.25 scan score with a -0.06 composite is a value trap, not an entry.

### CRWV | $63.93 | Trigger: **NOT PRINTED** — +7.32% to close at 98% of range (SOS-shaped bar) but price is below all three averages (SMA20 $71.90, SMA50 $80.75, EMA200 $89.54) and -45.6% off the 3-month high.

| Expert | Verdict | Conf | Action |
|---|---|---|---|
| 🔢 Thorp | **NO BET** | HIGH | One up-bar inside a markdown is not an edge; 9.96% ATR makes position sizing guesswork. |
| 📊 Wyckoff | **DISTRIBUTION → markdown** | HIGH | The bounce is an Automatic Rally inside a downtrend, not accumulation. No cause built. |
| 🧬 Medallion | **NOISE** | HIGH | -0.04 composite. Candle +1.0 and MFI +1.0 are overwhelmed by Trend/VWAP/OBV negatives — single-bar signals are the classic overfit trap. |

**Consensus:** WAIT for a close above $71.90 (SMA20) to even open a watch case.

### ACMR | $53.02 | Trigger: **NOT PRINTED** — RSI 22.8, -42.7% from 3m high, OBV slope -0.416, CMF -0.286, position in 60d range 11%.

| Expert | Verdict | Conf | Action |
|---|---|---|---|
| 🔢 Thorp | **NO BET** | HIGH | Lowest composite on the board (-0.73); 10 of 11 factors negative. |
| 📊 Wyckoff | **MARKDOWN** | HIGH | No support structure; every bounce has been sold. |
| 🧬 Medallion | **NOISE** | HIGH | Nothing to combine — the factors agree it is a falling knife. |

**Consensus:** NO TRADE. Reclaim of $63.00 (SMA20) is the first thing that would matter.

### MKSI | Plan zone $255–274 | Trigger: **NOT TRIGGERED** — spot $218.24 is 14% below the bottom of the planned entry zone; SMA50 slope -6.9%; -33.7% from the 3-month high.

| Expert | Verdict | Conf | Action |
|---|---|---|---|
| 🔢 Thorp | **NO BET** | HIGH | The plan's edge was a pullback inside an uptrend. That uptrend is gone; the premise is dead, not the trigger. |
| 📊 Wyckoff | **MARKDOWN** | HIGH | Below all averages, VPOC $257.82 far overhead = heavy supply. |
| 🧬 Medallion | **NOISE** | HIGH | -0.27; the only positives are oversold RSI/MFI, which is a level, not a signal. |

**Consensus:** plan stays dormant, unmodified, untriggered. No averaging, no bottom-fishing. Re-arm only on a reclaim of $255.

## 🚨 Exit Signals — Active Positions

| Ticker | Price | Entry | P&L | Regime | RSI | Stoch | ATR | Momentum | SL | TP1 | TP2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ZS | $255.80 | $150.00 | **+70.5%** (+$1,587) | UPTREND | 68.3 | 81.3 | $12.98 | STRONG | $229.87 → **$241.91** | open | open |
| AMZN | $254.60 | $259.55 | **-1.9%** (-$49.50) | DOWNTREND | 50.5 | 43.5 | $6.67 | WEAK | $246.21 | $269.56 | $272.89 |

### Exit Notes

| Ticker | Signals |
|---|---|
| ZS | Oct 28 bar: O $260.52 → H $265.99 → **C $255.80 at 13% of range** on 0.87× volume. Price is 89% up its 60-day range, 4.5% off the high, and 10.8% above VAH $230.43 — extended, away from value. Composite **+0.55** (Trend/OBV/CMF/VPOC/Mom all +1.0), so the trend is intact, but one factor (Candle) flipped to -1.0. Action: **raise trail from $229.87 to $241.91** (2×ATR below the $267.87 swing high) — locks +61.3% instead of +53%. Keep runner. Earnings Nov 24: decide trail width before then, don't carry a 2×ATR trail blindly into a print. |
| AMZN | **Setup is dead and the event is tonight.** Five consecutive closes below the $256.68 invalidation trigger (250.38 / 248.00 / 249.09 / 253.10 / 254.60), price pinned at the SMA20/SMA50 cluster ($255.17/$255.12) with MACD -0.47, VPOC $261.14 overhead as supply. Q3 2026 results are **confirmed for Oct 29 after the close**. Holding a failed 5-day setup into a binary print is not a trade, it is a coin flip with a -1.9% head start. Action: **exit before the close**, take the -$49.50. |

### 3-Expert on the exits

| Ticker | Thorp | Wyckoff | Medallion | Consensus |
|---|---|---|---|---|
| ZS | **HOLD (BET)** — edge intact, +0.55 composite, trend factors unanimous | **Upthrust risk** — weak close at range top after 267.87 = potential LPSY; needs a close back above 260 to invalidate | **STRONG** — 8/11 positive | Hold runner, trail to $241.91, trim only if a close lands below $241.91 |
| AMZN | **NO BET** — expectancy now dominated by a scheduled binary event, not by the signal | **NEUTRAL→DISTRIBUTION** — below VPOC, failed to hold the SMA cluster | **NOISE** — -0.01 composite | **EXIT before the print** |

## 📈 Journey Snapshot

| Account | Capital | Deployed | Total | Today | Target |
|---|---|---|---|---|---|
| Trading Journey (paper) | $9,480.06 | $463.99 (5/5 pos) | **$9,944.05** (-0.56%) | $0.00 (0.00%) | $100/day (1%) |

| Ticker | Entry → Now | R | Days | Status |
|---|---|---|---|---|
| ARKW | $154.06 → $151.38 | -0.4R | 4 | 🔴 open |
| HUBS | $240.51 → $239.86 | -0.0R | 4 | 🔴 open |
| ZM | $109.84 → $106.30 | -0.5R | 4 | 🔴 open |
| SPNT | $25.17 → $25.27 | +0.1R | 27 | 🟢 open |
| CON | $39.15 → $40.59 | +0.7R | 9 | 🟢 open |

**Stats:** 5 trades · W2 / L3 · WR 40% · Total R -0.60 (avg -0.12) · P&L -$55.96 · PF 0.79 · Max DD 1.7%

**Long-term (VOO/VXUS):** VXUS $83.75 (+0.54%), RSI 47.3, -5.5% from the 52-week high, below SMA100 $85.46 → **DCA add zone** (deep value, not a trade). No VOO trigger.

## 📋 SUMMARY — All Entry Points

| Ticker | Side | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|---|
| GDDY | Long | $107.10 | $104.40 | $110.61 | $114.77 | 1.30 / 2.84 | **NOT PRINTED** — earnings tonight, cannot trigger | 3/3 constructive but **event-blocked** | 15 sh = $1,606 · risk $40.50 (1.6%) |
| MRVL | Long | $245.00 | $237.90 | $254.27 | $261.43 | 1.31 / 2.31 | **NOT PRINTED** — needs retest of $244.65 | 0 BET / 1 early-accum / 1 weak | 7 sh = $1,715 · risk $49.70 (2.0%) |
| GME | Long | $23.85 | $22.35 | $25.58 | $26.30 | 1.15 / 1.63 | **NOT PRINTED** — no SOS, dry volume | 0 BET / neutral / noise | **$0 — do not trade** |
| CRWV | Long | — | — | — | — | — | **NOT PRINTED** — needs > $71.90 | 0 BET / distribution / noise | $0 |
| ACMR | Long | — | — | — | — | — | **NOT PRINTED** — needs > $63.00 | 0 BET / markdown / noise | $0 |
| MKSI | Long | $255–274 (plan) | — | — | — | — | **NOT TRIGGERED** — 14% below zone | 0 BET / markdown / noise | $0 (dormant) |
| ZS | Hold | $150.00 | **$241.91** | open | open | trail | Position open, trail raised | Hold (3/3 intact) | 15 sh held · +$1,587 |
| AMZN | **Exit** | $259.55 | — | — | — | — | **Exit signal — earnings tonight** | 3/3 exit | 10 sh · -$49.50 |

## 🏁 Final Results (3-Expert consensus on today's best entry)

| Ticker | Best Call | Direction | Size | Entry | Stop | TP | R:R | Expert Consensus | Invalidation | Catalyst risk | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **GDDY** | Best setup on the board — **wait for the print** | Long | 15 sh after trigger | $107.10 (buy-stop) | $104.40 | $110.61 / $114.77 | 1.30 / 2.84 | Thorp BET · Wyckoff ACCUMULATION · Medallion STRONG → **3/3 constructive, 0/3 enter today** | Close back below $104.40 (SMA20/VWAP lost) | **Q3 earnings TODAY after close** — do not hold through it | $1,606 notional · $40.50 risk |
| **AMZN** | **Exit before the close** | Long → flat | 10 sh | market on close | — | — | — | Thorp NO BET · Wyckoff NEUTRAL→DIST · Medallion NOISE → **exit** | Already invalidated: 5 closes < $256.68 | **Q3 earnings TONIGHT** into a failed setup | Realizes -$49.50 |
| **MRVL** | Second-best, needs the retest | Long | 7 sh | $245.00 | $237.90 | $254.27 / $261.43 | 1.31 / 2.31 | Thorp NO BET at spot · Wyckoff early ACC · Medallion WEAK → **wait** | Close under $237.90 (loses the reclaimed HVN) | Low — earnings Dec 1 | $1,715 notional · $49.70 risk |
| **ZS** | Manage the winner, don't add | Long (held) | 15 sh | $150.00 (held) | $241.91 | open | trail | 3/3 intact | Close under $241.91 | Earnings Nov 24 | +$1,587 unrealized |

**The honest Thorp answer for today:** one name clears the confluence gate, and it reports earnings in a few hours. The correct number of new positions to open this morning is **zero**. The action with positive expectancy is **closing AMZN before its print** and **raising the ZS trail** — everything else is a watch item.

## 🔧 System Notes (needs your call)

1. **Scanner coverage bug — FIXED.** `match` filter is substring-based; coverage was 539/1,463 and truncation-dependent. Now paginated full-market + exact intersect → 1,343/1,463 (the missing 120 are below the liquidity floor). Backup at `daily_market_scan.py.bak`.
2. **Monitor TP ladder is incoherent for non-held tickers.** MRVL printed `Entry $244.08 · TP1 $254.27 · TP2 $237.23` — TP2 below entry. Cause: TP1 comes from the entry-verdict path (SMA20) while TP2 comes from `calculate_dynamic_exits` (entry + nR on an ATR anchor). For tickers you don't own, targets must be structural (HVN/VAH), not entry+nR. My report uses corrected structural levels.
3. **AMZN stop basis conflicts.** Journal says hard SL $249.33; monitor says $246.21. Oct 23's low was **$246.45**, i.e. the journal stop was breached intrabar and the position survived because the monitor only evaluates closing prices against a floating 2×ATR stop. Pick one basis and write it down — this is how a -1.9% turns into a -5%.
4. **NVDU is still in the 15-ticker watchlist** but the position was fully closed on Oct 7. Fine for re-entry monitoring, but the "rename the cron job to match the ticker list" rule needs a decision if it stays.
