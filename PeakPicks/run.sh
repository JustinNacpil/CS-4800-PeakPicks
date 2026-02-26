#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/peakpicks"
APP_FILE="peakpicks_app.py"
PY="$APP_DIR/.venv/bin/python"

cd "$APP_DIR"

# Pull latest code
git fetch --all
git reset --hard origin/main

# Ensure venv exists
if [ ! -d ".venv" ]; then
  python3.12 -m venv .venv
fi

"$PY" -m pip install -U pip
"$PY" -m pip install -r requirements.txt

# Stop previous process (match exact command)
pkill -f "$PY $APP_FILE" || true

# Start new process
nohup "$PY" "$APP_FILE" > log.txt 2>&1 &
echo "Started PeakPicks. Tail logs with: tail -n 200 -f $APP_DIR/log.txt"
