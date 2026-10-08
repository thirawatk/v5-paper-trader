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
| AMZN | $259.55 | 10 | $2,595.55 | 🆕 Entered Oct 7 — SL $249.33 (2×ATR) · TP1 $274.88 · TP2 $285.10 · TP3 $295.32 |

**Open at cost:** $4,845.55
**NVDU proceeds (cash):** $4,333.21 = $2,284.80 (trim) + $2,048.41 (final exit)

---

## 🗓️ Planned Trades

### MKSI — Swing Plan (normal plan, revised Oct 7 2026 from 1–2yr version)

| Step | Rule |
|---|---|
| Entry | **ONE entry, full size** — Zone A: pullback **$255–274** (fib 38.2% $261 / SMA50 $274) · Zone B: daily close **>$311** on volume. **Never lump at $281** |
| Stop | **2× ATR(14) = $19.78** below actual fill (Wyckoff candle-low floor). Example @ $265 → SL **$245** |
| TP1 | **1.5R** from actual fill → trim ½ (example @ $265: **$295**) |
| TP2 | **2.5R** from actual fill → trim ½ (example @ $265: **$314** ≈ SMA100) |
| Runner | Trail 2× ATR · exit on RSI>85 / Stoch>90 overbought |
| Time stop | 2–4 wks without TP1 → exit, recycle |
| Sizing | risk$ ÷ $19.78 (1% account risk) · gate must pass ≥ +0.50 |

- **🛑 Kill: SL hit → full exit, no averaging** (old weekly <$228.46 invalidation retired)
- Funding: NVDU total $4,333.21 + ZS exit proceeds · remainder in SMH/SOXX
- Supersedes: 1–2yr staged plan (3 tranches, $380/$447 targets) → `mksi_longterm_report.md` still valid for entry zones
- Log: `trade_journal.json → planned_trades[0]` (MKSI-SW-1)

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
