#!/bin/bash
# V5 paper trader cron wrapper — quiet mode: silent unless exits/entries happen
cd /root/.hermes/profiles/trader/scripts
exec python3 v5_paper_trader.py --quiet 2>/dev/null