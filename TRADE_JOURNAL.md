# 📓 Tay's Real Trading Journal

**Account:** Dime/IBKR (real money) | **Currency:** USD
**Started tracking:** Aug 2026 | **Last updated:** 2026-08-20

---

## 📈 Closed Trades

| # | Ticker | Entry | Exit | Qty | P&L $ | P&L % | Days | Exit Reason |
|---|--------|-------|------|-----|-------|-------|------|-------------|
| 1 | PTC | $129.50 | $152.64 | ~2.29 | +$53.13 | +17.9% | 9 | 3M high resistance, TP2 passed |
| 2 | S | $18.00 | $21.10 | 100 | +$310.00 | +17.2% | — | Overbought (RSI 86), TP2 passed |

**Realized: +$363.13** | Win rate: 2/2 (100%) | Avg return: +17.6%

---

## 🟢 Open Positions

| Ticker | Entry | Qty | Cost | Status |
|--------|-------|-----|------|--------|
| NVDU | $90.00 | 27 | $2,430.00 | 📈 Trailing stop (~$120), letting profits run |
| ZS | $150.00 | 15 | $2,250.00 | ⚠️ TP2 hit, RSI 81 overbought — partial candidate |

**Open at cost:** $4,680.00
**Unrealized (at logging):** NVDU ~+53%, ZS ~+17% → **~+$1,668**

---

## 🎯 System Rules Used

- Stop loss: 2× ATR(14) from entry
- TP1 = 1.5R, TP2 = momentum-scaled 2–3R, TP3 = 3.5R
- Trailing mode after TP3 with strong momentum (trail 2× ATR below price)
- SL tightens to 1.5× ATR when RSI >85 / Stoch >90

## 📝 Lessons / Notes

- PTC & S both exited on overbought signals near resistance — worked well
- NVDU trailing approach: don't cap 10-baggers, trail instead
- Monitor script: `monitor_entries.py` POSITIONS dict tracks live exits automatically

---
*Journal file: `trade_journal.json` — update via QuantTrader on each trade*
