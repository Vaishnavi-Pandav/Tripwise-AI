import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class TravelPackage(Base):
    __tablename__ = "travel_packages"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination         = Column(String(255), nullable=False, index=True)
    agency_name         = Column(String(255), nullable=True)
    package_name        = Column(String(255), nullable=False)
    duration_days       = Column(Integer, nullable=False)
    price               = Column(Numeric(12, 2), nullable=False, index=True)
    package_description = Column(Text, nullable=True)
    inclusions          = Column(JSONB, nullable=True)   # ["Flights", "Hotel", "Meals"]
    exclusions          = Column(JSONB, nullable=True)   # ["Visa", "Travel Insurance"]
    created_at          = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("duration_days > 0", name="ck_packages_duration_positive"),
    )

    # Relationships
    reviews = relationship("Review", back_populates="package")
