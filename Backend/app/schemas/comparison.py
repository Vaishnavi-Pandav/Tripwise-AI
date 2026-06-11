from typing import Optional
from pydantic import BaseModel


class CompareRequest(BaseModel):
    destination1: str
    destination2: str


class CompareScore(BaseModel):
    destination: str
    budget_score: float
    safety_score: float
    weather_score: float
    crowd_score: float
    nightlife_score: float
    overall_score: float


class CompareOut(BaseModel):
    destination1: CompareScore
    destination2: CompareScore
    recommendation: str
    winner: str
