from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    price_per_night = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)
    amenities = Column(Text, nullable=True)       # JSON string of amenities list
    image_url = Column(String(500), nullable=True)
    tier = Column(String(50), nullable=True)      # "budget" | "mid-range" | "luxury"
    created_at = Column(DateTime, default=datetime.utcnow)
