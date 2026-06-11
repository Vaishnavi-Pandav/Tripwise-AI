import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id                 = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id            = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    preferred_budget   = Column(String(50), nullable=True)    # budget | mid-range | luxury
    travel_styles      = Column(JSONB, nullable=True)         # ["adventure", "cultural", "beach"]
    preferred_climates = Column(JSONB, nullable=True)         # ["tropical", "cold"]
    dietary_needs      = Column(JSONB, nullable=True)         # ["vegetarian", "halal"]
    updated_at         = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="preferences")
