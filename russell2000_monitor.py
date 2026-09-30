#!/usr/bin/env python3
"""
Russell 2000 Monitor — Same 2-stage logic, different universe.
Reads from russell2000_universe.txt instead of us_stocks_universe.txt.
"""

import sys
import os

# Override universe file before importing
UNIVERSE_FILE = "/root/.hermes/profiles/trader/scripts/russell2000_universe.txt"
STATE_FILE = "/root/.hermes/profiles/trader/scripts/russell2000_monitor_state.json"

# Monkey-patch the main script's config
import us_stocks_monitor as monitor
monitor.UNIVERSE_FILE = UNIVERSE_FILE
monitor.STATE_FILE = STATE_FILE

if __name__ == "__main__":
    # Inject --universe flag
    sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:]]
    monitor.main()
