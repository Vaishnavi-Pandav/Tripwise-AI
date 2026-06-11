import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.budget import (
    BudgetBreakdownOut,
    BudgetInsightsOut,
    BudgetRequest,
    TripBudgetCalculateRequest,
    TripExpenseOut,
)
from app.services.budget_service import BudgetService

logger = logging.getLogger("tripwise")
router = APIRouter(prefix="/budget", tags=["Budget"])
_svc   = BudgetService()


# ── POST /budget/calculate ─────────────────────────────────────────────────────
# Standalone estimate — no trip_id needed

@router.post(
    "/calculate",
    response_model=BudgetBreakdownOut,
    summary="Quick budget estimate (no trip required)",
    description="""
Estimate a trip budget without creating a trip.

**Example request:**
```json
{
  "destination": "Goa",
  "number_of_days": 4,
  "number_of_travelers": 2,
  "total_budget": 15000,
  "travel_mode": "flight",
  "accommodation_type": "mid-range",
  "destination_category": "beach"
}
```
""",
)
def calculate_budget_quick(
    payload: BudgetRequest,
    current_user: User = Depends(get_current_user),
):
    b = _svc.calculate_breakdown(
        total_budget=payload.total_budget,
        days=payload.number_of_days,
        travelers=payload.number_of_travelers,
        travel_mode=payload.travel_mode,
        accommodation_type=payload.accommodation_type,
        destination_category=payload.destination_category or "general",
    )
    return BudgetBreakdownOut(
        transport_cost=b.transport_cost,
        accommodation_cost=b.accommodation_cost,
        food_cost=b.food_cost,
        activity_cost=b.activity_cost,
        miscellaneous_cost=b.miscellaneous_cost,
        total_estimated_cost=b.total,
        budget_remaining=b.budget_remaining,
        per_person_cost=b.per_person,
        daily_cost_per_person=b.daily_per_person,
    )


# ── POST /budget/calculate/{trip_id} ──────────────────────────────────────────

@router.post(
    "/calculate/{trip_id}",
    response_model=TripExpenseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate & save budget for a trip",
    description="""
Calculate budget for an existing trip and save it to the database.
The trip's `total_estimated_cost` is also updated automatically.

**Example request:**
```json
{
  "accommodation_type": "mid-range",
  "destination_category": "beach"
}
```

**Example response:**
```json
{
  "transport_cost": 4800,
  "accommodation_cost": 4200,
  "food_cost": 2700,
  "activity_cost": 1650,
  "miscellaneous_cost": 1050,
  "total_cost": 14400,
  "budget_remaining": 600
}
```
""",
)
def calculate_and_save(
    trip_id: str,
    payload: TripBudgetCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.calculate_budget(
        db=db,
        trip_id=trip_id,
        user=current_user,
        accommodation_type=payload.accommodation_type,
        destination_category=payload.destination_category or "general",
        override_travel_mode=payload.override_travel_mode,
    )


# ── GET /budget/{trip_id} ─────────────────────────────────────────────────────

@router.get(
    "/{trip_id}",
    response_model=TripExpenseOut,
    summary="Get saved budget for a trip",
)
def get_budget(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.get_budget(db, trip_id, current_user)


# ── PUT /budget/{trip_id} ─────────────────────────────────────────────────────

@router.put(
    "/{trip_id}",
    response_model=TripExpenseOut,
    summary="Recalculate budget after trip changes",
    description="""
Recalculate and overwrite the saved budget. 
Useful after changing trip duration, travelers, or travel mode.

Send only the fields you want to change — the rest are taken from the saved budget.
""",
)
def update_budget(
    trip_id: str,
    payload: TripBudgetCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.update_budget(
        db=db,
        trip_id=trip_id,
        user=current_user,
        accommodation_type=payload.accommodation_type,
        destination_category=payload.destination_category,
        override_travel_mode=payload.override_travel_mode,
    )


# ── GET /budget/insights/{trip_id} ────────────────────────────────────────────

@router.get(
    "/insights/{trip_id}",
    response_model=BudgetInsightsOut,
    summary="Smart budget insights & recommendations",
    description="""
Returns AI-style budget analysis with actionable recommendations.

**Example response:**
```json
{
  "budget_status": "Tight Budget",
  "total_budget": 15000,
  "total_cost": 13500,
  "remaining_amount": 1500,
  "utilisation_pct": 90.0,
  "recommendations": [
    "Switch to train to save up to 50% on transport costs.",
    "Budget hostels can free up budget for activities."
  ],
  "category_breakdown": {
    "Transport": 4800,
    "Accommodation": 4200,
    "Food": 2700,
    "Activities": 1650,
    "Miscellaneous": 150
  },
  "cost_per_day": 3375.0,
  "cost_per_person": 6750.0
}
```
""",
)
def budget_insights(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.get_insights(db, trip_id, current_user)
