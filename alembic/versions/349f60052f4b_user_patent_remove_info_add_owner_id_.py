"""user_patent remove info, add owner_id/tenant_id

Revision ID: 349f60052f4b
Revises: 0b7ba216b43a
Create Date: 2025-08-12 22:36:23.630411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '349f60052f4b'
down_revision: Union[str, Sequence[str], None] = '0b7ba216b43a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1) adicionar colunas novas como NULLABLE primeiro
    op.add_column('user_patents', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.add_column('user_patents', sa.Column('tenant_id', sa.String(), nullable=True))

    op.create_index('ix_user_patents_owner_id', 'user_patents', ['owner_id'])
    op.create_index('ix_user_patents_tenant_id', 'user_patents', ['tenant_id'])

    op.create_foreign_key(
        'fk_user_patents_owner',
        'user_patents', 'users',
        ['owner_id'], ['id'],
        ondelete='CASCADE'  # se quiser cascata
    )

    # 2) data migration: popular owner_id
    # ATENÇÃO: escolha uma estratégia. Exemplos:
    # - Se todas as "minhas patentes" devem pertencer a um user específico:
    # op.execute("UPDATE user_patents SET owner_id = 1")
    #
    # - Se você não sabe o owner, crie um usuário 'admin' e use o id dele:
    # op.execute("UPDATE user_patents SET owner_id = (SELECT id FROM users WHERE role='admin' LIMIT 1)")
    #
    # Ajuste conforme sua realidade.
    # Remova esta linha se você garantirá o preenchimento por outra via.
    # op.execute("UPDATE user_patents SET owner_id = 1")

    # 3) tornar NOT NULL depois de popular
    op.alter_column('user_patents', 'owner_id', existing_type=sa.Integer(), nullable=False)

    # 4) remover a coluna info (quebra dados antigos)
    with op.batch_alter_table('user_patents') as batch_op:
        batch_op.drop_column('info')


def downgrade():
    # reverter drop
    with op.batch_alter_table('user_patents') as batch_op:
        batch_op.add_column(sa.Column('info', sa.JSON(), nullable=True))

    # tornar owner_id nullable de novo
    op.alter_column('user_patents', 'owner_id', existing_type=sa.Integer(), nullable=True)

    # soltar FK e índices
    op.drop_constraint('fk_user_patents_owner', 'user_patents', type_='foreignkey')
    op.drop_index('ix_user_patents_owner_id', table_name='user_patents')
    op.drop_index('ix_user_patents_tenant_id', table_name='user_patents')

    # remover colunas
    op.drop_column('user_patents', 'tenant_id')
    op.drop_column('user_patents', 'owner_id')
