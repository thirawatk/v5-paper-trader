import sys
sys.path.insert(0, "/root/.hermes/profiles/trader/scripts")
from tvDatafeed import Interval
print([m for m in dir(Interval) if not m.startswith("_")])
