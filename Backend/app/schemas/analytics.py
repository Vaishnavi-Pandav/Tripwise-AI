from typing import Optional
from pydantic import BaseModel

class DestinationFrequency(BaseModel):
    destination: str
    count: int

class AnalyticsDashboardOut(BaseModel):
    total_trips: int
    completed_trips: int
    planned_trips: int
    cancelled_trips: int
    draft_trips: int
    favorite_destination: Optional[str]
    total_budget_spent: float
    average_trip_cost: float
    total_days_travelled: int
    top_destinations: list[DestinationFrequency]
    most_used_travel_mode: Optional[str]
