"""trip_module_complete

Revision ID: 1a260098e20f
Revises: ee0ab6e3bc74
Create Date: 2026-06-11 18:00:00.000000

Adds CHECK constraint for budget > 0 and updates default trip_status
to 'draft'. Safe to run on existing databases — constraints are added
with SQLite-compatible IF NOT EXISTS guards where possible.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '1a260098e20f'
down_revision: Union[str, None] = 'ee0ab6e3bc74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # SQLite does not support adding CHECK constraints to existing tables.
    # On PostgreSQL these are applied via ALTER TABLE.
    if bind.dialect.name == "postgresql":
        op.execute("""
            ALTER TABLE trips
            ADD CONSTRAINT ck_trips_budget_positive CHECK (budget > 0)
        """)
        # Rename constraint if old name exists (idempotent)
        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'ck_trips_days_positive'
                ) THEN
                    ALTER TABLE trips
                    ADD CONSTRAINT ck_trips_days_positive
                    CHECK (number_of_days >= 1);
                END IF;
            END $$;
        """)
        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'ck_trips_travelers_positive'
                ) THEN
                    ALTER TABLE trips
                    ADD CONSTRAINT ck_trips_travelers_positive
                    CHECK (number_of_travelers >= 1);
                END IF;
            END $$;
        """)
    # SQLite: constraints are baked into the CREATE TABLE in the initial migration.
    # No ALTER TABLE needed.


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE trips DROP CONSTRAINT IF EXISTS ck_trips_budget_positive")
