from pydantic import BaseModel


class TripGenerationRequest(BaseModel):
    source: str
    destination: str
    days: int
    travelers: int
    budget: float


class ItineraryResponse(BaseModel):
    itinerary: str


class BudgetBreakdownRequest(BaseModel):
    destination: str
    days: int
    travelers: int
    total_budget: float


class RouteRequest(BaseModel):
    source: str
    destination: str
    days: int
