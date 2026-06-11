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

class TripCreate(BaseModel):
    destination: str
    duration_days: int
    budget: str
    travel_style: Optional[str] = None
    num_travelers: int = 1


class TripOut(BaseModel):
    id: int
    destination: str
    duration_days: int
    budget: str
    travel_style: Optional[str]
    num_travelers: int
    itinerary: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
