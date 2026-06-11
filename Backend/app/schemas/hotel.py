from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class HotelCreate(BaseModel):
    city: str
    hotel_name: str
    description: Optional[str] = None
    price_per_night: float
    rating: Optional[float] = None
    address: Optional[str] = None
    image_url: Optional[str] = None
    amenities: Optional[list[str]] = None


class HotelOut(BaseModel):
    id: str
    city: str
    hotel_name: str
    description: Optional[str]
    price_per_night: float
    rating: Optional[float]
    address: Optional[str]
    image_url: Optional[str]
    amenities: Optional[Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class HotelUpdate(BaseModel):
    hotel_name: Optional[str] = None
    description: Optional[str] = None
    price_per_night: Optional[float] = None
    rating: Optional[float] = None
    address: Optional[str] = None
    image_url: Optional[str] = None
    amenities: Optional[list[str]] = None
