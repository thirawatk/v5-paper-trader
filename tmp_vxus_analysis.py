import yfinance as yf
import pandas as pd
import numpy as np

ticker = yf.Ticker("VXUS")
hist = ticker.history(period="1y")

# Recent data
last = hist.iloc[-1]
print(f"=== VXUS Current Data ===")
print(f"Price: ${last['Close']:.2f}")
print(f"Volume: {last['Volume']:,.0f}")
print(f"ATR (14): ${hist['High'].subtract(hist['Low']).rolling(14).mean().iloc[-1]:.2f}")

# RSI
delta = hist['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs))
print(f"RSI(14): {rsi.iloc[-1]:.1f}")

# Moving averages
for period in [20, 50, 100, 200]:
    sma = hist['Close'].rolling(period).mean().iloc[-1]
    print(f"SMA{period}: ${sma:.2f} (price {'above' if last['Close'] > sma else 'below'})")

# 52-week high/low
high52 = hist['High'].max()
low52 = hist['Low'].min()
print(f"52w High: ${high52:.2f}")
print(f"52w Low: ${low52:.2f}")
print(f"From High: {((last['Close']/high52)-1)*100:.1f}%")
print(f"From Low: {((last['Close']/low52)-1)*100:.1f}%")

# Volume Profile (simplified - using VWAP)
vwap = (hist['Volume'] * (hist['High'] + hist['Low'] + hist['Close']) / 3).sum() / hist['Volume'].sum()
print(f"1Y VWAP: ${vwap:.2f}")

# Volume profile zones
price_bins = pd.cut(hist['Close'], bins=30)
vol_profile = hist.groupby(price_bins)['Volume'].sum().sort_values(ascending=False)
vpoc = vol_profile.index[0]
print(f"Volume POC (simplified): ~${vpoc.mid:.2f}")

# Recent trend
print(f"\n=== Recent Price Action ===")
for i in range(-5, 0):
    d = hist.index[i].strftime('%m/%d')
    c = hist['Close'].iloc[i]
    h = hist['High'].iloc[i]
    l = hist['Low'].iloc[i]
    v = hist['Volume'].iloc[i]
    print(f"{d}: O=${hist['Open'].iloc[i]:.2f} H=${h:.2f} L=${l:.2f} C=${c:.2f} V={v:,.0f}")

# Volume analysis
avg_vol = hist['Volume'].rolling(20).mean().iloc[-1]
print(f"\nAvg Volume (20d): {avg_vol:,.0f}")
print(f"Last Volume: {last['Volume']:,.0f}")
print(f"Vol Ratio: {last['Volume']/avg_vol:.2f}x")

# Drawdown from peak
peak = hist['Close'].cummax()
drawdown = ((hist['Close'] - peak) / peak) * 100
print(f"Max Drawdown: {drawdown.min():.1f}%")
print(f"Current Drawdown: {drawdown.iloc[-1]:.1f}%")

# Trend analysis
sma20 = hist['Close'].rolling(20).mean()
sma50 = hist['Close'].rolling(50).mean()
sma200 = hist['Close'].rolling(200).mean()
print(f"\n=== Trend Context ===")
print(f"Price vs SMA20: {'Above' if last['Close'] > sma20.iloc[-1] else 'Below'} ({((last['Close']/sma20.iloc[-1])-1)*100:.1f}%)")
print(f"Price vs SMA50: {'Above' if last['Close'] > sma50.iloc[-1] else 'Below'} ({((last['Close']/sma50.iloc[-1])-1)*100:.1f}%)")
print(f"Price vs SMA200: {'Above' if last['Close'] > sma200.iloc[-1] else 'Below'} ({((last['Close']/sma200.iloc[-1])-1)*100:.1f}%)")
print(f"SMA50 vs SMA200: {'Golden Cross' if sma50.iloc[-1] > sma200.iloc[-1] else 'Death Cross'}")

# Volatility
returns = hist['Close'].pct_change().dropna()
print(f"\n=== Volatility ===")
print(f"Daily Vol (20d): {returns.tail(20).std()*100:.2f}%")
print(f"Annual Vol: {returns.std()*np.sqrt(252)*100:.1f}%")

# Pullback analysis
print(f"\n=== Pullback Depth Analysis ===")
# Recent pullback from local high
recent_high_idx = hist['Close'].iloc[-30:].idxmax()
recent_high = hist['Close'].loc[recent_high_idx]
pullback_pct = ((last['Close'] / recent_high) - 1) * 100
print(f"Recent 30d High: ${recent_high:.2f} (on {recent_high_idx.strftime('%m/%d')})")
print(f"Pullback from recent high: {pullback_pct:.1f}%")

# How often does VXUS pull back this much?
drawdowns = []
for i in range(len(hist)):
    if i >= 20:
        window = hist['Close'].iloc[i-20:i]
        local_high = window.max()
        dd = ((hist['Close'].iloc[i] / local_high) - 1) * 100
        drawdowns.append(dd)

drawdowns = pd.Series(drawdowns)
print(f"\nHistorical pullback distribution (20d rolling):")
for pct in [-2, -3, -5, -8, -10]:
    freq = (drawdowns <= pct).mean() * 100
    print(f"  <= {pct}%: {freq:.1f}% of the time")
