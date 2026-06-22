import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import CheckConstraint, Column, DateTime, Float, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class GemCategory(str, PyEnum):
    BEACH      = "beach"
    TREK       = "trek"
    WATERFALL  = "waterfall"
    CAFE       = "cafe"
    VIEWPOINT  = "viewpoint"
    HISTORICAL = "historical"
    ADVENTURE  = "adventure"
    NATURE     = "nature"


class CrowdLevel(str, PyEnum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


class HiddenGem(Base):
    __tablename__ = "hidden_gems"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ── Location ──────────────────────────────────────────────────────────────
    city              = Column(String(150), nullable=False, index=True)
    place_name        = Column(String(255), nullable=False)
    latitude          = Column(Float, nullable=True)
    longitude         = Column(Float, nullable=True)

    # ── Details ───────────────────────────────────────────────────────────────
    category          = Column(String(50),  nullable=True, index=True)
    description       = Column(Text, nullable=True)
    estimated_cost    = Column(Numeric(10, 2), nullable=True)
    crowd_level       = Column(String(20),  nullable=True, default=CrowdLevel.LOW)
    best_time_to_visit= Column(String(150), nullable=True)  # e.g. "Oct–Mar, Early Morning"
    traveler_type     = Column(String(255), nullable=True)  # "solo,couples,backpacker"
    recommended_for   = Column(String(255), nullable=True)  # Backwards compat alias
    image_url         = Column(Text, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at        = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at        = Column(DateTime(timezone=True), default=datetime.utcnow,
                               onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("estimated_cost >= 0", name="ck_gem_cost_non_negative"),
    )

    def traveler_types_list(self) -> list[str]:
        if not self.traveler_type:
            return []
        return [t.strip() for t in self.traveler_type.split(",")]

    def __repr__(self) -> str:
        return f"<HiddenGem {self.place_name} | {self.city} | {self.category}>"
