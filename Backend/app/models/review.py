import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Review(Base):
    __tablename__ = "reviews"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id",            ondelete="CASCADE"),  nullable=False, index=True)
    hotel_id    = Column(UUID(as_uuid=True), ForeignKey("hotels.id",           ondelete="SET NULL"), nullable=True,  index=True)
    package_id  = Column(UUID(as_uuid=True), ForeignKey("travel_packages.id",  ondelete="SET NULL"), nullable=True,  index=True)
    rating      = Column(Numeric(3, 1), nullable=False)
    review_text = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
        CheckConstraint("hotel_id IS NOT NULL OR package_id IS NOT NULL", name="ck_review_target"),
    )

    # Relationships
    user    = relationship("User",          back_populates="reviews")
    hotel   = relationship("Hotel",         back_populates="reviews")
    package = relationship("TravelPackage", back_populates="reviews")
