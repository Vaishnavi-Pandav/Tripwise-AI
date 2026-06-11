import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Hotel(Base):
    __tablename__ = "hotels"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city            = Column(String(150), nullable=False, index=True)
    hotel_name      = Column(String(255), nullable=False)
    description     = Column(Text, nullable=True)
    price_per_night = Column(Numeric(10, 2), nullable=False)
    rating          = Column(Numeric(3, 1), nullable=True)
    address         = Column(Text, nullable=True)
    image_url       = Column(Text, nullable=True)
    amenities       = Column(JSONB, nullable=True)   # ["WiFi", "Pool", "Spa"]
    created_at      = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 5", name="ck_hotels_rating_range"),
    )

    # Relationships
    recommendations = relationship("HotelRecommendation", back_populates="hotel", cascade="all, delete-orphan")
    reviews         = relationship("Review",               back_populates="hotel")
