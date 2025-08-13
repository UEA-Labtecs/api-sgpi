"""add tenant_id and role to users; add owner_id and tenant_id to user_patents; drop info

Revision ID: 347914646834
Revises: 349f60052f4b
Create Date: 2025-08-12 22:51:03.891342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '347914646834'
down_revision: Union[str, Sequence[str], None] = '349f60052f4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # users
    op.add_column('users', sa.Column('tenant_id', sa.String(), nullable=True))
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.add_column('users', sa.Column('role', sa.String(), server_default='user', nullable=False))

    # user_patents (se ainda não tiver)
    if not _has_column('user_patents', 'owner_id'):
        op.add_column('user_patents', sa.Column('owner_id', sa.Integer(), nullable=True))
        op.create_index('ix_user_patents_owner_id', 'user_patents', ['owner_id'])
        op.create_foreign_key('fk_user_patents_owner', 'user_patents', 'users', ['owner_id'], ['id'])
        # popular provisoriamente (ajuste conforme sua realidade)
        op.execute("UPDATE user_patents SET owner_id = (SELECT id FROM users ORDER BY id LIMIT 1)")
        op.alter_column('user_patents', 'owner_id', existing_type=sa.Integer(), nullable=False)

    if not _has_column('user_patents', 'tenant_id'):
        op.add_column('user_patents', sa.Column('tenant_id', sa.String(), nullable=True))
        op.create_index('ix_user_patents_tenant_id', 'user_patents', ['tenant_id'])

    # remover info se a coluna ainda existir
    if _has_column('user_patents', 'info'):
        with op.batch_alter_table('user_patents') as batch:
            batch.drop_column('info')

def downgrade():
    # voltar info
    with op.batch_alter_table('user_patents') as batch:
        batch.add_column(sa.Column('info', sa.JSON(), nullable=True))

    # user_patents
    op.drop_constraint('fk_user_patents_owner', 'user_patents', type_='foreignkey')
    op.drop_index('ix_user_patents_owner_id', table_name='user_patents')
    op.drop_index('ix_user_patents_tenant_id', table_name='user_patents')
    op.drop_column('user_patents', 'owner_id')
    op.drop_column('user_patents', 'tenant_id')

    # users
    op.drop_index('ix_users_tenant_id', table_name='users')
    op.drop_column('users', 'tenant_id')
    op.drop_column('users', 'role')

# helpers
from sqlalchemy import inspect
from alembic.runtime.migration import MigrationContext

def _has_column(table_name, column_name):
    bind = op.get_bind()
    insp = inspect(bind)
    cols = [c['name'] for c in insp.get_columns(table_name)]
    return column_name in cols