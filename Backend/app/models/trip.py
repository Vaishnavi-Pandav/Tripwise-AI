from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    source = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    days = Column(Integer, nullable=False)
    travelers = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)

    # AI-generated markdown itinerary
    itinerary = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="trips")
