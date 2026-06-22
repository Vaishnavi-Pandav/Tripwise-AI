from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

class TripExportData(BaseModel):
    trip_id: str
    destination: str
    source: str
    budget: float
    days: int
    travelers: int
    travel_mode: Optional[str]
    trip_status: str
    budget_breakdown: Optional[dict]
    itinerary: Optional[list]
    hotel_recommendations: Optional[list]
    weather_summary: Optional[str]
    hidden_gems: Optional[list]
    route_info: Optional[dict]
    generated_at: datetime

class ExportHistoryOut(BaseModel):
    id: str
    trip_id: str
    exported_at: datetime
    model_config = {"from_attributes": True}
