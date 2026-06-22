import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    CheckConstraint, Column, DateTime,
    Float, Integer, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class PackageType(str, PyEnum):
    BUDGET   = "budget"
    STANDARD = "standard"
    PREMIUM  = "premium"
    LUXURY   = "luxury"


class TravelPackage(Base):
    __tablename__ = "travel_packages"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ── Agency & package info ─────────────────────────────────────────────────
    agency_name         = Column(String(255), nullable=True, index=True)
    package_name        = Column(String(255), nullable=False)
    package_type        = Column(String(50),  nullable=True, default=PackageType.STANDARD, index=True)
    destination         = Column(String(255), nullable=False, index=True)
    duration_days       = Column(Integer,     nullable=False)
    price               = Column(Numeric(12, 2), nullable=False, index=True)
    package_description = Column(Text, nullable=True)

    # ── Lists stored as JSON strings (SQLite + PostgreSQL compat) ─────────────
    inclusions          = Column(Text, nullable=True)   # JSON: ["Flights","Hotel","Meals"]
    exclusions          = Column(Text, nullable=True)   # JSON: ["Visa","Travel Insurance"]

    # ── Scoring & media ───────────────────────────────────────────────────────
    rating              = Column(Float, nullable=True, index=True)   # 0.0–5.0
    image_url           = Column(Text, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at          = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at          = Column(DateTime(timezone=True), default=datetime.utcnow,
                                 onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("duration_days > 0",  name="ck_packages_duration_positive"),
        CheckConstraint("price > 0",          name="ck_packages_price_positive"),
        CheckConstraint("rating >= 0 AND rating <= 5", name="ck_packages_rating_range"),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    reviews = relationship("Review", back_populates="package")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def inclusions_list(self) -> list[str]:
        import json
        if not self.inclusions:
            return []
        try:
            return json.loads(self.inclusions)
        except (ValueError, TypeError):
            return []

    def exclusions_list(self) -> list[str]:
        import json
        if not self.exclusions:
            return []
        try:
            return json.loads(self.exclusions)
        except (ValueError, TypeError):
            return []

    def __repr__(self) -> str:
        return f"<TravelPackage {self.package_name} | {self.destination} | ₹{self.price}>"
