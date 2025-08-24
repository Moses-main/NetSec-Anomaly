#!/usr/bin/env bash
set -euo pipefail

# Quiet TensorFlow INFO logs
export TF_CPP_MIN_LOG_LEVEL=2

# Use virtualenv if available
if [ -d "venv" ]; then
  # shellcheck disable=SC1091
  source "venv/bin/activate"
fi

# Generate results if not present
if [ ! -f "results/detection_report.json" ]; then
  echo "[start.sh] Generating results..."
  python src/main.py --mode full
fi

# Start backend
echo "[start.sh] Starting backend (Flask) on http://127.0.0.1:5000"
python src/server.py &
BACK_PID=$!

echo "[start.sh] Backend PID: ${BACK_PID}"
trap 'echo "[start.sh] Stopping backend (${BACK_PID})"; kill ${BACK_PID} 2>/dev/null || true' EXIT INT TERM

# Start frontend
echo "[start.sh] Starting frontend (Vite) on http://127.0.0.1:5173"
(
  cd frontend
  npm install
  npm run dev
)
