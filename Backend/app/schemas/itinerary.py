import json
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ── Activity structure ─────────────────────────────────────────────────────────

class Activity(BaseModel):
    time:        str             # "Morning" | "Afternoon" | "Evening"
    name:        str
    description: str
    location:    Optional[str]  = None
    cost:        Optional[str]  = None   # e.g. "₹200–₹400"
    tips:        Optional[str]  = None


class DayPlan(BaseModel):
    day_number:     int
    title:          str
    activities:     list[Activity]
    estimated_cost: Optional[float]
    notes:          Optional[str]        # AI tips for the day


# ── Request schemas ────────────────────────────────────────────────────────────

class GenerateItineraryRequest(BaseModel):
    trip_id: str = Field(..., description="UUID of an existing trip")


# ── Response schemas ───────────────────────────────────────────────────────────

class ItineraryDayResponse(BaseModel):
    id:             str
    trip_id:        str
    day_number:     int
    title:          Optional[str]
    activities:     Optional[list[Activity]]
    estimated_cost: Optional[float]
    notes:          Optional[str]
    created_at:     datetime
    updated_at:     datetime

    model_config = {"from_attributes": True}

    @field_validator("activities", mode="before")
    @classmethod
    def parse_activities(cls, v):
        if isinstance(v, str):
            try:
                raw = json.loads(v)
                if isinstance(raw, list):
                    return raw
                # Wrapped dict (legacy)
                return raw.get("activities", [])
            except (ValueError, TypeError):
                return []
        return v or []


class ItineraryResponse(BaseModel):
    trip_id:         str
    destination:     str
    total_days:      int
    total_cost:      float
    days:            list[ItineraryDayResponse]
    generated_at:    datetime


class ItineraryRawOut(BaseModel):
    trip_id:            str
    itinerary_markdown: str


# ── Backwards compat aliases ──────────────────────────────────────────────────
ItineraryOut              = ItineraryDayResponse
ItineraryGenerateRequest  = GenerateItineraryRequest
