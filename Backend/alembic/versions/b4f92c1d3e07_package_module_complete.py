"""package_module_complete

Revision ID: b4f92c1d3e07
Revises: 03779aefdf3a
Create Date: 2026-06-22 11:00:00.000000

Adds package_type, rating, image_url, updated_at to travel_packages.
Converts inclusions/exclusions from JSONB to Text for SQLite compat.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b4f92c1d3e07'
down_revision: Union[str, None] = '03779aefdf3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("travel_packages") as batch:
        batch.add_column(sa.Column("package_type", sa.String(50),  nullable=True))
        batch.add_column(sa.Column("rating",       sa.Float(),     nullable=True))
        batch.add_column(sa.Column("image_url",    sa.Text(),      nullable=True))
        batch.add_column(sa.Column("updated_at",   sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("travel_packages") as batch:
        batch.drop_column("package_type")
        batch.drop_column("rating")
        batch.drop_column("image_url")
        batch.drop_column("updated_at")
