import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id              = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_location      = Column(String(255), nullable=False)
    destination_location = Column(String(255), nullable=False, index=True)
    budget               = Column(Numeric(12, 2), nullable=False)
    number_of_days       = Column(Integer, nullable=False)
    number_of_travelers  = Column(Integer, nullable=False)
    travel_mode          = Column(String(50), nullable=True)     # flight | train | road | mixed
    total_estimated_cost = Column(Numeric(12, 2), nullable=True)
    trip_status          = Column(String(30), nullable=False, default="draft", index=True)  # draft | planned | ongoing | completed
    created_at           = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at           = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("number_of_days > 0",      name="ck_trips_days_positive"),
        CheckConstraint("number_of_travelers > 0", name="ck_trips_travelers_positive"),
    )

    # Relationships
    owner                = relationship("User",                back_populates="trips")
    hotel_recommendations= relationship("HotelRecommendation", back_populates="trip",    cascade="all, delete-orphan")
    expenses             = relationship("TripExpenses",         back_populates="trip",    uselist=False, cascade="all, delete-orphan")
    itineraries          = relationship("Itinerary",            back_populates="trip",    cascade="all, delete-orphan")
    saved_by             = relationship("SavedTrip",            back_populates="trip",    cascade="all, delete-orphan")
