import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Itinerary(Base):
    __tablename__ = "itineraries"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id        = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    day_number     = Column(Integer, nullable=False)
    title          = Column(String(255), nullable=True)
    activities     = Column(JSONB, nullable=True)      # structured activity list
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    created_at     = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("day_number > 0",  name="ck_itineraries_day_positive"),
        UniqueConstraint("trip_id", "day_number", name="uq_itineraries_trip_day"),
    )

    # Relationships
    trip = relationship("Trip", back_populates="itineraries")
