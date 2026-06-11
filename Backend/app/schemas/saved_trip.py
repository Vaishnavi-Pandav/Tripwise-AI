from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.trip import TripOut


class SavedTripCreate(BaseModel):
    trip_id: str


class SavedTripOut(BaseModel):
    id: str
    user_id: str
    trip_id: str
    created_at: datetime
    trip: Optional[TripOut] = None

    model_config = {"from_attributes": True}
