"""baseline schema (initial create)"""

from alembic import op
import sqlalchemy as sa

revision = "bf4c8ea79ab8"
down_revision = None
branch_labels = None
depends_on = None



def upgrade():
    from sqlalchemy import Table, Column, Integer, String, JSON, MetaData
    meta = MetaData()
    # Tabela patents completa (ajuste colunas p/ seu modelo atual)
    op.create_table(
        "patents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("numero_pedido", sa.String, index=True),
        sa.Column("data_deposito", sa.String),
        sa.Column("data_publicacao", sa.String),
        sa.Column("data_concessao", sa.String),
        sa.Column("classificacao_ipc", sa.JSON, nullable=True),
        sa.Column("classificacao_cpc", sa.JSON, nullable=True),
        sa.Column("titulo", sa.String, nullable=True),
        sa.Column("resumo", sa.String, nullable=True),
        sa.Column("depositante", sa.String, nullable=True),
        sa.Column("inventores", sa.String, nullable=True),
        sa.Column("url_detalhe", sa.String, nullable=True),
        # sem FK aqui; isso fica para revisões seguintes
    )



def downgrade() -> None:
    """Downgrade schema."""
    pass
