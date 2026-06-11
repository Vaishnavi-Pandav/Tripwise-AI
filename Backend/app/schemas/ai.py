from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class TripGenerationRequest(BaseModel):
    source: str
    destination: str
    days: int
    travelers: int
    budget: float


class ItineraryResponse(BaseModel):
    itinerary: str
