from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class TripCreate(BaseModel):
    source_location: str
    destination_location: str
    budget: float
    number_of_days: int
    number_of_travelers: int
    travel_mode: Optional[str] = None  # flight | train | road | mixed

    @field_validator("number_of_days", "number_of_travelers")
    @classmethod
    def must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Must be greater than 0")
        return v

    @field_validator("budget")
    @classmethod
    def budget_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Budget must be positive")
        return v


class TripUpdate(BaseModel):
    source_location: Optional[str] = None
    destination_location: Optional[str] = None
    budget: Optional[float] = None
    number_of_days: Optional[int] = None
    number_of_travelers: Optional[int] = None
    travel_mode: Optional[str] = None
    trip_status: Optional[str] = None


class TripOut(BaseModel):
    id: str
    user_id: str
    source_location: str
    destination_location: str
    budget: float
    number_of_days: int
    number_of_travelers: int
    travel_mode: Optional[str]
    total_estimated_cost: Optional[float]
    trip_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
