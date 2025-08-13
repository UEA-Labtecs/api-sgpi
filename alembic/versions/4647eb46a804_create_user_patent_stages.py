"""create user_patent_stages

Revision ID: 4647eb46a804
Revises: 347914646834
Create Date: 2025-08-12 23:17:35.497843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4647eb46a804'
down_revision: Union[str, Sequence[str], None] = '347914646834'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        "user_patent_stages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_patent_id", sa.Integer(), sa.ForeignKey("user_patents.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("stage", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("file_key", sa.String(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("user_patent_id", "stage", name="uq_user_patent_stage"),
        sa.CheckConstraint("stage BETWEEN 3 AND 6", name="ck_stage_range_3_6"),
    )

def downgrade():
    op.drop_table("user_patent_stages")
