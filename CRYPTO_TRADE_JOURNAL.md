# 📓 Tay's Crypto Trading Journal

**Account:** Hyperliquid perps (USDC) | **Currency:** USDC
**Started:** 2026-08-25 | **Separate from stock journal** (Dime/IBKR)

---

## 🟢 Open Positions

| Ticker | Market | Entry | Qty | SL | TP1 | TP2 | TP3 | Status |
|--------|--------|-------|-----|-----|-----|-----|-----|--------|
| HYPE | HYPE/USDC perp | $80.80 (25 Aug) | **0.9825** (~$79.39) | $75.44 | $84.82 ✅ | $87.50 | $90.18 | 🟢 Profit run (25% runner) |

**Runner note:** 50% sold @ TP1 ($84.82), 50% of remainder sold @ TP2 ($85.55) on Aug 28. Remaining 0.9825 HYPE rides for TP3 / trail.

**Entry reason (HYPE):** UPTREND pullback confirmed — 4h close $80.88 > $80.20 + green candle, CMF 0.220, ROC +1.48%

---

## 📈 Closed Trades

| Ticker | Entry | Exit | Qty | Realized P&L | % | Notes |
|--------|-------|------|-----|--------------|---|-------|
| HYPE | $80.80 (25 Aug) | TP1: 1.965 @ $84.82 + TP2: 0.9825 @ $85.55 (28 Aug) | 2.9475 | **+$12.57** | **+5.28%** | Scale-out 50% + 50% of remainder |

---

## 🎯 System Rules (crypto)

- Stop loss: 2× ATR(14)
- TP1 = 1.5R, TP2 = 2.5R, TP3 = 3.5R — **recalculate from ACTUAL fill price, never reuse plan levels**
- Scale-out convention: 50% of position at TP1, then 50% of *remainder* at TP2 — the rest runs
- Entry: Wyckoff stop-order — buy-stop above trigger candle high
- Confirmation required: green close above swing high OR CMF > 0.15 + ROC positive
- Watchdog: `watch_hype.py` tracks position, alerts TP/SL

---

*Journal file: `crypto_trade_journal.json` — update on each crypto trade*
