import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class HotelRecommendation(Base):
    __tablename__ = "hotel_recommendations"

    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id              = Column(UUID(as_uuid=True), ForeignKey("trips.id",  ondelete="CASCADE"),
                                  nullable=False, index=True)
    hotel_id             = Column(UUID(as_uuid=True), ForeignKey("hotels.id", ondelete="CASCADE"),
                                  nullable=False, index=True)
    # Score out of 100 (changed from 10 to match requirement)
    recommendation_score = Column(Numeric(5, 2), nullable=True)
    created_at           = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "recommendation_score >= 0 AND recommendation_score <= 100",
            name="ck_rec_score_range_100",
        ),
        UniqueConstraint("trip_id", "hotel_id", name="uq_hotel_rec_trip_hotel"),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    trip  = relationship("Trip",  back_populates="hotel_recommendations")
    hotel = relationship("Hotel", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<HotelRecommendation trip={self.trip_id} hotel={self.hotel_id} score={self.recommendation_score}>"
