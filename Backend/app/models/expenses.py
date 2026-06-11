import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class TripExpenses(Base):
    """
    One-to-one with Trip.
    Stores the full budget breakdown linked to a specific trip.
    """
    __tablename__ = "trip_expenses"

    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id              = Column(
                               UUID(as_uuid=True),
                               ForeignKey("trips.id", ondelete="CASCADE"),
                               nullable=False,
                               unique=True,
                               index=True,
                           )
    # ── Cost categories ───────────────────────────────────────────────────────
    transport_cost       = Column(Numeric(12, 2), nullable=False, default=0)
    accommodation_cost   = Column(Numeric(12, 2), nullable=False, default=0)
    food_cost            = Column(Numeric(12, 2), nullable=False, default=0)
    activity_cost        = Column(Numeric(12, 2), nullable=False, default=0)
    miscellaneous_cost   = Column(Numeric(12, 2), nullable=False, default=0)
    total_cost           = Column(Numeric(12, 2), nullable=False, default=0)
    budget_remaining     = Column(Numeric(12, 2), nullable=False, default=0)

    # ── Metadata ──────────────────────────────────────────────────────────────
    accommodation_type   = Column(String(50), nullable=True)   # budget | mid-range | luxury
    travel_mode          = Column(String(50), nullable=True)   # flight | train | road | mixed
    destination_category = Column(String(100), nullable=True)  # beach | mountain | city | cultural

    created_at           = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at           = Column(
                               DateTime(timezone=True),
                               default=datetime.utcnow,
                               onupdate=datetime.utcnow,
                               nullable=False,
                           )

    # ── Relationship ──────────────────────────────────────────────────────────
    trip = relationship("Trip", back_populates="expenses")

    # ── Backwards compat ──────────────────────────────────────────────────────
    @property
    def hotel_cost(self) -> float:
        return float(self.accommodation_cost or 0)

    def __repr__(self) -> str:
        return f"<TripExpenses trip_id={self.trip_id} total={self.total_cost}>"
