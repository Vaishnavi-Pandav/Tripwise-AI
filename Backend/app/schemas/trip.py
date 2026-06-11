from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TripCreate(BaseModel):
    source: str
    destination: str
    days: int
    travelers: int
    budget: float


class TripOut(BaseModel):
    id: int
    source: str
    destination: str
    days: int
    travelers: int
    budget: float
    itinerary: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
