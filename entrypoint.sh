#!/usr/bin/env bash
set -e

echo "[entrypoint] aguardando banco..."

python - <<'PY'
import os, time
from sqlalchemy import create_engine
url = os.getenv("DATABASE_URL")
if not url:
    print("DATABASE_URL não definido; seguindo...")
else:
    for i in range(60):
        try:
            e = create_engine(url, pool_pre_ping=True, future=True)
            with e.connect() as c:
                c.execute("SELECT 1")
            print("DB OK")
            break
        except Exception as ex:
            print(f"DB ainda não pronto ({ex}); retry {i+1}/60")
            time.sleep(2)
    else:
        raise SystemExit("Banco indisponível.")
PY

echo "[entrypoint] aplicando migrations..."
alembic upgrade head

# (opcional) autogerar migration em DEV se AUTO_MIGRATE=1
if [ "${AUTO_MIGRATE}" = "1" ]; then
  echo "[entrypoint] autogerando migration (dev) ..."
  alembic revision --autogenerate -m "auto on startup" || true
  alembic upgrade head || true
fi

echo "[entrypoint] iniciando API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8009
