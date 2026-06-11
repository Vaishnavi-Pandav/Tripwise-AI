import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class WeatherDataCache(Base):
    __tablename__ = "weather_data_cache"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city              = Column(String(150), nullable=False, index=True)
    temperature       = Column(Numeric(5, 2), nullable=True)
    weather_condition = Column(String(100), nullable=True)
    humidity          = Column(Numeric(5, 2), nullable=True)
    forecast_date     = Column(Date, nullable=False, index=True)
    fetched_at        = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("city", "forecast_date", name="uq_weather_city_date"),
    )
