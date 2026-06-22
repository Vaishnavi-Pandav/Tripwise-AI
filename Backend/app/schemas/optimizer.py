from typing import Optional
from pydantic import BaseModel

class OptimizeSuggestion(BaseModel):
    category: str        # route|hotel|activity|package
    current: str
    suggestion: str
    savings: float

class BudgetOptimizeResponse(BaseModel):
    trip_id: str
    destination: str
    current_cost: float
    optimized_cost: float
    savings: float
    savings_pct: float
    recommendations: list[str]
    suggestions: list[OptimizeSuggestion]
