import json, urllib.request, statistics
def fetch(tkr, rng="6mo"):
    url=f"https://query1.finance.yahoo.com/v8/finance/chart/{tkr}?range={rng}&interval=1d"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64)"})
    d=json.loads(urllib.request.urlopen(req, timeout=20).read())
    r=d["chart"]["result"][0]
    ts=r["timestamp"]; q=r["indicators"]["quote"][0]
    rows=[(t,q["open"][i],q["high"][i],q["low"][i],q["close"][i],q["volume"][i])
          for i,t in enumerate(ts) if q["close"][i] is not None]
    return rows
for t in ["CRM","GOOG","GEV"]:
    try:
        rows=fetch(t)
    except Exception as e:
        print(t,"ERR",e); continue
    closes=[r[4] for r in rows]; highs=[r[2] for r in rows]; lows=[r[3] for r in rows]
    vols=[r[5] or 0 for r in rows]
    last=closes[-1]
    hi6=max(highs); lo6=min(lows)
    # volume profile: 60 bins between lo6 and hi6
    lo,hi=lo6,hi6
    nb=60; w=(hi-lo)/nb
    prof=[0.0]*nb
    for h,l,v in zip(highs,lows,vols):
        a=max(0,min(nb-1,int((l-lo)/w))); b=max(0,min(nb-1,int((h-lo)/w)))
        for i in range(a,b+1): prof[i]+=v/(b-a+1)
    vpoc_i=max(range(nb), key=lambda i:prof[i])
    vpoc=lo+(vpoc_i+0.5)*w
    tot=sum(prof); cum=0; va_lo=vpoc_i; va_hi=vpoc_i
    target=tot*0.70
    # expand around vpoc
    while cum<target:
        up=prof[va_hi+1] if va_hi+1<nb else -1
        dn=prof[va_lo-1] if va_lo-1>=0 else -1
        if up>=dn and up>=0: va_hi+=1; cum+=prof[va_hi]
        elif dn>=0: va_lo-=1; cum+=prof[va_lo]
        else: break
    val=lo+(va_lo+0.5)*w; vah=lo+(va_hi+0.5)*w
    # swing structure last 60 bars
    def swings(pr,k=5):
        s=[]
        for i in range(k,len(pr)-k):
            if pr[i]==max(pr[i-k:i+k+1]): s.append(("H",i,pr[i]))
            elif pr[i]==min(pr[i-k:i+k+1]): s.append(("L",i,pr[i]))
        return s
    sw=swings(closes)[-6:]
    # last 30d high/low
    h30=max(highs[-30:]); l30=min(lows[-30:])
    # avg vol last 10 vs 30
    av10=statistics.mean(vols[-10:]); av30=statistics.mean(vols[-30:])
    print(f"== {t} last={last:.2f} 6moHi={hi6:.2f} 6moLo={lo6:.2f} fromHi={(last/hi6-1)*100:.1f}% 30dHi={h30:.2f} 30dLo={l30:.2f}")
    print(f"   VPOC={vpoc:.2f} VAH={vah:.2f} VAL={val:.2f} | price vs VPOC {(last/vpoc-1)*100:+.1f}%")
    print(f"   vol10/vol30={av10/av30:.2f} lastVol={vols[-1]}")
    print("   swings:", ", ".join(f"{k}@{v:.2f}" for k,i,v in sw))
    print(f"   last5 closes: {[round(c,2) for c in closes[-5:]]}")
    print(f"   last5 ranges: {[(round(h,2),round(l,2)) for _,_,h,l,_,_ in rows[-5:]]}")
