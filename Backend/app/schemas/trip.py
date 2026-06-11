from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

# ── Allowed values ─────────────────────────────────────────────────────────────

TripStatusType  = Literal["draft", "planned", "completed", "cancelled"]
TravelModeType  = Literal["flight", "train", "road", "mixed"]


# ── Request schemas ────────────────────────────────────────────────────────────

class TripCreate(BaseModel):
    source_location:      str           = Field(..., min_length=2, max_length=255, examples=["Mumbai"])
    destination_location: str           = Field(..., min_length=2, max_length=255, examples=["Goa"])
    budget:               float         = Field(..., gt=0, examples=[15000])
    number_of_days:       int           = Field(..., ge=1, examples=[4])
    number_of_travelers:  int           = Field(..., ge=1, examples=[2])
    travel_mode:          Optional[TravelModeType] = Field(None, examples=["flight"])

    @field_validator("source_location", "destination_location")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def source_and_dest_differ(self) -> "TripCreate":
        if self.source_location.lower() == self.destination_location.lower():
            raise ValueError("Source and destination cannot be the same")
        return self


class TripUpdate(BaseModel):
    source_location:      Optional[str]            = Field(None, min_length=2, max_length=255)
    destination_location: Optional[str]            = Field(None, min_length=2, max_length=255)
    budget:               Optional[float]          = Field(None, gt=0)
    number_of_days:       Optional[int]            = Field(None, ge=1)
    number_of_travelers:  Optional[int]            = Field(None, ge=1)
    travel_mode:          Optional[TravelModeType] = None
    trip_status:          Optional[TripStatusType] = None


# ── Response schemas ───────────────────────────────────────────────────────────

class TripResponse(BaseModel):
    id:                   str
    user_id:              str
    source_location:      str
    destination_location: str
    budget:               float
    number_of_days:       int
    number_of_travelers:  int
    travel_mode:          Optional[str]
    total_estimated_cost: Optional[float]
    trip_status:          str
    created_at:           datetime
    updated_at:           datetime

    model_config = {"from_attributes": True}


class TripListResponse(BaseModel):
    trips:       list[TripResponse]
    total:       int
    page:        int
    page_size:   int
    total_pages: int


# ── Dashboard schema ───────────────────────────────────────────────────────────

class TripDashboardStats(BaseModel):
    total_trips:     int
    draft_trips:     int
    planned_trips:   int
    completed_trips: int
    cancelled_trips: int
    total_budget:    float
    avg_days:        float


# ── Backwards compat alias ─────────────────────────────────────────────────────
TripOut = TripResponse
