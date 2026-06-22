"""hidden_gem_module

Revision ID: e5b8a4c91d32
Revises: a3e7d9b12c45
Create Date: 2026-06-22 15:00:00.000000

Adds category, estimated_cost, crowd_level, best_time_to_visit,
traveler_type, latitude, longitude, updated_at to hidden_gems.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e5b8a4c91d32'
down_revision: Union[str, None] = 'a3e7d9b12c45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("hidden_gems") as batch:
        batch.add_column(sa.Column("category",           sa.String(50),      nullable=True))
        batch.add_column(sa.Column("estimated_cost",     sa.Numeric(10, 2),  nullable=True))
        batch.add_column(sa.Column("crowd_level",        sa.String(20),      nullable=True))
        batch.add_column(sa.Column("best_time_to_visit", sa.String(150),     nullable=True))
        batch.add_column(sa.Column("traveler_type",      sa.String(255),     nullable=True))
        batch.add_column(sa.Column("latitude",           sa.Float(),         nullable=True))
        batch.add_column(sa.Column("longitude",          sa.Float(),         nullable=True))
        batch.add_column(sa.Column("updated_at",         sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_hidden_gems_category", "hidden_gems", ["category"])


def downgrade() -> None:
    op.drop_index("ix_hidden_gems_category", table_name="hidden_gems")
    with op.batch_alter_table("hidden_gems") as batch:
        batch.drop_column("category")
        batch.drop_column("estimated_cost")
        batch.drop_column("crowd_level")
        batch.drop_column("best_time_to_visit")
        batch.drop_column("traveler_type")
        batch.drop_column("latitude")
        batch.drop_column("longitude")
        batch.drop_column("updated_at")
