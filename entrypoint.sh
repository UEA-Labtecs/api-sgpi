#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] aplicando migrations..."
alembic upgrade head

echo "[entrypoint] iniciando API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8009
