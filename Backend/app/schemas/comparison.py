from typing import Literal, Optional
from pydantic import BaseModel, Field

TravelerType = Literal["solo", "couple", "family", "friends", "backpacker"]


# ── Request ────────────────────────────────────────────────────────────────────

class DestinationCompareRequest(BaseModel):
    destination1:  str          = Field(..., min_length=2, examples=["Goa"])
    destination2:  str          = Field(..., min_length=2, examples=["Gokarna"])
    traveler_type: Optional[TravelerType] = Field(None, examples=["couple"])
    budget:        Optional[float]        = Field(None, gt=0, examples=[15000])


# ── Per-destination scores ─────────────────────────────────────────────────────

class DestinationScoreDetail(BaseModel):
    destination:          str
    country:              str
    avg_budget_score:     float
    safety_score:         float
    weather_score:        float
    crowd_score:          float
    nightlife_score:      float
    food_score:           float
    adventure_score:      float
    family_friendly_score: float
    overall_score:        float
    pros:                 list[str]
    cons:                 list[str]
    best_for:             list[str]   # traveler types this destination suits
    best_season:          Optional[str]
    known_for:            Optional[str]


# ── Factor comparison ──────────────────────────────────────────────────────────

class FactorComparison(BaseModel):
    factor:        str
    dest1_score:   float
    dest2_score:   float
    winner:        str
    insight:       str


# ── Full response ──────────────────────────────────────────────────────────────

class DestinationCompareOut(BaseModel):
    destination1:          DestinationScoreDetail
    destination2:          DestinationScoreDetail
    factor_comparisons:    list[FactorComparison]
    winner:                str
    recommendation:        str           # narrative summary
    best_for_traveler:     Optional[str] # if traveler_type was provided
    ai_insight:            Optional[str] # Gemini-generated insight
    source:                str           # "database" | "heuristic"


# ── Backwards compat aliases ───────────────────────────────────────────────────

class CompareRequest(BaseModel):
    destination1: str
    destination2: str
    traveler_type: Optional[TravelerType] = None
    budget: Optional[float] = None


class CompareScore(BaseModel):
    destination:   str
    budget_score:  float
    safety_score:  float
    weather_score: float
    crowd_score:   float
    nightlife_score: float
    overall_score: float


class CompareOut(BaseModel):
    destination1:   CompareScore
    destination2:   CompareScore
    recommendation: str
    winner:         str
