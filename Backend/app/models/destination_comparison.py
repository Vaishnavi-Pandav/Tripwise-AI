import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, Column, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class DestinationComparison(Base):
    __tablename__ = "destination_comparisons"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_one = Column(String(255), nullable=False, index=True)
    destination_two = Column(String(255), nullable=False, index=True)
    budget_score    = Column(Numeric(4, 2), nullable=True)
    safety_score    = Column(Numeric(4, 2), nullable=True)
    weather_score   = Column(Numeric(4, 2), nullable=True)
    crowd_score     = Column(Numeric(4, 2), nullable=True)
    nightlife_score = Column(Numeric(4, 2), nullable=True)

    __table_args__ = (
        CheckConstraint("budget_score    >= 0 AND budget_score    <= 10", name="ck_budget_score"),
        CheckConstraint("safety_score    >= 0 AND safety_score    <= 10", name="ck_safety_score"),
        CheckConstraint("weather_score   >= 0 AND weather_score   <= 10", name="ck_weather_score"),
        CheckConstraint("crowd_score     >= 0 AND crowd_score     <= 10", name="ck_crowd_score"),
        CheckConstraint("nightlife_score >= 0 AND nightlife_score <= 10", name="ck_nightlife_score"),
    )

    @property
    def overall_score(self) -> Decimal | None:
        scores = [self.budget_score, self.safety_score, self.weather_score,
                  self.crowd_score, self.nightlife_score]
        valid = [s for s in scores if s is not None]
        if not valid:
            return None
        return round(sum(valid) / len(valid), 2)
