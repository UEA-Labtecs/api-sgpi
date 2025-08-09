import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from dotenv import load_dotenv

# 1) .env
load_dotenv()
config = context.config

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definido no .env")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 2) logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3) metadata (importe TODAS as models)
from app.core.database import Base
from app.models.userPatents import UserPatent  # ajuste o import se seu arquivo for user_patent.py
from app.models.patent import Patent

target_metadata = Base.metadata

# 4) opcional: ignorar tabelas no autogenerate
def include_object(object, name, type_, reflected, compare_to):
    # exemplo: ignore a tabela 'users' no autogenerate
    if type_ == "table" and name == "users":
        return False
    return True


def run_migrations_offline() -> None:
    """Gera SQL sem conectar no DB."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        # render_as_batch=True,  # só precisa em SQLite; em Postgres pode deixar comentado
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Conecta e aplica migrações."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_object=include_object,
            # render_as_batch=True,  # desnecessário em Postgres
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
