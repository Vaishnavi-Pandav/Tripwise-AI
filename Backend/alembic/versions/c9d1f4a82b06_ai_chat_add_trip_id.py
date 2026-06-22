"""ai_chat_add_trip_id

Revision ID: c9d1f4a82b06
Revises: b4f92c1d3e07
Create Date: 2026-06-22 12:00:00.000000

Adds trip_id FK to ai_chat_history table.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c9d1f4a82b06'
down_revision: Union[str, None] = 'b4f92c1d3e07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("ai_chat_history") as batch:
        batch.add_column(
            sa.Column("trip_id", sa.String(36), nullable=True)
        )
        batch.create_index("ix_ai_chat_history_trip_id", ["trip_id"])


def downgrade() -> None:
    with op.batch_alter_table("ai_chat_history") as batch:
        batch.drop_index("ix_ai_chat_history_trip_id")
        batch.drop_column("trip_id")
