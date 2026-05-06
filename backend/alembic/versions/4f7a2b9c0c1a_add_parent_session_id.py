"""Add parent_session_id to agent_sessions for session branching

Revision ID: 4f7a2b9c0c1a
Revises: c4d1f3a2d991
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "4f7a2b9c0c1a"
down_revision = "c4d1f3a2d991"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "agent_sessions",
        sa.Column("parent_session_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_agent_sessions_parent",
        "agent_sessions",
        "agent_sessions",
        ["parent_session_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_agent_sessions_parent", "agent_sessions", ["parent_session_id"])


def downgrade() -> None:
    op.drop_constraint("fk_agent_sessions_parent", "agent_sessions", type_="foreignkey")
    op.drop_index("ix_agent_sessions_parent")
    op.drop_column("agent_sessions", "parent_session_id")

