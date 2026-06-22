import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey,
    Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Itinerary(Base):
    """
    Stores one row per day per trip.
    activities: JSON string — list of morning/afternoon/evening activities.
    notes:      AI-generated tips and warnings for that day.
    """
    __tablename__ = "itineraries"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id        = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    day_number     = Column(Integer, nullable=False)
    title          = Column(String(255), nullable=True)
    activities     = Column(Text, nullable=True)      # JSON string — morning/afternoon/evening
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    notes          = Column(Text, nullable=True)      # AI tips / warnings for the day
    created_at     = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at     = Column(DateTime(timezone=True), default=datetime.utcnow,
                            onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("day_number >= 0",  name="ck_itineraries_day_non_negative"),
        UniqueConstraint("trip_id", "day_number", name="uq_itineraries_trip_day"),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    trip = relationship("Trip", back_populates="itineraries")

    def activities_parsed(self) -> dict:
        import json
        if not self.activities:
            return {}
        try:
            return json.loads(self.activities)
        except (ValueError, TypeError):
            return {"raw": self.activities}

    def __repr__(self) -> str:
        return f"<Itinerary trip={self.trip_id} day={self.day_number}>"
