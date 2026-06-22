"""weather_module_complete

Revision ID: f2a8c6b03d91
Revises: c9d1f4a82b06
Create Date: 2026-06-22 13:00:00.000000

Adds feels_like, wind_speed, weather_icon, rain_probability to weather_data_cache.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f2a8c6b03d91'
down_revision: Union[str, None] = 'd7e3b52a9f14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("weather_data_cache") as batch:
        batch.add_column(sa.Column("feels_like",       sa.Numeric(5, 2), nullable=True))
        batch.add_column(sa.Column("wind_speed",       sa.Float(),       nullable=True))
        batch.add_column(sa.Column("weather_icon",     sa.String(50),    nullable=True))
        batch.add_column(sa.Column("rain_probability", sa.Float(),       nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("weather_data_cache") as batch:
        batch.drop_column("feels_like")
        batch.drop_column("wind_speed")
        batch.drop_column("weather_icon")
        batch.drop_column("rain_probability")
