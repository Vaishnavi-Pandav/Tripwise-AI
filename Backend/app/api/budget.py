from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.budget import BudgetBreakdownOut, BudgetRequest
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budget", tags=["Budget"])

_svc = BudgetService()


@router.post("/calculate", response_model=BudgetBreakdownOut, summary="Calculate budget breakdown")
def calculate_budget(
    payload: BudgetRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Estimate costs split across transport, hotel, food, activities,
    and miscellaneous for a trip.
    """
    b = _svc.calculate_breakdown(
        total_budget=payload.total_budget,
        days=payload.number_of_days,
        travelers=payload.number_of_travelers,
        travel_mode=payload.travel_mode,
    )
    return BudgetBreakdownOut(
        transport_cost=b.transport_cost,
        hotel_cost=b.hotel_cost,
        food_cost=b.food_cost,
        activity_cost=b.activity_cost,
        miscellaneous_cost=b.miscellaneous_cost,
        total_estimated_cost=b.total,
        per_person_cost=b.per_person,
        daily_cost_per_person=b.daily_per_person,
    )
