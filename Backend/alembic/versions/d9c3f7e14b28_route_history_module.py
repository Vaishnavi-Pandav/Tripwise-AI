"""route_history_module

Revision ID: d9c3f7e14b28
Revises: e5b8a4c91d32
Create Date: 2026-06-22 16:00:00.000000

Creates route_history table.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd9c3f7e14b28'
down_revision: Union[str, None] = 'e5b8a4c91d32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "route_history",
        sa.Column("id",                   sa.String(36),            primary_key=True),
        sa.Column("user_id",              sa.String(36),            nullable=False),
        sa.Column("source_location",      sa.String(255),           nullable=False),
        sa.Column("destination_location", sa.String(255),           nullable=False),
        sa.Column("distance_km",          sa.Float(),               nullable=True),
        sa.Column("duration_minutes",     sa.Integer(),             nullable=True),
        sa.Column("travel_mode",          sa.String(50),            nullable=True),
        sa.Column("estimated_cost",       sa.Numeric(12, 2),        nullable=True),
        sa.Column("created_at",           sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_route_history_user_id", "route_history", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_route_history_user_id", table_name="route_history")
    op.drop_table("route_history")
