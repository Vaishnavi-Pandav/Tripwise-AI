"""hotel_module_complete

Revision ID: 03779aefdf3a
Revises: 1a260098e20f
Create Date: 2026-06-22 10:00:00.000000

Adds hotel_category, latitude, longitude, updated_at to hotels table.
Adds accommodation_cost, budget_remaining, accommodation_type,
destination_category, updated_at to trip_expenses table.
Updates recommendation_score range to 0–100.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '03779aefdf3a'
down_revision: Union[str, None] = '1a260098e20f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # ── hotels ──────────────────────────────────────────────────────────────
    with op.batch_alter_table("hotels") as batch:
        batch.add_column(sa.Column("hotel_category",  sa.String(50),  nullable=True))
        batch.add_column(sa.Column("latitude",        sa.Float(),     nullable=True))
        batch.add_column(sa.Column("longitude",       sa.Float(),     nullable=True))
        batch.add_column(sa.Column("updated_at",      sa.DateTime(timezone=True),
                                   nullable=True))

    # ── trip_expenses ────────────────────────────────────────────────────────
    with op.batch_alter_table("trip_expenses") as batch:
        batch.add_column(sa.Column("accommodation_cost",    sa.Numeric(12, 2),  nullable=True))
        batch.add_column(sa.Column("budget_remaining",      sa.Numeric(12, 2),  nullable=True))
        batch.add_column(sa.Column("accommodation_type",    sa.String(50),      nullable=True))
        batch.add_column(sa.Column("travel_mode",           sa.String(50),      nullable=True))
        batch.add_column(sa.Column("destination_category",  sa.String(100),     nullable=True))
        batch.add_column(sa.Column("updated_at",            sa.DateTime(timezone=True),
                                   nullable=True))

    # ── hotel_recommendations — widen score column to 5,2 ──────────────────
    if bind.dialect.name == "postgresql":
        op.execute("""
            ALTER TABLE hotel_recommendations
            ALTER COLUMN recommendation_score TYPE NUMERIC(5,2)
        """)
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'ck_rec_score_range'
                ) THEN
                    ALTER TABLE hotel_recommendations
                    DROP CONSTRAINT ck_rec_score_range;
                END IF;
            END $$;
        """)
        op.execute("""
            ALTER TABLE hotel_recommendations
            ADD CONSTRAINT ck_rec_score_range_100
            CHECK (recommendation_score >= 0 AND recommendation_score <= 100)
        """)


def downgrade() -> None:
    with op.batch_alter_table("hotels") as batch:
        batch.drop_column("hotel_category")
        batch.drop_column("latitude")
        batch.drop_column("longitude")
        batch.drop_column("updated_at")

    with op.batch_alter_table("trip_expenses") as batch:
        batch.drop_column("accommodation_cost")
        batch.drop_column("budget_remaining")
        batch.drop_column("accommodation_type")
        batch.drop_column("travel_mode")
        batch.drop_column("destination_category")
        batch.drop_column("updated_at")
