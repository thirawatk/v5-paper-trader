import json, urllib.request, datetime, collections

def fetch(sym, rng='1y', interval='1d'):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval={interval}"
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    r = d['chart']['result'][0]
    ts = r['timestamp']; q = r['indicators']['quote'][0]
    rows=[]
    for i,t in enumerate(ts):
        c=q['close'][i]
        if c is None: continue
        rows.append(dict(d=datetime.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d'),c=c,h=q['high'][i],l=q['low'][i],v=q['volume'][i],o=q['open'][i]))
    return rows

for sym in ['GEV','NVDU','ZS']:
    try:
        rows=fetch(sym)
    except Exception as e:
        print(sym,"ERR",e); continue
    closes=[r['c'] for r in rows]; vols=[r['v'] for r in rows]
    highs=[r['h'] for r in rows]; lows=[r['l'] for r in rows]
    def rsi(cs,n=14):
        gains=[];losses=[]
        for i in range(1,len(cs)):
            ch=cs[i]-cs[i-1]; gains.append(max(ch,0)); losses.append(max(-ch,0))
        ag=sum(gains[:n])/n; al=sum(losses[:n])/n
        for i in range(n,len(gains)):
            ag=(ag*(n-1)+gains[i])/n; al=(al*(n-1)+losses[i])/n
        return 100 if al==0 else 100-100/(1+ag/al)
    print("="*50)
    print(sym, "bars:",len(rows), rows[-1]['d'], "close", round(closes[-1],2))
    print("RSI14:", round(rsi(closes),1))
    for n in (20,50,100,200):
        if len(closes)>=n: print(f"  SMA{n}: {sum(closes[-n:])/n:.2f}")
    print("  52w high:", round(max(highs[-252:]),2), "low:", round(min(lows[-252:]),2))
    print("  3M high:", round(max(highs[-63:]),2), "3M low:", round(min(lows[-63:]),2))
    av20=sum(vols[-20:])/20
    print("  vol ratio:", round(vols[-1]/av20,2) if av20 else 'n/a')
    print("  last 8 bars:")
    for r in rows[-8:]:
        print("   ", r['d'], "c",round(r['c'],2),"h",round(r['h'],2),"l",round(r['l'],2),"v",r['v'])
    # volume profile last 63 bars
    bmin=min(lows[-63:]); bmax=max(highs[-63:]); step=(bmax-bmin)/25
    buckets=collections.Counter()
    for i in range(-63,0):
        mid=(highs[i]+lows[i]+closes[i])/3
        b=int((mid-bmin)/step) if step>0 else 0
        buckets[b]+=vols[i]
    top=sorted(buckets.items(), key=lambda x:-x[1])[:4]
    print("  VPOC zones (63d):")
    for b,v in top:
        print(f"    {bmin+b*step:.1f}-{bmin+(b+1)*step:.1f} vol={v}")
    # 20d momentum
    if len(closes)>20:
        print("  ROC10:", round((closes[-1]/closes[-11]-1)*100,2), "%  ROC20:", round((closes[-1]/closes[-21]-1)*100,2),"%")
