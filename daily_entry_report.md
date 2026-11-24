# 📊 Daily Entry Report — Wed 25 Nov 2026 ICT

> New-entry scanner only. Open-position management belongs to cron 906420a9f2e2.

## 🔍 Full Scan Results

Scanned: **1,308 stocks** (2,444 market rows from the 1,463-ticker universe) | Qualifying (score ≥ 7.0): **1**

| Ticker | Score | Price | %Δ | Setup reason |
|---|---|---|---|---|
| VSXY | 7.25 | $93.38 | -0.88% | PULLBACK · CMF+ · -19.7% off 3m high $116.32 · holding rising SMA50 $92.74 |

- Liquidity: mcap $7.4B, ADV-20 ≈ 1.25M sh (~$117M/day) → passes the $500M / $2M floor.
- Breadth: VIX 27.0; 16 of the 18 watchlist names sit in DOWNTREND below all three SMAs. The scan gate (UPTREND/PULLBACK + RSI ≤ 45) produced exactly one qualifier — thin list, and the screen is behaving correctly, not broken.
- Identity check: VSXY = **Victoria's Secret & Co.** (NYSE), former ticker VSCO, renamed 2 Jun 2026. TradingView and Yahoo return byte-identical bars ($93.38 / 1,248,839 sh on 24 Nov) — valid listing, not a phantom symbol.

## ⚡ Intra-Day Watchlist Snapshot (informational)

| Ticker | Price | %Δ | RSI | Vol | SMA 20 | SMA 50 | SMA 100 | 5d | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| GOOG | $276.58 | -1.06% | 42.8 | 0.77x | $283.52 | $316.65 | $330.58 | 3🔴/2🟢 | — |
| RDDT | $90.34 | +1.78% | 39.0 | 0.51x | $98.64 | $130.25 | $148.36 | 3🔴/2🟢 | — |
| GDDY | $102.28 | +0.49% | 25.2 | 0.77x | $110.26 | $105.33 | $100.11 | 3🔴/2🟢 | 🔴 WAIT |
| NVDU | $58.52 | -11.76% | 28.8 | 1.07x | $84.61 | $118.09 | $124.82 | 4🔴/1🟢 | — |
| ZS | $231.62 | +1.04% | 53.3 | 2.01x | $211.25 | $213.93 | $189.31 | 1🔴/4🟢 | flat, no position |
| BCC | $65.77 | +0.55% | 24.1 | 0.82x | $70.33 | $73.48 | $76.17 | 2🔴/3🟢 | — |
| FBK | $52.38 | +0.44% | 29.2 | 0.64x | $53.80 | $53.07 | $55.82 | 3🔴/2🟢 | — |
| AMZN | $252.29 | -1.21% | 41.0 | 0.61x | $257.70 | $255.15 | $255.35 | 3🔴/2🟢 | flat, stopped 20 Nov |
| MRVL | $131.57 | -9.10% | 40.6 | 0.80x | $161.00 | $216.99 | $216.38 | 4🔴/1🟢 | — |
| GEV | $720.65 | -4.77% | 36.7 | 0.76x | $804.33 | $888.10 | $940.14 | 4🔴/1🟢 | — |
| MKSI | $191.32 | -6.82% | 48.8 | 1.04x | $204.91 | $228.99 | $263.95 | 3🔴/2🟢 | plan retired |
| OPEN | $1.18 | -7.09% | 24.8 | 1.00x | $1.48 | $1.97 | $2.85 | 3🔴/2🟢 | — |
| ACMR | $40.34 | -10.69% | 45.6 | 0.90x | $45.86 | $58.81 | $69.95 | 3🔴/2🟢 | 🔴 WAIT |
| AMKR | $31.81 | -8.62% | 43.9 | 0.63x | $35.58 | $43.21 | $49.33 | 3🔴/2🟢 | — |
| CRWV | $42.60 | -11.85% | 45.0 | 0.85x | $50.65 | $66.53 | $75.99 | 4🔴/1🟢 | 🔴 WAIT |
| WTM | $2210.60 | +0.10% | 22.8 | 0.90x | $2254.18 | $2156.73 | $2145.46 | 2🔴/3🟢 | — |
| ITRN | $45.01 | -3.37% | 28.5 | 1.41x | $49.39 | $50.66 | $52.10 | 3🔴/2🟢 | — |
| NVDA | $155.38 | -5.86% | 34.4 | 1.13x | $175.78 | $204.95 | $209.09 | 4🔴/1🟢 | — |

_Prompt still names ZS and AMZN as held; the desk is actually **flat** (AMZN stopped 20 Nov). The monitor POSITIONS dict is the authority — no new entry on either name._

## 📍 Entry Verdicts & Levels (new entries only)

| Ticker | Verdict | Regime | Entry Zone | Stop | TP | Trigger / Notes |
|---|---|---|---|---|---|---|
| VSXY | 🟡 WAIT — conditional | PULLBACK inside a larger markdown | Buy-stop $97.61–98.10 (above 24 Nov high $97.55) | $91.20–91.85 (below 24 Nov low $91.92) | $104.26 HVN / $108.45 / $115.35 | Trigger **NOT PRINTED** — close 93.38, 4.5% below the trigger. Confluence composite **+0.01** vs ±0.50 gate → fails. Earnings 3 Dec.

Monitor-generated WAITs on the watchlist (context, not new entries): GDDY $102.28 (RSI 25.2, broken below SMA50), ACMR $40.34 (needs close > SMA20 $45.86), CRWV $42.60 (needs close > SMA20 $50.65). All three are knife-catches below every SMA — no market-buys.

## 🧠 3-Expert Analysis — VSXY (3 independent subagents)

**Setup under test:** $93.38 close 24 Nov · RSI-14 Wilder 29.7 (TV scanner field prints 43.3 — feed discrepancy flagged below) · SMA20 $101.95 · SMA50 $92.74 (+5.3% slope) · EMA200 $79.57 · ATR14 $6.10 (6.5%) · 20d range 91.36–116.32 · 60d range 71.72–116.32 · VPOC 74.51 / VAH 101.45 / VAL 73.58 · VWAP20 102.05 · HVNs above 94.95, below 89.37 / 87.52 / 83.80 · MACD hist -2.09 · OBV slope -0.124 · CMF +0.02 · MFI 27.3 · ROC-10 -15.7% · vol 0.87x

Recent bars (O/H/L/C/V): 17 Nov 102.66/104.90/97.91/98.70/1.33M · 18 Nov 97.87/104.15/97.69/101.30/1.18M · 19 Nov 100.13/102.20/95.89/96.47/1.22M · 20 Nov 95.69/98.18/92.46/94.57/1.52M · 23 Nov 97.20/97.99/92.93/94.21/1.42M · 24 Nov 92.63/97.55/91.92/93.38/1.25M

### VSXY | Entry $97.61–98.10 (buy-stop) | Stop $91.20–91.85 | TP1 $104.26–108.45 | TP2 $115.35 | R:R 1.15–1.5R | Trigger: **NOT PRINTED** — last close 93.38, no SOS bar, no reclaim of 97.55

| Expert | Verdict | Conf | Action |
|---|---|---|---|
| Thorp edge eval | **15/40 — NO BET** (below the 25 execute line) | High | Stand down. Generic mean reversion, no structural edge, zero sample on this setup, no forward test. Reconsider only on a close above SMA20 with composite > +2. |
| Wyckoff 2.0 | **Phase 4 markdown — WAIT** | High | 9 Nov climax at 116.32, AR 11/12 at 103.57, SOW 16 Nov, LPSY 18 Nov, 24 Nov lower low 91.92 closing in the bottom quarter on no demand = no-demand test, not a spring. Preferred long is a spring into 88.3/86.3 (VPOC/VAL), buy-stop above that bar high. |
| Medallion pattern | **14/40 — NO BUY** | Medium | No setup was specified to condition on, so any base rate would be fabricated. Unconditional mid-cap specialty-retail prior ≈ +0.3%/52% (5d), +0.7%/53% (10d), +1.2%/53% (20d). One name, ~4.3y history, earnings 4x/yr → n too small, survivorship biased, does not survive costs at 5d. |

**Consensus: 0 of 3 BET — WAIT / no entry today.** Direction (if it ever triggers): long only, mean-reversion off the rising SMA50, size cap 14 sh / $1,373 notional at a $91.20 stop = $96.60 risk (0.90%). Invalidation for the whole idea: daily close below $86.29 on rising volume. Catalyst risk: **Q3 FY2026 earnings Thu 3 Dec, 8 calendar days out** — do not open a short-leash mean-reversion long into a print. Do-NOT: no market-buy, no entry below 97.55, no averaging down under 91.36. Budget used today: $0 of $2,500.

**Data-integrity notes:** (1) RSI disagreement — TV scanner field 43.3 vs Wilder-14 on the same closes 29.7; both feeds return identical OHLCV, so the raw series is trustworthy and the scanner field is the suspect. (2) Two experts flagged VSXY as an unknown symbol; resolved — it is the post-rename NYSE ticker for Victoria's Secret (VSCO → VSXY, 2 Jun 2026), verified by live quote $93.49 and matching bars. (3) Expert 2 pulled a 501-bar profile giving VPOC 88.34 / VAL 86.29 / VAH 102.72 / SMA200 73.38, which supersedes my 60-day window (VPOC 74.51) for near-term levels — the spring zone is 86–88, not 74.

## 🚨 Active Positions — informational only (owned by 906420a9f2e2)

| Ticker | Price | Entry | P&L | Regime | RSI | ATR | Monitor flag |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | **Book flat: 0 open positions, 0 exit signals** |

No recommendations here. Any future exit flag is recorded as informational only and belongs to the 04:30 position review.

## 📈 Journey Snapshot

| Account | Capital | Deployed | Total | Today | Target |
|---|---|---|---|---|---|
| Journey (paper) | $9,583.97 | $466.92 (5/5) | $10,050.89 🟢 +0.51% | $0.00 | $100/day (51%) |

| Ticker | Entry→ | R | Days | Status |
|---|---|---|---|---|
| ARKW | $154.06→$151.38 | -0.4R | 4 | open |
| HUBS | $240.51→$239.86 | -0.0R | 4 | open |
| ZM | $109.84→$106.30 | -0.5R | 4 | open |
| DXC | $14.98→$14.26 | -0.4R | 17 | open |
| ALKS | $49.95→$49.95 | +0.0R | 0 | new today |

Stats: 8 trades (W4/L4, 50% WR) · total +0.56R, avg +0.07R · P&L +$50.88 · PF 1.14 · max DD 1.7% · VIX 27.0

## 📋 SUMMARY — All Entry Points

| Ticker | Side | Entry | Stop | TP1 | TP2 | R:R | Trigger State | Expert Consensus | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|---|
| VSXY | Long | $97.61 buy-stop | $91.20 | $104.26 | $108.45 | 1.15R | **NOT PRINTED** (close 93.38) | 0/3 BET — 15/40 · WAIT · 14/40 | $0 used, $1,373 reserved if triggered |

## 🏁 Final Results (3-expert consensus on the day's best entry)

| Ticker | Best Call | Direction | Size | Entry | Stop | TP | R:R | Expert Consensus | Invalidation | Catalyst risk | Budget $2,500 |
|---|---|---|---|---|---|---|---|---|---|---|
| VSXY | 🟡 **WAIT — do not enter** | Long | 14 sh max ($1,373 notional, $96.60 risk = 0.90%) | $97.61 buy-stop (Thorp: $98.10) | $91.20 (Wyckoff: $91.85) | $104.26 HVN → $108.45 → $115.35 | 1.15R at first supply, 1.5R to Thorp TP1 | 0/3 BET | Daily close < $86.29 on rising volume | Q3 earnings Thu 3 Dec 2026 (8 days) | $0 deployed today |

**Bottom line:** One scan qualifier, and all three frameworks reject it for entry today. VSXY is a mid-markdown no-demand test on the rising SMA50, 4.5% below its own buy-stop, with an earnings print inside 8 days. Score 7.25 on the scanner is not an entry — it is a watch level. The higher-quality long, per Wyckoff, is a spring into $86–88 with a stop below that bar. Desk stays flat, $2,500 new-entry budget untouched.

