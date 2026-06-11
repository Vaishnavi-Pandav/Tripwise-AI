import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class TripExpenses(Base):
    __tablename__ = "trip_expenses"

    id                 = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id            = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    transport_cost     = Column(Numeric(12, 2), nullable=False, default=0)
    hotel_cost         = Column(Numeric(12, 2), nullable=False, default=0)
    food_cost          = Column(Numeric(12, 2), nullable=False, default=0)
    activity_cost      = Column(Numeric(12, 2), nullable=False, default=0)
    miscellaneous_cost = Column(Numeric(12, 2), nullable=False, default=0)
    # total_cost computed in Python (Postgres generated column handled in SQL)
    created_at         = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    trip = relationship("Trip", back_populates="expenses")

    @property
    def total_cost(self) -> float:
        return float(
            (self.transport_cost or 0) +
            (self.hotel_cost or 0) +
            (self.food_cost or 0) +
            (self.activity_cost or 0) +
            (self.miscellaneous_cost or 0)
        )
