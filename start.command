#!/bin/bash
set -e

cd "$(dirname "$0")"

NODE_BIN="$(command -v node || true)"
if [ -z "$NODE_BIN" ]; then
  NODE_BIN="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
fi
if [ ! -x "$NODE_BIN" ]; then
  echo "Node.js is required to run the frontend."
  exit 1
fi
if [ ! -f frontend/node_modules/vite/bin/vite.js ]; then
  echo "Frontend dependencies are missing. Run pnpm install in frontend/ first."
  exit 1
fi

export PYTHONPATH="$(pwd)"
python3 -m backend.api > backend.log 2>&1 &
BACKEND_PID=$!
cleanup() { kill "$BACKEND_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

cd frontend
"$NODE_BIN" node_modules/vite/bin/vite.js --host 127.0.0.1 &
FRONTEND_PID=$!
sleep 2
open "http://127.0.0.1:5173"
wait "$FRONTEND_PID"
