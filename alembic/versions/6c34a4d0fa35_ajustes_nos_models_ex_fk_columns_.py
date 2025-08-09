from alembic import op
import sqlalchemy as sa

revision = "6c34a4d0fa35"
down_revision = "747bacce7d86"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()

    # Se você usa PgBouncer em transaction pooling, garanta que essa conexão é direta.
    # Opcional: aumente timeouts p/ evitar cancelamentos
    # bind.execute(sa.text("SET lock_timeout = '60s'"))
    # bind.execute(sa.text("SET statement_timeout = '10min'"))

    # 1) ADD COLUMN (sem default, sem not null) com IF NOT EXISTS => lock curtíssimo
    op.execute("ALTER TABLE IF EXISTS user_patents ADD COLUMN IF NOT EXISTS status INTEGER")
    op.execute("ALTER TABLE IF EXISTS user_patents ADD COLUMN IF NOT EXISTS info JSON")

    # 2) Backfill (idempotente)
    op.execute("UPDATE user_patents SET status = 0 WHERE status IS NULL")

    # 3) SET DEFAULT e NOT NULL (idempotente)
    op.execute("ALTER TABLE user_patents ALTER COLUMN status SET DEFAULT 0")
    # NOT NULL só se ainda não for:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='user_patents'
                  AND column_name='status'
                  AND is_nullable='NO'
            ) THEN
                ALTER TABLE user_patents ALTER COLUMN status SET NOT NULL;
            END IF;
        END$$;
    """)

    # 4) Coluna de vínculo em patents
    op.execute("ALTER TABLE IF EXISTS patents ADD COLUMN IF NOT EXISTS user_patent_id INTEGER")

    # 5) FK com menos lock (NOT VALID -> VALIDATE), idempotente
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints
                WHERE table_name='patents'
                  AND constraint_type='FOREIGN KEY'
                  AND constraint_name='fk_patents_user_patent'
            ) THEN
                ALTER TABLE patents
                ADD CONSTRAINT fk_patents_user_patent
                FOREIGN KEY (user_patent_id)
                REFERENCES user_patents(id)
                ON DELETE CASCADE
                NOT VALID;
            END IF;
        END$$;
    """)
    op.execute("ALTER TABLE patents VALIDATE CONSTRAINT fk_patents_user_patent")

    # 6) Remover campos antigos de patents (se existirem)
    op.execute("ALTER TABLE IF EXISTS patents DROP COLUMN IF EXISTS status")
    op.execute("ALTER TABLE IF EXISTS patents DROP COLUMN IF EXISTS info")

def downgrade():
    pass
