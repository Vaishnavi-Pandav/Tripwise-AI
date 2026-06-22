import json
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

HotelCategoryType = Literal["budget", "standard", "premium", "luxury"]


# ── Request schemas ────────────────────────────────────────────────────────────

class HotelCreate(BaseModel):
    city:            str             = Field(..., min_length=2, max_length=150, examples=["Goa"])
    hotel_name:      str             = Field(..., min_length=2, max_length=255, examples=["Sea View Resort"])
    description:     Optional[str]   = None
    address:         Optional[str]   = None
    price_per_night: float           = Field(..., gt=0, examples=[2500])
    rating:          Optional[float] = Field(None, ge=0, le=5, examples=[4.5])
    hotel_category:  HotelCategoryType = Field("standard", examples=["premium"])
    amenities:       Optional[list[str]] = Field(None, examples=[["WiFi", "Pool", "AC"]])
    image_url:       Optional[str]   = None
    latitude:        Optional[float] = Field(None, ge=-90,  le=90)
    longitude:       Optional[float] = Field(None, ge=-180, le=180)

    @field_validator("amenities", mode="before")
    @classmethod
    def parse_amenities(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                return []
        return v


class HotelUpdate(BaseModel):
    hotel_name:      Optional[str]   = Field(None, min_length=2, max_length=255)
    description:     Optional[str]   = None
    address:         Optional[str]   = None
    price_per_night: Optional[float] = Field(None, gt=0)
    rating:          Optional[float] = Field(None, ge=0, le=5)
    hotel_category:  Optional[HotelCategoryType] = None
    amenities:       Optional[list[str]] = None
    image_url:       Optional[str]   = None
    latitude:        Optional[float] = Field(None, ge=-90,  le=90)
    longitude:       Optional[float] = Field(None, ge=-180, le=180)


# ── Response schemas ───────────────────────────────────────────────────────────

class HotelResponse(BaseModel):
    id:              str
    city:            str
    hotel_name:      str
    description:     Optional[str]
    address:         Optional[str]
    price_per_night: float
    rating:          Optional[float]
    hotel_category:  Optional[str]
    amenities:       Optional[list[str]]
    image_url:       Optional[str]
    latitude:        Optional[float]
    longitude:       Optional[float]
    created_at:      datetime
    updated_at:      datetime

    model_config = {"from_attributes": True}

    @field_validator("amenities", mode="before")
    @classmethod
    def parse_amenities(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                return []
        return v or []


class HotelListResponse(BaseModel):
    hotels:      list[HotelResponse]
    total:       int
    page:        int
    page_size:   int
    total_pages: int


class HotelRecommendationResponse(BaseModel):
    hotel_id:             str
    hotel_name:           str
    city:                 str
    price_per_night:      float
    rating:               Optional[float]
    hotel_category:       Optional[str]
    amenities:            Optional[list[str]]
    image_url:            Optional[str]
    recommendation_score: float
    score_breakdown:      dict[str, float]  # shows how score was computed

    model_config = {"from_attributes": True}


class HotelRecommendationsOut(BaseModel):
    trip_id:             str
    destination:         str
    budget_per_night:    float
    recommended_hotels:  list[HotelRecommendationResponse]
    total_found:         int


# Backwards compat alias
HotelOut = HotelResponse
