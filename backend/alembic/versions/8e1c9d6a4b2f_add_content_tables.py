"""Add content generation tables (brand_voices, content_templates, content_pieces)

Revision ID: 8e1c9d6a4b2f
Revises: 4f7a2b9c0c1a
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "8e1c9d6a4b2f"
down_revision = "4f7a2b9c0c1a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "brand_voices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("personality", sa.Text(), nullable=True),
        sa.Column("writing_style", sa.Text(), nullable=True),
        sa.Column("forbidden_words", postgresql.ARRAY(sa.String()), server_default="{}", nullable=True),
        sa.Column("preferred_phrases", postgresql.ARRAY(sa.String()), server_default="{}", nullable=True),
        sa.Column("emoji_style", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_brand_voices_user_id", "brand_voices", ["user_id"])

    op.create_table(
        "content_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("content_type", sa.String(), nullable=True),
        sa.Column("structure", sa.Text(), nullable=False),
        sa.Column("variables", postgresql.ARRAY(sa.String()), server_default="{}", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_templates_user_id", "content_templates", ["user_id"])

    op.create_table(
        "content_pieces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False, server_default="social_post"),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("raw_output", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("parsed_content", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("brand_voice_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("model_used", sa.String(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), server_default="0", nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["brand_voice_id"], ["brand_voices.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["template_id"], ["content_templates.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_pieces_user_id", "content_pieces", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_content_pieces_user_id", table_name="content_pieces")
    op.drop_table("content_pieces")

    op.drop_index("ix_content_templates_user_id", table_name="content_templates")
    op.drop_table("content_templates")

    op.drop_index("ix_brand_voices_user_id", table_name="brand_voices")
    op.drop_table("brand_voices")

