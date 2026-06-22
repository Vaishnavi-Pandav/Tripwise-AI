import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class Notification(Base):
    __tablename__ = "notifications"
    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id           = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title             = Column(String(255), nullable=False)
    message           = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=True)  # trip_reminder|weather_alert|budget_alert|package_alert|hotel_alert
    is_read           = Column(Boolean, default=False, nullable=False)
    created_at        = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    user = relationship("User")
