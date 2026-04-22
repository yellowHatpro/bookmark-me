#!/usr/bin/env bash
# First-time setup:
#   - create .env (from .env.example) if missing
#   - generate APP_FERNET_KEY if empty
#   - start Postgres (compose)
#   - uv sync + alembic upgrade head
#   - pnpm install in ui/
#
# Safe to re-run: each step is a no-op if already done.
set -euo pipefail

cd "$(dirname "$0")/.."

say() { printf "\033[1;34m==>\033[0m %s\n" "$*"; }

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "error: '$1' is required on PATH" >&2
    exit 1
  }
}

need docker
need uv
need pnpm

# 1. .env
if [[ ! -f .env ]]; then
  say "Creating .env from .env.example"
  cp .env.example .env
fi

# 2. APP_FERNET_KEY
if ! grep -qE '^APP_FERNET_KEY=.+' .env; then
  say "Generating APP_FERNET_KEY"
  KEY=$(uv run --with cryptography python -c \
    'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
  # Replace the empty APP_FERNET_KEY= line, or append if missing.
  if grep -q '^APP_FERNET_KEY=' .env; then
    # GNU sed; on macOS users would need gsed. Works on Linux (the env here).
    sed -i "s|^APP_FERNET_KEY=.*|APP_FERNET_KEY=${KEY}|" .env
  else
    printf '\nAPP_FERNET_KEY=%s\n' "$KEY" >> .env
  fi
fi

# 3. Postgres
say "Starting Postgres (compose)"
docker compose up -d db

say "Waiting for Postgres to be healthy"
for _ in {1..30}; do
  status=$(docker compose ps --format json db 2>/dev/null | grep -oE '"Health":"[^"]*"' | cut -d'"' -f4 || true)
  [[ "$status" == "healthy" ]] && break
  sleep 1
done

# 4. Backend
say "Installing backend deps (uv sync)"
uv sync

say "Running migrations (alembic upgrade head)"
set -a
# shellcheck disable=SC1091
source .env
set +a
uv run alembic upgrade head

# 5. Frontend
say "Installing frontend deps (pnpm install)"
(cd ui && pnpm install --prefer-frozen-lockfile || (cd ui && pnpm install))

say "Setup complete. Run ./scripts/dev.sh to start everything."
