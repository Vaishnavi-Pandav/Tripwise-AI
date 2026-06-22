from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

# ── Allowed types ──────────────────────────────────────────────────────────────

TravelModeType       = Literal["flight", "train", "road", "mixed", "bus", "car"]
AccommodationType    = Literal["budget", "mid-range", "luxury"]
DestinationCategory  = Literal["beach", "mountain", "city", "cultural", "adventure", "general"]


# ── Request schemas ────────────────────────────────────────────────────────────

class BudgetRequest(BaseModel):
    """Standalone budget calculation — no trip_id required."""
    destination:          str                          = Field(..., examples=["Goa"])
    number_of_days:       int                          = Field(..., ge=1, examples=[4])
    number_of_travelers:  int                          = Field(..., ge=1, examples=[2])
    total_budget:         float                        = Field(..., gt=0, examples=[15000])
    travel_mode:          TravelModeType               = Field("flight", examples=["flight"])
    accommodation_type:   AccommodationType            = Field("mid-range", examples=["mid-range"])
    destination_category: Optional[DestinationCategory] = Field("general", examples=["beach"])

    @field_validator("total_budget")
    @classmethod
    def budget_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Budget must be positive")
        return v


class TripBudgetCalculateRequest(BaseModel):
    """Attach budget calculation to an existing trip."""
    accommodation_type:    AccommodationType            = Field("mid-range")
    destination_category:  Optional[DestinationCategory] = Field("general")
    override_travel_mode:  Optional[TravelModeType]     = Field(None)


# ── Response schemas ───────────────────────────────────────────────────────────

class BudgetBreakdownOut(BaseModel):
    transport_cost:        float
    accommodation_cost:    float
    food_cost:             float
    activity_cost:         float
    miscellaneous_cost:    float
    total_estimated_cost:  float
    budget_remaining:      float
    per_person_cost:       float
    daily_cost_per_person: float
    currency:              str = "INR"

    # Backwards compat
    @property
    def hotel_cost(self) -> float:
        return self.accommodation_cost


class TripExpenseOut(BaseModel):
    id:                   str
    trip_id:              str
    transport_cost:       float
    accommodation_cost:   float
    food_cost:            float
    activity_cost:        float
    miscellaneous_cost:   float
    total_cost:           float
    budget_remaining:     float
    accommodation_type:   Optional[str]
    travel_mode:          Optional[str]
    destination_category: Optional[str]
    created_at:           datetime
    updated_at:           datetime

    model_config = {"from_attributes": True}


class BudgetInsightsOut(BaseModel):
    budget_status:     str              # "Within Budget" | "Over Budget" | "Tight Budget"
    total_budget:      float
    total_cost:        float
    remaining_amount:  float
    utilisation_pct:   float            # percentage of budget used
    recommendations:   list[str]
    category_breakdown: dict[str, float] # {category: cost}
    cost_per_day:      float
    cost_per_person:   float
