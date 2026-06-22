import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class AIChatHistory(Base):
    """
    Stores every user ↔ AI conversation turn.
    trip_id is optional — when provided the AI uses trip context.
    """
    __tablename__ = "ai_chat_history"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False, index=True)
    trip_id      = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="SET NULL"),
                          nullable=True, index=True)
    user_message = Column(Text, nullable=False)
    ai_response  = Column(Text, nullable=False)
    created_at   = Column(DateTime(timezone=True), default=datetime.utcnow,
                          nullable=False, index=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    user = relationship("User", back_populates="chat_history")
    trip = relationship("Trip")

    def __repr__(self) -> str:
        return f"<AIChatHistory user={self.user_id} trip={self.trip_id}>"
