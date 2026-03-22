"""add conversation sessions

Revision ID: 0002_conversation_sessions
Revises: 0001_keepiq_mvp
Create Date: 2026-03-22 14:20:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_conversation_sessions"
down_revision: str | None = "0001_keepiq_mvp"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conversation_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("root_inbox_item_id", sa.Integer(), sa.ForeignKey("inbox_items.id", ondelete="SET NULL"), nullable=True),
        sa.Column("last_inbox_item_id", sa.Integer(), sa.ForeignKey("inbox_items.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'active'")),
        sa.Column("draft_kind", sa.String(length=20), nullable=True),
        sa.Column("draft_title", sa.String(length=255), nullable=True),
        sa.Column("draft_summary", sa.Text(), nullable=True),
        sa.Column("draft_payload_json", sa.JSON(), nullable=True),
        sa.Column("transcript_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_conversation_sessions_user_id", "conversation_sessions", ["user_id"])
    op.create_index("ix_conversation_sessions_status", "conversation_sessions", ["status"])
    op.create_index("ix_conversation_sessions_updated_at", "conversation_sessions", ["updated_at"])


def downgrade() -> None:
    op.drop_table("conversation_sessions")
