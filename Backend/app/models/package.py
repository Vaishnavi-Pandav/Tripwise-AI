from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    highlights = Column(Text, nullable=True)      # JSON string of highlights list
    image_url = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True) # "adventure" | "cultural" | "beach" etc.
    created_at = Column(DateTime, default=datetime.utcnow)
