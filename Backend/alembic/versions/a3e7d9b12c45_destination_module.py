"""destination_module

Revision ID: a3e7d9b12c45
Revises: f2a8c6b03d91
Create Date: 2026-06-22 14:00:00.000000

Creates destinations table.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a3e7d9b12c45'
down_revision: Union[str, None] = 'f2a8c6b03d91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "destinations",
        sa.Column("id",                    sa.String(36),  primary_key=True),
        sa.Column("city_name",             sa.String(150), nullable=False),
        sa.Column("state",                 sa.String(150), nullable=True),
        sa.Column("country",               sa.String(150), nullable=False),
        sa.Column("avg_budget_score",      sa.Float(),     nullable=True),
        sa.Column("safety_score",          sa.Float(),     nullable=True),
        sa.Column("weather_score",         sa.Float(),     nullable=True),
        sa.Column("crowd_score",           sa.Float(),     nullable=True),
        sa.Column("nightlife_score",       sa.Float(),     nullable=True),
        sa.Column("food_score",            sa.Float(),     nullable=True),
        sa.Column("adventure_score",       sa.Float(),     nullable=True),
        sa.Column("family_friendly_score", sa.Float(),     nullable=True),
        sa.Column("description",           sa.Text(),      nullable=True),
        sa.Column("best_season",           sa.String(100), nullable=True),
        sa.Column("known_for",             sa.Text(),      nullable=True),
        sa.Column("image_url",             sa.String(500), nullable=True),
        sa.Column("created_at",            sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at",            sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_destinations_city_name", "destinations", ["city_name"])
    op.create_index("ix_destinations_country",   "destinations", ["country"])


def downgrade() -> None:
    op.drop_index("ix_destinations_country",   table_name="destinations")
    op.drop_index("ix_destinations_city_name", table_name="destinations")
    op.drop_table("destinations")
