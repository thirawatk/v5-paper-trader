# 📓 Tay's Real Trading Journal

**Account:** Dime/IBKR (real money) | **Currency:** USD
**Started tracking:** Aug 2026 | **Last updated:** 2026-10-07

---

## 📈 Closed Trades

| # | Ticker | Entry | Exit | Qty | P&L $ | P&L % | Days | Exit Reason |
|---|--------|-------|------|-----|-------|-------|------|-------------|
| 1 | PTC | $129.50 | $152.64 | ~2.29 | +$53.13 | +17.9% | 9 | 3M high resistance, TP2 passed |
| 2 | S | $18.00 | $21.10 | 100 | +$310.00 | +17.2% | — | Overbought (RSI 86), TP2 passed |
| 3 | NVDU | $90.00 | $163.20 | 14 | +$1,024.80 | +81.3% | — | **Partial trim** — 3-expert panel: RSI 84.5 + new 3M high w/o SOS bar |
| 4 | NVDU | $90.00 | $157.57 | 13 | +$878.41 | +75.1% | — | **Runner full exit** — manual @ $157.57 |

**Realized: +$2,266.34** | Win rate: 4/4 (100%) | Avg return: +47.9%
*NVDU lifecycle total: +$1,903.21 on $2,430 (14 sh @ $163.20 + 13 sh @ $157.57)*

---

## 🟢 Open Positions

| Ticker | Entry | Qty | Cost | Status |
|--------|-------|-----|------|--------|
| ZS | $150.00 | 15 | $2,250.00 | ⏳ 3-expert WAIT — trail $193.09 (SMA20), trim into $216.97 |

**Open at cost:** $2,250.00
**NVDU proceeds (cash):** $4,333.21 = $2,284.80 (trim) + $2,048.41 (final exit)

---

## 🗓️ Planned Trades

### MKSI — 1–2 Year Staged Entry (3-expert panel, Oct 7 2026)

| Tranche | Trigger | Qty | Cost |
|---|---|---|---|
| T1 | Anchor — market | 1 sh | ~$281 |
| T2 | Pullback **$255–274** (38.2% $261 / SMA50 $274), higher-low >$228.46 | 1 sh | ~$265 |
| T3 | Daily close **>$311** / weekly **>$322** on volume | 1 sh | ~$311 |

- **Total:** 3 sh ≈ $857 (15.5% ≈ full Kelly) · **Cap:** 4 sh (20.6%)
- **🛑 Kill switch: weekly close <$228.46 → exit all**
- Funding: NVDU total $4,333.21 + ZS exit proceeds
- Park remainder in SMH/SOXX · Report: `mksi_longterm_report.md`
- Log: `trade_journal.json → planned_trades[0]`

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
