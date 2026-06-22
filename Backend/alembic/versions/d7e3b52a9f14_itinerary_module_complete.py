"""itinerary_module_complete

Revision ID: d7e3b52a9f14
Revises: c9d1f4a82b06
Create Date: 2026-06-22 13:00:00.000000

Adds notes, updated_at to itineraries table.
Converts activities column to Text for SQLite compat.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd7e3b52a9f14'
down_revision: Union[str, None] = 'c9d1f4a82b06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("itineraries") as batch:
        batch.add_column(sa.Column("notes",      sa.Text(),  nullable=True))
        batch.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("itineraries") as batch:
        batch.drop_column("notes")
        batch.drop_column("updated_at")
