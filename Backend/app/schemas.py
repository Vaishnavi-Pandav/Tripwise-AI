from pydantic import BaseModel


class TripGenerationRequest(BaseModel):
    source: str
    destination: str
    days: int
    travelers: int
    budget: float
