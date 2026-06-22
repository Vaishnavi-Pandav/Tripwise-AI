import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


def _score_check(col: str) -> CheckConstraint:
    return CheckConstraint(f"{col} >= 0 AND {col} <= 10", name=f"ck_dest_{col}")


class Destination(Base):
    """
    Stores curated scores for popular destinations.
    All scores are out of 10.
    """
    __tablename__ = "destinations"

    id                    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_name             = Column(String(150), nullable=False, index=True)
    state                 = Column(String(150), nullable=True)
    country               = Column(String(150), nullable=False, index=True)

    # ── Scores (0–10) ─────────────────────────────────────────────────────────
    avg_budget_score      = Column(Float, nullable=True)   # How affordable (10 = very cheap)
    safety_score          = Column(Float, nullable=True)   # Safety for tourists
    weather_score         = Column(Float, nullable=True)   # Climate appeal
    crowd_score           = Column(Float, nullable=True)   # Less crowded = higher score
    nightlife_score       = Column(Float, nullable=True)   # Bars, clubs, events
    food_score            = Column(Float, nullable=True)   # Cuisine variety & quality
    adventure_score       = Column(Float, nullable=True)   # Trekking, sports, adventure
    family_friendly_score = Column(Float, nullable=True)   # Suitability for families

    # ── Extra info ────────────────────────────────────────────────────────────
    description           = Column(Text, nullable=True)
    best_season           = Column(String(100), nullable=True)  # e.g. "Oct–Mar"
    known_for             = Column(Text, nullable=True)          # comma-separated tags
    image_url             = Column(String(500), nullable=True)

    created_at            = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at            = Column(DateTime(timezone=True), default=datetime.utcnow,
                                   onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        _score_check("avg_budget_score"),
        _score_check("safety_score"),
        _score_check("weather_score"),
        _score_check("crowd_score"),
        _score_check("nightlife_score"),
        _score_check("food_score"),
        _score_check("adventure_score"),
        _score_check("family_friendly_score"),
    )

    def overall_score(self) -> float:
        scores = [
            self.avg_budget_score, self.safety_score, self.weather_score,
            self.crowd_score, self.nightlife_score, self.food_score,
            self.adventure_score, self.family_friendly_score,
        ]
        valid = [s for s in scores if s is not None]
        return round(sum(valid) / len(valid), 2) if valid else 5.0

    def __repr__(self) -> str:
        return f"<Destination {self.city_name}, {self.country}>"
