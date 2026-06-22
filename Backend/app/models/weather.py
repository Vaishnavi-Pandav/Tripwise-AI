import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class WeatherDataCache(Base):
    """
    Caches weather API responses per city per date.
    Unique on (city, forecast_date) — one row per city per day.
    """
    __tablename__ = "weather_data_cache"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city              = Column(String(150), nullable=False, index=True)

    # ── Current weather fields ─────────────────────────────────────────────────
    temperature       = Column(Numeric(5, 2), nullable=True)   # °C
    feels_like        = Column(Numeric(5, 2), nullable=True)   # °C
    humidity          = Column(Numeric(5, 2), nullable=True)   # %
    wind_speed        = Column(Float, nullable=True)            # km/h
    weather_condition = Column(String(100), nullable=True)      # "Rainy", "Clear"
    weather_icon      = Column(String(50),  nullable=True)      # OWM icon code
    rain_probability  = Column(Float, nullable=True)            # 0–100 %

    # ── Timestamps ────────────────────────────────────────────────────────────
    forecast_date     = Column(Date, nullable=False, index=True)
    fetched_at        = Column(DateTime(timezone=True), default=datetime.utcnow,
                               nullable=False)

    __table_args__ = (
        UniqueConstraint("city", "forecast_date", name="uq_weather_city_date"),
    )

    def __repr__(self) -> str:
        return f"<Weather {self.city} {self.forecast_date} {self.temperature}°C>"
