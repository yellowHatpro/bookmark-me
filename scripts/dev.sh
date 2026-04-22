#!/usr/bin/env bash
# Start db + backend (uvicorn --reload) + frontend (pnpm dev) together.
# Ctrl-C stops api + ui; Postgres keeps running in the background (compose).
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "error: .env not found. Run ./scripts/setup.sh first." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

echo "==> Starting Postgres"
docker compose up -d db >/dev/null

echo "==> Starting backend on :8000"
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

echo "==> Starting frontend on :3000"
(cd ui && pnpm dev -p 3000) &
UI_PID=$!

cleanup() {
  echo
  echo "==> Shutting down"
  kill "$API_PID" "$UI_PID" 2>/dev/null || true
  wait "$API_PID" "$UI_PID" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

wait
