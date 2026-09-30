#!/bin/bash
# Runs a program on the hub over Bluetooth and saves all output and errors
# to logs/hub-run.log (overwritten each run) for easier troubleshooting.
#
# Usage: scripts/run-hub.sh ["Hub Name"] [file.py]
#   defaults: "Lucky Chicken" robot.py

cd "$(dirname "$0")/.." || exit 1

HUB_NAME="${1:-Lucky Chicken}"
PROGRAM="${2:-robot.py}"
LOG_FILE="logs/hub-run.log"

mkdir -p logs
{
    echo "=== $(date) | hub: $HUB_NAME | program: $PROGRAM ==="
    PYTHONUNBUFFERED=1 .venv/bin/python -m pybricksdev run ble --name "$HUB_NAME" "$PROGRAM" 2>&1
    echo "=== exit code: $? ==="
} | tee "$LOG_FILE"
