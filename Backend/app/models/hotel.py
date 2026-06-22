import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import CheckConstraint, Column, DateTime, Float, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class HotelCategory(str, PyEnum):
    BUDGET   = "budget"
    STANDARD = "standard"
    PREMIUM  = "premium"
    LUXURY   = "luxury"


class Hotel(Base):
    __tablename__ = "hotels"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ── Location ──────────────────────────────────────────────────────────────
    city            = Column(String(150), nullable=False, index=True)
    address         = Column(Text, nullable=True)
    latitude        = Column(Float, nullable=True)
    longitude       = Column(Float, nullable=True)

    # ── Hotel info ────────────────────────────────────────────────────────────
    hotel_name      = Column(String(255), nullable=False)
    description     = Column(Text, nullable=True)
    hotel_category  = Column(String(50), nullable=True, default=HotelCategory.STANDARD, index=True)
    price_per_night = Column(Numeric(10, 2), nullable=False, index=True)
    rating          = Column(Numeric(3, 1), nullable=True, index=True)
    amenities       = Column(Text, nullable=True)   # JSON string — compatible with SQLite + PostgreSQL
    image_url       = Column(Text, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at      = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at      = Column(DateTime(timezone=True), default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 5",       name="ck_hotels_rating_range"),
        CheckConstraint("price_per_night > 0",               name="ck_hotels_price_positive"),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    recommendations = relationship("HotelRecommendation", back_populates="hotel",
                                   cascade="all, delete-orphan")
    reviews         = relationship("Review", back_populates="hotel")

    def amenities_list(self) -> list[str]:
        """Parse stored JSON amenities string into a Python list."""
        import json
        if not self.amenities:
            return []
        try:
            return json.loads(self.amenities)
        except (ValueError, TypeError):
            return []

    def __repr__(self) -> str:
        return f"<Hotel {self.hotel_name} | {self.city} | ₹{self.price_per_night}/night>"
