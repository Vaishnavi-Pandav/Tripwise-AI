from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ──────────────────────────────────────────────
# Auth schemas
# ──────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ──────────────────────────────────────────────
# Trip schemas
# ──────────────────────────────────────────────

class TripGenerationRequest(BaseModel):
    source: str
    destination: str
    days: int
    travelers: int
    budget: float


class TripOut(BaseModel):
    id: int
    source: str
    destination: str
    days: int
    travelers: int
    budget: float
    itinerary: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
