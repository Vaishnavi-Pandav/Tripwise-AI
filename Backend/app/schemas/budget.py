from pydantic import BaseModel, field_validator


class BudgetRequest(BaseModel):
    destination: str
    number_of_days: int
    number_of_travelers: int
    total_budget: float
    travel_mode: str = "flight"

    @field_validator("total_budget")
    @classmethod
    def budget_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Budget must be positive")
        return v


class BudgetBreakdownOut(BaseModel):
    transport_cost: float
    hotel_cost: float
    food_cost: float
    activity_cost: float
    miscellaneous_cost: float
    total_estimated_cost: float
    per_person_cost: float
    daily_cost_per_person: float
    currency: str = "USD"
