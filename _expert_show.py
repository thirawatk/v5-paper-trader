import json
d = json.load(open('/root/.hermes/profiles/trader/scripts/_expert_data.json'))
for t, v in d.items():
    if 'error' in v:
        print(f"{t}: ERROR {v['error']}"); continue
    print(f"--- {t} @ {v['close']} ({v['chg1d']:+}%) asof {v['last_date']}")
    print(f"  RSI {v['rsi']} | ATR {v['atr']} ({v['atr_pct']}%) | MACDhist {v['macd_hist']} | volR {v['vol_ratio']}")
    print(f"  SMA20 {v['sma20']} | SMA50 {v['sma50']} | SMA200 {v['sma200']} | EMA200 {v['ema200']} | slope50 {v['sma50_slope_pct']}%")
    print(f"  VWAP20 {v['vwap20']} | VPOC {v['vpoc']} | VAH {v['vah']} | VAL {v['val']} | nearHVN {v['near_hvns']}")
    print(f"  20d {v['lo20']}-{v['hi20']} | 60d {v['lo60']}-{v['hi60']} | 3mHigh {v['hi3m']} ({v['from_3m_high_pct']}%) | pos60 {v['pos_in_60d_range']}%")
    for b in v['bars']:
        print(f"    {b['date']} O{b['o']} H{b['h']} L{b['l']} C{b['c']} pos{b['pos']} V{b['v']:,}")
