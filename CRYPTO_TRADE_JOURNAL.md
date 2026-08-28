# 📓 Tay's Crypto Trading Journal

**Account:** Hyperliquid perps (USDC) | **Currency:** USDC
**Started:** 2026-08-25 | **Separate from stock journal** (Dime/IBKR)

---

## 🟢 Open Positions

_None — flat_

---

## 📈 Closed Trades

| Ticker | Entry | Exit | Qty | Realized P&L | % | Notes |
|--------|-------|------|-----|--------------|---|-------|
| HYPE | $80.80 (25 Aug) | 50% @ $84.82 (TP1) + 50% @ $85.55 (TP2), 28 Aug | 3.93 | **+$17.23** | **+5.43%** | Both TP points exited; avg exit $85.19 |

**Exit reason:** TP1 leg (1.965) @ $84.82 + TP2 leg (1.965) @ $85.55 — executed on original plan levels (watcher config was TP2 $87.50; user exited at plan TP2).

**Entry reason (HYPE):** UPTREND pullback confirmed — 4h close $80.88 > $80.20 + green candle, CMF 0.220, ROC +1.48%

---

## 🎯 System Rules (crypto)

- Stop loss: 2× ATR(14)
- TP1 = 1.5R, TP2 = 2.5R, TP3 = 3.5R — **recalculate from ACTUAL fill price, never reuse plan levels**
- Entry: Wyckoff stop-order — buy-stop above trigger candle high
- Confirmation required: green close above swing high OR CMF > 0.15 + ROC positive
- Watchdog: `watch_hype.py` tracks position, alerts TP/SL

---

*Journal file: `crypto_trade_journal.json` — update on each crypto trade*
