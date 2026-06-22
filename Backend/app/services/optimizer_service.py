import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.trip import Trip
from app.models.expenses import TripExpenses
from app.models.hotel import Hotel
from app.models.user import User
from app.schemas.optimizer import BudgetOptimizeResponse, OptimizeSuggestion

logger = logging.getLogger("tripwise")

class OptimizerService:
    @staticmethod
    def optimize(db: Session, trip_id: str, user: User) -> BudgetOptimizeResponse:
        trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user.id).first()
        if not trip:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        expense = db.query(TripExpenses).filter(TripExpenses.trip_id == trip_id).first()
        current_cost = float(trip.total_estimated_cost or trip.budget)

        suggestions: list[OptimizeSuggestion] = []
        recs: list[str] = []
        savings = 0.0

        # Route optimization
        mode = (trip.travel_mode or "flight").lower()
        if mode == "flight":
            route_save = current_cost * 0.15
            savings += route_save
            suggestions.append(OptimizeSuggestion(
                category="route", current="Flight",
                suggestion="Switch to train — saves up to 50% on transport",
                savings=round(route_save, 2),
            ))
            recs.append("✈️→🚂 Choose train instead of flight to save ₹{:,.0f}".format(route_save))

        # Hotel optimization
        if expense and float(expense.accommodation_cost or 0) > current_cost * 0.35:
            hotel_save = float(expense.accommodation_cost) * 0.30
            savings += hotel_save
            suggestions.append(OptimizeSuggestion(
                category="hotel", current="Current hotel",
                suggestion="Switch to a budget/standard hotel to reduce accommodation cost by 30%",
                savings=round(hotel_save, 2),
            ))
            recs.append("🏨 Opt for a budget hotel to save ₹{:,.0f}".format(hotel_save))

        # Activity optimization
        if expense and float(expense.activity_cost or 0) > current_cost * 0.18:
            act_save = float(expense.activity_cost) * 0.40
            savings += act_save
            suggestions.append(OptimizeSuggestion(
                category="activity", current="Paid activities",
                suggestion="Replace 40% of paid activities with free local attractions",
                savings=round(act_save, 2),
            ))
            recs.append("🎯 Visit free attractions and hidden gems to save ₹{:,.0f}".format(act_save))

        # Food optimization
        if expense and float(expense.food_cost or 0) > current_cost * 0.22:
            food_save = float(expense.food_cost) * 0.35
            savings += food_save
            suggestions.append(OptimizeSuggestion(
                category="food", current="Restaurants",
                suggestion="Eat at local dhabas/street food instead of tourist restaurants",
                savings=round(food_save, 2),
            ))
            recs.append("🍽️ Eat at local spots to save ₹{:,.0f} on food".format(food_save))

        if not recs:
            recs.append("✅ Your trip budget is already well-optimized!")

        optimized = round(max(current_cost - savings, current_cost * 0.5), 2)
        savings_pct = round((savings / current_cost) * 100, 1) if current_cost else 0

        logger.info(f"Budget optimized: trip={trip_id} savings=₹{savings:.0f}")
        return BudgetOptimizeResponse(
            trip_id=trip_id,
            destination=trip.destination_location,
            current_cost=current_cost,
            optimized_cost=optimized,
            savings=round(savings, 2),
            savings_pct=savings_pct,
            recommendations=recs,
            suggestions=suggestions,
        )
