import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name     = Column(String(150), nullable=False)
    email         = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    profile_image = Column(Text, nullable=True)
    created_at    = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at    = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    trips            = relationship("Trip",             back_populates="owner",    cascade="all, delete-orphan")
    saved_trips      = relationship("SavedTrip",        back_populates="user",     cascade="all, delete-orphan")
    chat_history     = relationship("AIChatHistory",    back_populates="user",     cascade="all, delete-orphan")
    reviews          = relationship("Review",           back_populates="user",     cascade="all, delete-orphan")
    preferences      = relationship("UserPreferences",  back_populates="user",     uselist=False, cascade="all, delete-orphan")
    ai_suggestions   = relationship("AITripSuggestion", back_populates="user",     cascade="all, delete-orphan")
