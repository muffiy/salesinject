"""add viral mission fields

Revision ID: c4d1f3a2d991
Revises: b9e812d1b112
Create Date: 2026-05-03
"""
from alembic import op
import sqlalchemy as sa

revision = 'c4d1f3a2d991'
down_revision = 'b9e812d1b112'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('reputation_score', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('level', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('users', sa.Column('xp', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('offers', sa.Column('auto_boost', sa.Boolean(), nullable=True, server_default=sa.false()))
    op.add_column('offer_claims', sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('offer_claims', sa.Column('position', sa.Integer(), nullable=True))
    op.add_column('offer_claims', sa.Column('boosted', sa.Boolean(), nullable=True, server_default=sa.false()))
    op.add_column('offer_claims', sa.Column('payout_amount', sa.Numeric(10, 2), nullable=True, server_default='0'))
    op.create_table('mission_shares',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('mission_id', sa.UUID(), nullable=False),
        sa.Column('bonus_granted', sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['mission_id'], ['offer_claims.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('mission_shares')
    op.drop_column('offer_claims', 'payout_amount')
    op.drop_column('offer_claims', 'boosted')
    op.drop_column('offer_claims', 'position')
    op.drop_column('offer_claims', 'claimed_at')
    op.drop_column('offers', 'auto_boost')
    op.drop_column('users', 'xp')
    op.drop_column('users', 'level')
    op.drop_column('users', 'reputation_score')
