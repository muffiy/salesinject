"""Add suggestion engine and agent progression columns

Revision ID: d5e8f1a3c992
Revises: c4d1f3a2d991
Create Date: 2026-05-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'd5e8f1a3c992'
down_revision = 'c4d1f3a2d991'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Phase 1: Suggestion Engine
    op.create_table('agent_suggestions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('agent_id', sa.UUID(), nullable=True),
        sa.Column('suggestion_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('action_data', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Phase 2: Agent Goal Progression
    op.add_column('agents', sa.Column('score', sa.Float(), nullable=True, server_default='0'))
    op.add_column('agents', sa.Column('level', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('agents', sa.Column('goal', sa.String(), nullable=True))
    op.add_column('agents', sa.Column('goal_progress', sa.Float(), nullable=True, server_default='0'))
    op.add_column('agents', sa.Column('goal_target', sa.Float(), nullable=True, server_default='100'))

    # Phase 3: Referral system
    op.add_column('users', sa.Column('referrer_id', sa.UUID(), nullable=True))
    op.add_column('users', sa.Column('referral_code', sa.String(), nullable=True, unique=True))
    op.create_foreign_key('fk_users_referrer', 'users', 'users', ['referrer_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_users_referrer', 'users', type_='foreignkey')
    op.drop_column('users', 'referral_code')
    op.drop_column('users', 'referrer_id')
    op.drop_column('agents', 'goal_target')
    op.drop_column('agents', 'goal_progress')
    op.drop_column('agents', 'goal')
    op.drop_column('agents', 'level')
    op.drop_column('agents', 'score')
    op.drop_table('agent_suggestions')