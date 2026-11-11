"""Breadth + watchlist scoring for the 12 Nov 2026 daily entry report."""
import json
from daily_market_scan import fetch_market_rows, load_universe, COLS

WATCH = ["GOOG", "RDDT", "GDDY", "NVDU", "ZS", "BCC", "FBK", "AMZN", "MRVL",
         "GEV", "MKSI", "OPEN", "ACMR", "AMKR", "CRWV", "WTM", "ITRN"]


def regime_of(price, sma20, sma50, sma200):
    if price > sma20 and sma20 >= sma50 and price > sma200:
        return "UPTREND"
    if sma50 <= price <= sma20 and price > sma200:
        return "PULLBACK"
    if price < sma20 and price >= sma50:
        return "PULLBACK"
    if price < sma50 and price < sma20 and price < sma200:
        return "DOWNTREND"
    return "MIXED"


def main():
    universe = set(load_universe())
    rows = fetch_market_rows()
    stats = dict(rows=len(rows), matched=0, usable=0, above200=0, above20=0,
                 above50=0, rsi45=0, rsi45_above200=0, rsi45_at_sma50=0,
                 rsi35=0, rsi45_uptrend=0, rsi45_pullback=0, rsi45_down=0, rsi45_mixed=0)
    watch_out, deep_weak = [], []
    for row in rows:
        d = row.get("d")
        if not d or len(d) < len(COLS):
            continue
        r = dict(zip(COLS, d))
        if r["name"] not in universe:
            continue
        stats["matched"] += 1
        need = ("close", "rsi", "sma20", "sma50", "sma200")
        if any(r.get(k) is None for k in need) or r["close"] is None or r["close"] <= 1:
            continue
        stats["usable"] += 1
        price, rsi = r["close"], r["rsi"]
        sma20, sma50, sma200 = r["sma20"], r["sma50"], r["sma200"]
        if price > sma200: stats["above200"] += 1
        if price > sma20: stats["above20"] += 1
        if price >= sma50: stats["above50"] += 1
        if rsi < 35: stats["rsi35"] += 1
        if rsi < 45:
            stats["rsi45"] += 1
            if price > sma200: stats["rsi45_above200"] += 1
            if price >= sma50: stats["rsi45_at_sma50"] += 1
            reg = regime_of(price, sma20, sma50, sma200)
            stats["rsi45_" + reg.lower()[:8]] = stats.get("rsi45_" + reg.lower()[:8], 0) + 1
            deep_weak.append((r["name"], round(rsi, 1), reg,
                              round((price / sma50 - 1) * 100, 1)))
        if r["name"] in WATCH:
            hist = (r["macd"] - r["macd_sig"]) if r.get("macd") is not None and r.get("macd_sig") is not None else None
            watch_out.append(dict(
                ticker=r["name"], price=round(price, 2),
                rsi=round(rsi, 1), stoch=round(r["stoch"], 1) if r.get("stoch") is not None else None,
                regime=regime_of(price, sma20, sma50, sma200),
                sma20=round(sma20, 2), sma50=round(sma50, 2), sma200=round(sma200, 2),
                atr=round(r["atr"], 2) if r.get("atr") else None,
                vol_ratio=round(r["vol"] / r["avgvol"], 2) if r.get("avgvol") else None,
                macd_hist=round(hist, 3) if hist is not None else None,
                cmf=round(r["cmf"], 3) if r.get("cmf") is not None else None,
                from_3m_high=round((price / r["high3m"] - 1) * 100, 1) if r.get("high3m") else None,
                vs_sma20=round((price / sma20 - 1) * 100, 1),
                vs_sma50=round((price / sma50 - 1) * 100, 1),
                mcap_m=round(r["mcap"] / 1e6) if r.get("mcap") else None,
            ))
    deep_weak.sort(key=lambda x: x[1])
    json.dump(dict(stats=stats, watch=watch_out,
                          deepest=deep_weak[:12]), open("/root/.hermes/profiles/trader/cache/scratch/breadth_1112.json","w"), indent=1)


main()
