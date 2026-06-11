import uuid
import logging
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    CheckConstraint, Column, DateTime, Enum,
    ForeignKey, Integer, Numeric, String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

logger = logging.getLogger("tripwise")


class TripStatus(str, PyEnum):
    DRAFT     = "draft"
    PLANNED   = "planned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TravelMode(str, PyEnum):
    FLIGHT = "flight"
    TRAIN  = "train"
    ROAD   = "road"
    MIXED  = "mixed"


class Trip(Base):
    __tablename__ = "trips"

    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id              = Column(
                               UUID(as_uuid=True),
                               ForeignKey("users.id", ondelete="CASCADE"),
                               nullable=False,
                               index=True,
                           )
    source_location      = Column(String(255), nullable=False)
    destination_location = Column(String(255), nullable=False, index=True)
    budget               = Column(Numeric(12, 2), nullable=False)
    number_of_days       = Column(Integer, nullable=False)
    number_of_travelers  = Column(Integer, nullable=False)
    travel_mode          = Column(
                               String(50),
                               nullable=True,
                               default=TravelMode.FLIGHT,
                           )
    total_estimated_cost = Column(Numeric(12, 2), nullable=True)
    trip_status          = Column(
                               String(30),
                               nullable=False,
                               default=TripStatus.DRAFT,
                               index=True,
                           )
    created_at           = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at           = Column(
                               DateTime(timezone=True),
                               default=datetime.utcnow,
                               onupdate=datetime.utcnow,
                               nullable=False,
                           )

    __table_args__ = (
        CheckConstraint("number_of_days >= 1",      name="ck_trips_days_positive"),
        CheckConstraint("number_of_travelers >= 1", name="ck_trips_travelers_positive"),
        CheckConstraint("budget > 0",               name="ck_trips_budget_positive"),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    owner                 = relationship("User",                 back_populates="trips")
    hotel_recommendations = relationship("HotelRecommendation",  back_populates="trip",   cascade="all, delete-orphan")
    expenses              = relationship("TripExpenses",          back_populates="trip",   uselist=False, cascade="all, delete-orphan")
    itineraries           = relationship("Itinerary",             back_populates="trip",   cascade="all, delete-orphan")
    saved_by              = relationship("SavedTrip",             back_populates="trip",   cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Trip id={self.id} dest={self.destination_location} status={self.trip_status}>"
