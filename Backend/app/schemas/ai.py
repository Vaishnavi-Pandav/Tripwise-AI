from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ── Chat request / response ────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message:  str           = Field(..., min_length=1, max_length=2000,
                                    examples=["Suggest a Goa trip under ₹15000"])
    trip_id:  Optional[str] = Field(None, examples=["uuid-of-existing-trip"],
                                    description="Optional trip UUID for context-aware responses")

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatResponse(BaseModel):
    reply:      str
    trip_context_used: bool = False   # True when trip context was injected


# ── Chat history ───────────────────────────────────────────────────────────────

class ChatHistoryResponse(BaseModel):
    id:           str
    user_id:      str
    trip_id:      Optional[str]
    user_message: str
    ai_response:  str
    created_at:   datetime

    model_config = {"from_attributes": True}


class ChatHistoryListResponse(BaseModel):
    history:   list[ChatHistoryResponse]
    total:     int
    page:      int
    page_size: int


# ── Itinerary generation (public endpoint) ────────────────────────────────────

class TripGenerationRequest(BaseModel):
    source:      str   = Field(..., min_length=2, examples=["Mumbai"])
    destination: str   = Field(..., min_length=2, examples=["Goa"])
    days:        int   = Field(..., ge=1, examples=[4])
    travelers:   int   = Field(..., ge=1, examples=[2])
    budget:      float = Field(..., gt=0, examples=[15000])


class ItineraryResponse(BaseModel):
    itinerary: str


# ── Trip context (internal — not exposed as API schema) ───────────────────────

class TripContext(BaseModel):
    destination:     str
    source:          str
    budget:          float
    number_of_days:  int
    number_of_travelers: int
    travel_mode:     Optional[str]
    trip_status:     str
