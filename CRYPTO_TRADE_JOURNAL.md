# 📓 Tay's Crypto Trading Journal

**Account:** Hyperliquid perps (USDC) | **Currency:** USDC
**Started:** 2026-08-25 | **Separate from stock journal** (Dime/IBKR)

---

## 🟢 Open Positions

| Ticker | Market | Entry | Qty | SL | TP1 | TP2 | TP3 | Status |
|--------|--------|-------|-----|-----|-----|-----|-----|--------|
| HYPE | HYPE/USDC perp | $80.80 (25 Aug) | **3.93** (~$317.54) | $75.44 | $84.82 | $87.50 | $90.18 | 🟢 Running |

**Entry reason:** UPTREND pullback confirmed — 4h close $80.88 > $80.20 + green candle, CMF 0.220, ROC +1.48%

---

## 📈 Closed Trades

_None yet_

---

## 🎯 System Rules (crypto)

- Stop loss: 2× ATR(14)
- TP1 = 1.5R, TP2 = 2.5R, TP3 = 3.5R
- Entry: Wyckoff stop-order — buy-stop above trigger candle high
- Confirmation required: green close above swing high OR CMF > 0.15 + ROC positive
- Watchdog: `watch_hype.py` tracks position, alerts TP/SL

---

*Journal file: `crypto_trade_journal.json` — update on each crypto trade*
