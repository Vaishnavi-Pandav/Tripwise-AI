import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class AITripSuggestion(Base):
    __tablename__ = "ai_trip_suggestions"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    destination  = Column(String(255), nullable=False)
    reason       = Column(Text, nullable=True)
    suggested_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_dismissed = Column(Boolean, nullable=False, default=False)

    # Relationships
    user = relationship("User", back_populates="ai_suggestions")
