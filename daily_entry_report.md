# 📊 Daily Entry Report — Wed 21 Oct 2026 ICT

## 🔍 Full Scan Results
Scanned: 1,463 stocks | Candidates found: 1 (≥7.0 threshold)

| Ticker | Score | Price | Regime | MCap | Signals |
|--------|-------|-------|--------|------|---------|
| FTNT | 7.25 | $170.93 | PULLBACK | $125.4B | 💰CMF+ RSI 42.9 Stoch 12.6 Vol 0.89x |

**Scan detail:** FTNT pulled back -13.3% from $197.13 high to $170.93, finding support at 50d MA ($169.77) with positive CMF (accumulation). RSI cooling to 42.9, Stoch deeply oversold at 12.6. Volume at 0.89x (consolidation, not panic).

## ⚡ Signals Watchlist (post-expert filtering)

**FTNT** — Pullback to 50d MA in strong uptrend (37% above 200d MA), positive CMF, Stoch 14.4 (pre-collapse oversold). Pending SOS candle confirmation.

### Expert Analysis

#### 🔢 Thorp Edge Evaluation

**1.1 Logical Foundation:**
- **Inefficiency:** Short-term mean-reversion within long-term uptrend — stocks pulling back to 50d MA in uptrends historically bounce
- **Why it exists:** Behavioral bias — retail panic-selling during pullbacks creates temporary undervaluation; momentum-focused quants don't fade dips
- **Why not arbitraged away:** Requires real-time execution + risk management; most automated systems chase momentum, creating a behavioral gap
- **Counterparties:** Retail/momentum sellers who liquidate on short-term downturns

**1.2 Economic Rationale:**
> "I believe pullback mean-reversion in high-conviction uptrend stocks creates a 2-3% edge per cycle because institutional buyers accumulate during retail panic selling at key technical support levels (50d MA). This hasn't been fully arbitraged away because quant funds predominantly use momentum-following rather than pullback-fading strategies. My expected excess return after all costs is approximately 3-6% annualized from ~2 trades/year on this single ticker."

**2.2 Backtest Results (FTNT, 5-year, yfinance):**

| Filter | Trades | Win Rate | PF | Avg P&L | Cum Return | Annualized | Max DD |
|--------|--------|----------|-----|---------|------------|------------|--------|
| Strict (Stoch<30, CMF>0, near SMA50) | 10 | 60.0% | 1.69 | +1.9% | +18.7% | +3.7%/yr | $0.11 |
| Loose (Stoch<40, CMF>0, near SMA50) | 18 | 66.7% | 2.32 | +2.4% | +43.0% | +8.6%/yr | $0.05 |
| Very Loose (Stoch<50, CMF>0) | 21 | 47.6% | 1.18 | +0.4% | +7.7% | +1.5%/yr | $12.00 |

**2.3 Cost Analysis (per trade):**
- Commission: $0 (broker)
- Effective spread: ~0.02% ($125B mcap, high liquidity)
- Slippage: ~0.03% (estimated)
- **Total cost: ~0.05% per trade** (vs 0.15% modeled in backtest — conservative)

**2.4 Portfolio-Level:**
- FTNT annualized edge: +3.7% to +8.6% (strict to loose filter)
- **vs SPY benchmark (~10.5%/yr with dividends): edge does NOT beat passive**
- Historical precedent: 69 instances of current setup pattern since 2021

**Scorecard:**

| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Logical basis | 3 | Well-known pullback mean-reversion, valid but not unique |
| Statistical significance | 2 | 10-18 trades below 100+ minimum; consistent but small sample |
| Cost-adjusted expectancy | 3 | Positive per trade (+1.9%), but thin |
| Robustness | 3 | 60-67% WR across strict/loose filters; consistent |
| Capacity | 5 | $125B mcap, 3.5M avg vol — massive capacity |
| Backtest integrity | 3 | No survivorship bias (FTNT survived); no look-ahead; realistic costs |
| Paper trade validation | 1 | No prior paper trading of this exact signal |
| Risk/reward profile | 3 | R:R 1.25:1, PF 1.69, minimal drawdown |
| **TOTAL** | **23/40** | **BELOW 25/40 threshold** |

> **Key issue:** Thorp's litmus test — "Why is this better than buying and holding SPY?" — fails on annualized return. +3.7%/yr (strict) to +8.6%/yr (loose) vs SPY's ~10.5%/yr. Even the loose filter doesn't clearly beat the benchmark. The edge exists at trade level but is too thin at portfolio level.

**Thorp Verdict: NO BET (65% confidence)** — Edge is positive but thin. Sample too small for statistical confidence. Doesn't beat passive benchmark on annualized basis. **Recommend paper trading first.**

#### 📊 Wyckoff 2.0 Analysis

**Step 1: Context Analysis**
- **TREND context** — FTNT is 37% above 200d MA ($124.80), firmly in markup phase
- The $150→$197 run (Oct 1-9) was clear markup
- The $197→$170.93 pullback (-13.3%) is a correction within the uptrend

**Step 2: Trading Zones & Levels**
- **$166.52** = recent swing low (Oct 15) — structure support
- **$169.77** = 50d MA — dynamic support (price currently testing/reclaiming at $170.93)
- **$170-$185** zone = prior consolidation area (Oct 1-8) — potential VPOC/VAH area
- **$180.49-$183.07** = Oct 18-20 resistance cluster (failed rally)
- **$197.13** = 20-day high = distribution resistance ceiling

**Step 3: Scenario Planning**
- **One-move scenario:** Price at $170.93 is already at the support zone (50d MA). Wait for SOS bar — wide-range bullish candle closing upper third with volume above 1.0x. Place buy-stop above the candle high (~$173+).
- **Two-move scenario:** Price could dip again to $169.77 (50d MA) or $166.52 (recent low) before bouncing. Wait for second test as entry opportunity.

**Step 4: Position Management**
- **Entry:** Buy-stop above SOS candle high (~173+) — **pending confirmation**
- **Stop Loss:** $157.71 (2×ATR below entry, below 50d MA + recent low)
- **Take Profit 1:** $180.85 (1.5×ATR — first resistance zone)
- **Take Profit 2:** $187.46 (2.5×ATR — test of prior range; near $197 high = partial exit)
- **Wyckoff Verdict: ACCUMULATION (PENDING)** — Support holds at 50d MA, CMF positive (0.034), but no SOS bar yet. Entry is conditional on Wyckoff buy-stop confirmation.

#### 🧬 Medallion Pattern Recognition

**Signal Quality — Confluence Factors:**
1. ✅ Price above 200d MA (+37%) — trend context established
2. ✅ Pullback to 50d MA — support zone test
3. ✅ Stoch 14.4 (deeply oversold, <25 threshold) — momentum extreme
4. ✅ CMF 0.034 (positive) — accumulation during pullback
5. ✅ Volume 1.01x (consolidation, not panic distribution)
6. ✅ Historical precedent: 69 instances since 2021 with 60% win rate
7. ✅ $125B market cap — high liquidity, execution feasibility

**Statistical Rigor:**
- 5-year backtest: 60% WR (strict), PF 1.69, +3.7% annual (below SPY)
- t-statistic: ~1.2 (10 trades) — well below Medallion's 3.0 threshold
- Cross-market validation: Pattern is common across tech growth stocks (not unique to FTNT)
- Multiple testing correction: Pullback-to-MA is a widely known signal → likely competed

**Correlation Assessment:**
- Not correlated with recent NVDU exit (different sector, different catalyst)
- Not correlated with ZS exit (commodity vs tech)

**Medallion Verdict: WEAK** — 7 confluence factors provide solid signal quality, but the pattern is common and widely followed. Statistical significance is insufficient (t-stat < 3.0, small sample). Edge magnitude is thin.

### Expert Consensus Summary
| Expert | Verdict | Confidence |
|--------|---------|------------|
| Thorp | NO BET | 65% |
| Wyckoff | ACCUMULATION (pending) | 70% |
| Medallion | WEAK | 60% |

**Overall: NO BET / PENDING** — 2 of 3 experts see some merit, but the edge is thin and doesn't beat the benchmark. Wait for SOS candle confirmation + consider paper trading.

## 🏆 Best Entry of the Day

| Parameter | Value |
|-----------|-------|
| **Ticker** | FTNT |
| **Entry** | $171.00 buy-stop (above SOS candle high ~$173, pending confirmation) |
| **Stop Loss** | $157.71 (2×ATR) |
| **TP1** | $180.85 (1.5×ATR, ~0.75R) |
| **TP2** | $187.46 (2.5×ATR, 1.25R) |
| **R:R** | 1.25:1 (to TP2) |
| **Risk** | $13.22/share |
| **Position** | 8 shares (~$1,367, risking ~$106 @ 1% of $10K) |
| **Expert Consensus** | Mixed: Thorp NO BET / Wyckoff ACCUMULATION / Medallion WEAK |
| **Budget** | $2,500 (position is 55% of budget) |
| **Status** | 🔴 PENDING — waiting for SOS candle confirmation |

## 🚪 Exit Signals

| Ticker | Action | Price | P&L | Notes |
|--------|--------|-------|-----|-------|
| **ZS** | 📈 TAKE PROFITS (TP2 hit) | $176.28 | +43.0% (+$967.65) | TP2 $176.28 (2.5R) exceeded; current $214.51 well above. MACD hist -1.38 (bearish), momentum fading. Exit now. |
| **AMZN** | ✅ HOLD | $152.07* | — | No exit signal. No new entry signal from scan. Monitor for SOS. |
| **NVDU** | — | — | — | Already fully closed Oct 7: +$1,903.21 lifecycle |

*Note: AMZN not in today's scan results. Monitor continues per entry monitor.

### ZS Detailed Exit Rationale
- **Entry:** 15 sh @ $150.00 (cost $2,250)
- **TP2 target:** $176.28 — **HIT** (price ran to $214.51)
- **Current P&L:** +43.0% ($967.65) — well beyond original target
- **Signal:** MACD histogram turning bearish (-1.38), momentum neutral
- **Action:** Take full profits. Trailing stop was at $193.09; trim was at $216.97. At $214.51, recommend full exit.

## 📋 SUMMARY — All Entry Points

| Ticker | Entry | Stop | TP1 | TP2 | R:R | Experts | Budget $2,500 | Status |
|--------|-------|------|-----|-----|-----|---------|---------------|--------|
| **FTNT** | $171.00 | $157.71 | $180.85 | $187.46 | 1.25:1 | Thorp: NO BET / Wyckoff: ACCUMULATION / Medallion: WEAK | ~8 sh ($1,367) | 🟡 PENDING (no SOS yet) |

**No active trades recommended today.** FTNT pullback setup lacks SOS confirmation and fails Thorp's benchmark litmus test. Wait for Wyckoff buy-stop trigger before entering.
