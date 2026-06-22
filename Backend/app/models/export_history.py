import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class ExportHistory(Base):
    __tablename__ = "export_history"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    trip_id     = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    file_url    = Column(Text, nullable=True)
    exported_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    user = relationship("User")
    trip = relationship("Trip")
