import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class RouteHistory(Base):
    __tablename__ = "route_history"

    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id              = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                                  nullable=False, index=True)
    source_location      = Column(String(255), nullable=False)
    destination_location = Column(String(255), nullable=False)
    distance_km          = Column(Float, nullable=True)
    duration_minutes     = Column(Integer, nullable=True)
    travel_mode          = Column(String(50), nullable=True)   # car | bus | train | flight
    estimated_cost       = Column(Numeric(12, 2), nullable=True)
    created_at           = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<Route {self.source_location} → {self.destination_location} [{self.travel_mode}]>"
