import json, sys
try:
    import yfinance as yf
except Exception as e:
    print("NO_YF", e); sys.exit(0)
tickers = ["GOOG", "GEV", "OPEN", "ZS"]
out = {}
for t in tickers:
    try:
        df = yf.download(t, period="6mo", interval="1d", progress=False, auto_adjust=True)
        if df is None or len(df) == 0:
            out[t] = "EMPTY"
            continue
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        rec = {
            "last_close": round(float(df['Close'].iloc[-1]), 2),
            "last_date": str(df.index[-1]),
            "vol_ratio": round(float(df['Volume'].iloc[-1] / df['Volume'].iloc[-20:].mean()), 2),
            "ret_5d": round(float(df['Close'].iloc[-1] / df['Close'].iloc[-6] - 1), 4),
            "ret_20d": round(float(df['Close'].iloc[-1] / df['Close'].iloc[-21] - 1), 4),
            "high_6mo": round(float(df['Close'].max()), 2),
            "low_6mo": round(float(df['Close'].min()), 2),
            "green_days_10d": int((df['Close'].diff().tail(10) > 0).sum()),
            "atr14": round(float((df['High'] - df['Low']).tail(14).mean()), 2),
            "last5": [[str(df.index[i].date()), round(float(df['Close'].iloc[i]), 2), int(df['Volume'].iloc[i])] for i in range(-5, 0)],
        }
        out[t] = rec
    except Exception as e:
        out[t] = f"ERR {e}"
print(json.dumps(out, indent=1))
