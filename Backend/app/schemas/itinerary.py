from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class ItineraryGenerateRequest(BaseModel):
    trip_id: str
    source_location: str
    destination_location: str
    number_of_days: int
    number_of_travelers: int
    budget: float
    travel_mode: Optional[str] = None


class ItineraryOut(BaseModel):
    id: str
    trip_id: str
    day_number: int
    title: Optional[str]
    activities: Optional[Any]
    estimated_cost: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class ItineraryRawOut(BaseModel):
    trip_id: str
    itinerary_markdown: str
