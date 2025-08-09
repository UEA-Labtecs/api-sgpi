"""add user_patents + fk em patents"""

from alembic import op
import sqlalchemy as sa

# --- Identificadores da revisão ---
revision = "747bacce7d86"        # pode manter esse id
down_revision = None             # ou a revisão anterior, se existir
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 1) criar tabela user_patents se não existir
    if not insp.has_table("user_patents"):
        op.create_table(
            "user_patents",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("titulo", sa.String(), nullable=False),
            sa.Column("descricao", sa.Text(), nullable=True),
            sa.Column("status", sa.Integer(), server_default="0", nullable=False),
            sa.Column("info", sa.JSON(), nullable=True),
        )

    # 2) adicionar coluna user_patent_id em patents se não existir
    cols = {c["name"] for c in insp.get_columns("patents")}
    if "user_patent_id" not in cols:
        op.add_column("patents", sa.Column("user_patent_id", sa.Integer(), nullable=True))

    # 3) criar FK se não existir
    fks = {fk["name"] for fk in insp.get_foreign_keys("patents") if fk.get("name")}
    if "fk_patents_user_patent" not in fks:
        op.create_foreign_key(
            "fk_patents_user_patent",
            "patents",
            "user_patents",
            ["user_patent_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade():
    # opcional — implemente se precisar dar rollback
    pass
