"""offer boost safety fields

Revision ID: e12a4dd91b2c
Revises: c4d1f3a2d991
Create Date: 2026-05-03
"""
from alembic import op
import sqlalchemy as sa

revision = 'e12a4dd91b2c'
down_revision = 'c4d1f3a2d991'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('offers', sa.Column('boost_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('offers', sa.Column('last_boosted_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('offers', 'last_boosted_at')
    op.drop_column('offers', 'boost_count')
