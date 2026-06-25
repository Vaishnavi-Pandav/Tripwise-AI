import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class Favorite(Base):
    __tablename__ = "favorites"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)   # destination|hotel|trip|package
    entity_id   = Column(String(36), nullable=False)
    created_at  = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("user_id","entity_type","entity_id", name="uq_favorite"),)
    user = relationship("User")
