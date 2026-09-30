import json, urllib.request, datetime, statistics
url = "https://query1.finance.yahoo.com/v8/finance/chart/GOOG?range=6mo&interval=1d"
req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
d = json.load(urllib.request.urlopen(req, timeout=30))
r = d["chart"]["result"][0]
ts = r["timestamp"]
q = r["indicators"]["quote"][0]
rows = []
for i,t in enumerate(ts):
    if q["close"][i] is None: continue
    rows.append({"d": datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"),
                 "o":q["open"][i],"h":q["high"][i],"l":q["low"][i],"c":q["close"][i],"v":q["volume"][i]})
print("LAST10")
for x in rows[-10:]:
    print({k:(round(v,2) if isinstance(v,float) else v) for k,v in x.items()})
closes=[x["c"] for x in rows]
vols=[x["v"] for x in rows]
print("last close", round(closes[-1],2), "5d chg %", round((closes[-1]/closes[-6]-1)*100,2))
print("20d chg %", round((closes[-1]/closes[-21]-1)*100,2))
print("vol5 avg", sum(vols[-5:])/5, "vol20 avg", sum(vols[-20:])/20)
print("10d high", round(max(x["h"] for x in rows[-10:]),2), "10d low", round(min(x["l"] for x in rows[-10:]),2))
print("6mo high", round(max(x["h"] for x in rows),2), "6mo low", round(min(x["l"] for x in rows),2))
ups = sum(1 for i in range(1,len(closes)) if closes[i]>closes[i-1])
print("up day freq", round(ups/(len(closes)-1),3))
rets=[(closes[i]/closes[i-1]-1) for i in range(1,len(closes))]
print("daily vol %", round(statistics.pstdev(rets)*100,2))
# SMA checks
import statistics as st
sma20=st.mean(closes[-20:]); sma50=st.mean(closes[-50:])
print("sma20", round(sma20,2), "sma50", round(sma50,2))
# simple range position
h6=max(x["h"] for x in rows); l6=min(x["l"] for x in rows)
print("range pos", round((closes[-1]-l6)/(h6-l6),3))
# distribution of last 20: higher lows count
hl=sum(1 for i in range(-20,-1) if rows[i]["l"]>rows[i-1]["l"])
print("higher lows in last 20", hl)
