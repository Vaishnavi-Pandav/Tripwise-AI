from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Attraction schemas ────────────────────────────────────────────────────────

class AttractionOut(BaseModel):
    id:                   str
    city:                 str
    attraction_name:      str
    category:             Optional[str]
    description:          Optional[str]
    entry_fee:            Optional[float]
    rating:               Optional[float]
    location_coordinates: Optional[Any]
    image_url:            Optional[str]

    model_config = {"from_attributes": True}


# ── Hidden Gem schemas ────────────────────────────────────────────────────────

class HiddenGemOut(BaseModel):
    id:                str
    city:              str
    place_name:        str
    category:          Optional[str]
    description:       Optional[str]
    estimated_cost:    Optional[float]
    crowd_level:       Optional[str]
    best_time_to_visit: Optional[str]
    traveler_type:     Optional[str]
    recommended_for:   Optional[str]
    image_url:         Optional[str]
    latitude:          Optional[float]
    longitude:         Optional[float]
    created_at:        Optional[datetime]
    updated_at:        Optional[datetime]

    model_config = {"from_attributes": True}


# ── Recommendation schemas ────────────────────────────────────────────────────

class HiddenGemRecommendationItem(BaseModel):
    id:              str
    name:            str
    city:            str
    category:        Optional[str]
    estimated_cost:  Optional[float]
    crowd_level:     Optional[str]
    best_time:       Optional[str]
    image_url:       Optional[str]
    reason:          str       # why this gem was recommended
    best_for:        str       # traveler type fit
    travel_tips:     list[str] # practical tips


class HiddenGemRecommendRequest(BaseModel):
    trip_id: str = Field(..., description="UUID of an existing trip")


class HiddenGemRecommendResponse(BaseModel):
    trip_id:         str
    destination:     str
    traveler_type:   str
    recommendations: list[HiddenGemRecommendationItem]
    total_found:     int
