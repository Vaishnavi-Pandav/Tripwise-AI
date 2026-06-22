from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Request ────────────────────────────────────────────────────────────────────

class RouteRequest(BaseModel):
    source:      str   = Field(..., min_length=2, examples=["Pune"])
    destination: str   = Field(..., min_length=2, examples=["Goa"])
    travelers:   int   = Field(1,  ge=1, examples=[2])
    budget:      Optional[float] = Field(None, gt=0, examples=[5000])


class NearbyRequest(BaseModel):
    latitude:  float = Field(..., ge=-90,  le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(10.0, ge=1, le=100)


# ── Per-mode detail ────────────────────────────────────────────────────────────

class TravelModeDetail(BaseModel):
    mode:              str
    estimated_cost:    float        # ₹ per person
    total_cost:        float        # ₹ for all travelers
    duration_hours:    float
    duration_label:    str          # "9h 30m"
    pros:              list[str]
    cons:              list[str]
    recommended:       bool         # true for the best option
    savings_vs_flight: Optional[float] = None


# ── Route response ─────────────────────────────────────────────────────────────

class RouteResponse(BaseModel):
    source:          str
    destination:     str
    distance_km:     float
    suggested_modes: list[TravelModeDetail]
    best_mode:       str
    recommendation:  str            # narrative smart recommendation
    source_type:     str            # "heuristic" | "api"


# ── Nearby attraction ──────────────────────────────────────────────────────────

class NearbyAttractionResponse(BaseModel):
    name:          str
    category:      Optional[str]
    distance_km:   float
    latitude:      Optional[float]
    longitude:     Optional[float]
    description:   Optional[str]
    estimated_cost: Optional[float]
    source:        str = "database"


# ── Route history ──────────────────────────────────────────────────────────────

class RouteHistoryOut(BaseModel):
    id:                  str
    source_location:     str
    destination_location: str
    distance_km:         Optional[float]
    duration_minutes:    Optional[int]
    travel_mode:         Optional[str]
    estimated_cost:      Optional[float]
    created_at:          datetime

    model_config = {"from_attributes": True}
