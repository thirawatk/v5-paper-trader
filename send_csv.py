#!/usr/bin/env python3
import subprocess, json

token = None
with open("/root/.hermes/profiles/trader/.env") as f:
    for line in f:
        line = line.strip()
        if line.startswith("TELEGRAM") and "BOT_TOKEN" in line and "=" in line:
            token = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

files = [
    ("/root/.hermes/profiles/trader/scripts/backtest_stage2_confirmed.csv",
     "Stage 2 Confirmed - 38 signals, 97% WR, +16.08% avg 20d"),
    ("/root/.hermes/profiles/trader/scripts/backtest_stage2_missed.csv",
     "Stage 2 Missed - 272 signals, 63% WR, +5.98% avg 20d"),
]

for path, caption in files:
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.telegram.org/bot{token}/sendDocument",
        "-F", "chat_id=2135517501",
        "-F", f"document=@{path}",
        "-F", f"caption={caption}"
    ], capture_output=True, text=True)
    print(f"{caption}: {'Sent' if json.loads(r.stdout).get('ok') else r.stdout}")
