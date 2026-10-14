import importlib.util, sys, datetime
spec = importlib.util.spec_from_file_location("me", "/root/.hermes/profiles/trader/scripts/monitor_entries.py")
me = importlib.util.module_from_spec(spec)
sys.argv = ["me", "--probe"]
try:
    spec.loader.exec_module(me)
except SystemExit:
    pass

def show(t):
    d = me.fetch_range(t, "1mo")
    r = d["chart"]["result"][0]
    ts = r["timestamp"]
    q = r["indicators"]["quote"][0]
    rows = []
    for i, tstamp in enumerate(ts):
        c = q["close"][i]
        if c is None:
            continue
        rows.append((datetime.datetime.fromtimestamp(tstamp, datetime.timezone.utc).strftime("%Y-%m-%d"),
                     q["high"][i], q["low"][i], c, q["volume"][i]))
    print("==", t, "n=", len(rows), "last date=", rows[-1][0])
    for row in rows[-5:]:
        print("   %s H=%.2f L=%.2f C=%.2f V=%s" % row)
    vols = [r[4] for r in rows[:-1] if r[4]]
    if vols and rows[-1][4]:
        avg = sum(vols[-20:]) / len(vols[-20:])
        print("   volratio vs prior-20avg = %.2f" % (rows[-1][4] / avg))
    # 5d change
    if len(rows) >= 6:
        print("   5d close change = %+.2f%%" % ((rows[-1][3] / rows[-6][3] - 1) * 100))

for t in ["AMZN", "GOOG", "GEV", "AMKR", "MKSI", "ZS"]:
    try:
        show(t)
    except Exception as e:
        print(t, "ERR", type(e).__name__, e)
