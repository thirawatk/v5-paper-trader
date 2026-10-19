#!/bin/bash
# V5 paper trader cron wrapper — quiet mode: silent unless exits/entries happen
# Oct 2026: pin interpreter to hermes-agent venv (py3.11) — the post-update tool venv
# (bare python3 on PATH) lost numpy/pandas/yfinance and broke every run with exit 1.
cd /root/.hermes/profiles/trader/scripts
exec /usr/local/lib/hermes-agent/venv/bin/python3 v5_paper_trader.py --quiet 2>>/root/.hermes/profiles/trader/scripts/v5_cron.err