import json
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

PackageTypeType = Literal["budget", "standard", "premium", "luxury"]


# ── Request schemas ────────────────────────────────────────────────────────────

class PackageCreate(BaseModel):
    agency_name:         Optional[str]          = Field(None, max_length=255)
    package_name:        str                    = Field(..., min_length=2, max_length=255,
                                                         examples=["Goa Beach Getaway 4N/5D"])
    package_type:        PackageTypeType        = Field("standard", examples=["premium"])
    destination:         str                    = Field(..., min_length=2, max_length=255,
                                                         examples=["Goa"])
    duration_days:       int                    = Field(..., ge=1, examples=[5])
    price:               float                  = Field(..., gt=0, examples=[12999])
    package_description: Optional[str]          = None
    inclusions:          Optional[list[str]]    = Field(None, examples=[["Flights","Hotel","Meals"]])
    exclusions:          Optional[list[str]]    = Field(None, examples=[["Visa","Insurance"]])
    rating:              Optional[float]        = Field(None, ge=0, le=5, examples=[4.3])
    image_url:           Optional[str]          = None

    @field_validator("inclusions", "exclusions", mode="before")
    @classmethod
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                return []
        return v


class PackageUpdate(BaseModel):
    agency_name:         Optional[str]       = Field(None, max_length=255)
    package_name:        Optional[str]       = Field(None, min_length=2, max_length=255)
    package_type:        Optional[PackageTypeType] = None
    duration_days:       Optional[int]       = Field(None, ge=1)
    price:               Optional[float]     = Field(None, gt=0)
    package_description: Optional[str]       = None
    inclusions:          Optional[list[str]] = None
    exclusions:          Optional[list[str]] = None
    rating:              Optional[float]     = Field(None, ge=0, le=5)
    image_url:           Optional[str]       = None


# ── Response schemas ───────────────────────────────────────────────────────────

class PackageOut(BaseModel):
    id:                  str
    agency_name:         Optional[str]
    package_name:        str
    package_type:        Optional[str]
    destination:         str
    duration_days:       int
    price:               float
    package_description: Optional[str]
    inclusions:          Optional[list[str]]
    exclusions:          Optional[list[str]]
    rating:              Optional[float]
    image_url:           Optional[str]
    created_at:          datetime
    updated_at:          datetime

    model_config = {"from_attributes": True}

    @field_validator("inclusions", "exclusions", mode="before")
    @classmethod
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                return []
        return v or []


class PackageListResponse(BaseModel):
    packages:    list[PackageOut]
    total:       int
    page:        int
    page_size:   int
    total_pages: int


class PackageRecommendationOut(BaseModel):
    package_id:           str
    package_name:         str
    agency_name:          Optional[str]
    destination:          str
    duration_days:        int
    price:                float
    package_type:         Optional[str]
    rating:               Optional[float]
    inclusions:           Optional[list[str]]
    image_url:            Optional[str]
    recommendation_score: float
    score_breakdown:      dict[str, float]


class PackageRecommendationsOut(BaseModel):
    trip_id:              str
    destination:          str
    trip_budget:          float
    trip_days:            int
    recommended_packages: list[PackageRecommendationOut]
    total_found:          int


# ── Compare schemas ────────────────────────────────────────────────────────────

class PackageCompareRequest(BaseModel):
    package_ids: list[str] = Field(..., min_length=2, max_length=5,
                                   examples=[["uuid1", "uuid2"]])


class PackageCompareItem(BaseModel):
    package_id:   str
    package_name: str
    agency_name:  Optional[str]
    destination:  str
    duration_days: int
    price:        float
    package_type: Optional[str]
    rating:       Optional[float]
    inclusions:   list[str]
    exclusions:   list[str]
    value_score:  float    # price / duration / rating composite


class PackageCompareOut(BaseModel):
    packages:              list[PackageCompareItem]
    cheapest:              str     # package_name
    highest_rated:         str     # package_name
    best_duration_match:   str     # package_name
    best_value:            str     # package_name
    recommendation:        str     # narrative summary
    price_difference:      float
    common_inclusions:     list[str]
    unique_to_each:        dict[str, list[str]]   # {package_name: unique inclusions}
