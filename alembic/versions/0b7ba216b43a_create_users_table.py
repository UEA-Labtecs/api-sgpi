"""create users table

Revision ID: 0b7ba216b43a
Revises: 6c34a4d0fa35
Create Date: 2025-08-09 13:41:16.573315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b7ba216b43a'
down_revision = '6c34a4d0fa35'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'])
    op.create_index(op.f('ix_users_name'), 'users', ['name'])
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
