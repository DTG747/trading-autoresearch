#!/bin/bash
# Overnight AutoResearch Runner
# Runs 150 iterations (~6-8 hours). Logs to overnight.log.
# Usage: bash run_overnight.sh

export PATH="/opt/homebrew/opt/node@22/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

LOGFILE="/tmp/trading-autoresearch/overnight.log"
cd /tmp/trading-autoresearch

echo "============================================" | tee -a "$LOGFILE"
echo "Overnight run started: $(date)" | tee -a "$LOGFILE"
echo "Max iterations: 150" | tee -a "$LOGFILE"
echo "============================================" | tee -a "$LOGFILE"

python3 runner.py --max-iters 150 2>&1 | tee -a "$LOGFILE"

echo "============================================" | tee -a "$LOGFILE"
echo "Overnight run finished: $(date)" | tee -a "$LOGFILE"
echo "============================================" | tee -a "$LOGFILE"

# Notify when done
/opt/homebrew/bin/openclaw system event --text "AutoResearch overnight run complete — check Strategy Lab on MTOI" --mode now
