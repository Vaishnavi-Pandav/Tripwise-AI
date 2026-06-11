import uuid

from sqlalchemy import CheckConstraint, Column, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class Attraction(Base):
    __tablename__ = "attractions"

    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city                 = Column(String(150), nullable=False, index=True)
    attraction_name      = Column(String(255), nullable=False)
    category             = Column(String(100), nullable=True, index=True)  # temple | museum | park | beach
    description          = Column(Text, nullable=True)
    entry_fee            = Column(Numeric(10, 2), nullable=True)
    rating               = Column(Numeric(3, 1),  nullable=True)
    location_coordinates = Column(JSONB, nullable=True)   # {"lat": 12.97, "lng": 77.59}
    image_url            = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 5", name="ck_attraction_rating_range"),
    )
