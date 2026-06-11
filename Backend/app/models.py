from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="owner", cascade="all, delete-orphan")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    destination = Column(String(255), nullable=False)
    duration_days = Column(Integer, nullable=False)
    budget = Column(String(100), nullable=False)
    travel_style = Column(String(100), nullable=True)   # e.g. "adventure", "relaxation"
    num_travelers = Column(Integer, default=1)

    # AI-generated itinerary stored as JSON string
    itinerary = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="trips")
