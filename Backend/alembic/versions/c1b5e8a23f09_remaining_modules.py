"""remaining_modules

Revision ID: c1b5e8a23f09
Revises: d9c3f7e14b28
Create Date: 2026-06-22 17:00:00.000000

Creates favorites, notifications, export_history tables.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c1b5e8a23f09'
down_revision: Union[str, None] = 'd9c3f7e14b28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("favorites",
        sa.Column("id",          sa.String(36),  primary_key=True),
        sa.Column("user_id",     sa.String(36),  nullable=False),
        sa.Column("entity_type", sa.String(50),  nullable=False),
        sa.Column("entity_id",   sa.String(36),  nullable=False),
        sa.Column("created_at",  sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id","entity_type","entity_id", name="uq_favorite"),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"])

    op.create_table("notifications",
        sa.Column("id",                sa.String(36),  primary_key=True),
        sa.Column("user_id",           sa.String(36),  nullable=False),
        sa.Column("title",             sa.String(255), nullable=False),
        sa.Column("message",           sa.Text(),      nullable=False),
        sa.Column("notification_type", sa.String(50),  nullable=True),
        sa.Column("is_read",           sa.Boolean(),   nullable=False, server_default="0"),
        sa.Column("created_at",        sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_notifications_user_id",   "notifications", ["user_id"])
    op.create_index("ix_notifications_created_at","notifications", ["created_at"])

    op.create_table("export_history",
        sa.Column("id",          sa.String(36), primary_key=True),
        sa.Column("user_id",     sa.String(36), nullable=False),
        sa.Column("trip_id",     sa.String(36), nullable=False),
        sa.Column("file_url",    sa.Text(),     nullable=True),
        sa.Column("exported_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_export_history_user_id", "export_history", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_export_history_user_id", table_name="export_history")
    op.drop_table("export_history")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_user_id",    table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_favorites_user_id", table_name="favorites")
    op.drop_table("favorites")
