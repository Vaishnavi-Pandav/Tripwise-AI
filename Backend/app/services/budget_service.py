import logging
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.expenses import TripExpenses
from app.models.trip import Trip
from app.models.user import User
from app.schemas.budget import BudgetInsightsOut, TripExpenseOut

logger = logging.getLogger("tripwise")


# ── Configuration tables ───────────────────────────────────────────────────────

# Transport weight by travel mode (fraction of total budget)
TRANSPORT_WEIGHTS: dict[str, float] = {
    "flight": 0.32,
    "train":  0.16,
    "bus":    0.08,
    "road":   0.12,
    "car":    0.14,
    "mixed":  0.22,
}

# Accommodation weight by type
ACCOMMODATION_WEIGHTS: dict[str, float] = {
    "budget":    0.20,
    "mid-range": 0.28,
    "luxury":    0.40,
}

# Food weight (per traveler per day as fraction of total)
FOOD_WEIGHT: float = 0.18

# Activity weight by destination category
ACTIVITY_WEIGHTS: dict[str, float] = {
    "beach":     0.10,
    "mountain":  0.12,
    "city":      0.14,
    "cultural":  0.13,
    "adventure": 0.18,
    "general":   0.11,
}

# Miscellaneous is whatever is left (always 5–10%)
MISC_WEIGHT: float = 0.07


# ── Breakdown dataclass ────────────────────────────────────────────────────────

@dataclass
class BudgetBreakdown:
    transport_cost:      float
    accommodation_cost:  float
    food_cost:           float
    activity_cost:       float
    miscellaneous_cost:  float
    total:               float
    budget_remaining:    float
    per_person:          float
    daily_per_person:    float

    # Backwards compat alias
    @property
    def hotel_cost(self) -> float:
        return self.accommodation_cost


# ── Service ────────────────────────────────────────────────────────────────────

class BudgetService:

    # ── Core calculation ──────────────────────────────────────────────────────

    def calculate_breakdown(
        self,
        total_budget:         float,
        days:                 int,
        travelers:            int,
        travel_mode:          str = "flight",
        accommodation_type:   str = "mid-range",
        destination_category: str = "general",
    ) -> BudgetBreakdown:
        """
        Calculate cost breakdown from configurable weight tables.
        Weights are normalised so they always sum to ≤ 1.
        """
        t_w   = TRANSPORT_WEIGHTS.get(travel_mode.lower(),          TRANSPORT_WEIGHTS["flight"])
        a_w   = ACCOMMODATION_WEIGHTS.get(accommodation_type.lower(), ACCOMMODATION_WEIGHTS["mid-range"])
        f_w   = FOOD_WEIGHT
        ac_w  = ACTIVITY_WEIGHTS.get(destination_category.lower(),  ACTIVITY_WEIGHTS["general"])
        mi_w  = MISC_WEIGHT

        # Normalise so sum ≤ 1
        total_w = t_w + a_w + f_w + ac_w + mi_w
        if total_w > 1.0:
            scale = 1.0 / total_w
            t_w, a_w, f_w, ac_w, mi_w = (
                t_w * scale, a_w * scale, f_w * scale,
                ac_w * scale, mi_w * scale,
            )

        transport     = round(total_budget * t_w,  2)
        accommodation = round(total_budget * a_w,  2)
        food          = round(total_budget * f_w,  2)
        activity      = round(total_budget * ac_w, 2)
        misc          = round(total_budget * mi_w, 2)

        total            = round(transport + accommodation + food + activity + misc, 2)
        budget_remaining = round(total_budget - total, 2)
        per_person       = round(total / max(travelers, 1), 2)
        daily_pp         = round(per_person / max(days, 1), 2)

        return BudgetBreakdown(
            transport_cost=transport,
            accommodation_cost=accommodation,
            food_cost=food,
            activity_cost=activity,
            miscellaneous_cost=misc,
            total=total,
            budget_remaining=budget_remaining,
            per_person=per_person,
            daily_per_person=daily_pp,
        )

    # ── DB operations ─────────────────────────────────────────────────────────

    def calculate_budget(
        self,
        db: Session,
        trip_id: str,
        user: User,
        accommodation_type:   str = "mid-range",
        destination_category: str = "general",
        override_travel_mode: Optional[str] = None,
    ) -> TripExpenses:
        """Calculate budget for a trip and save/update the TripExpenses record."""
        trip = self._get_trip(db, trip_id, user)

        travel_mode = override_travel_mode or trip.travel_mode or "flight"
        breakdown = self.calculate_breakdown(
            total_budget=float(trip.budget),
            days=trip.number_of_days,
            travelers=trip.number_of_travelers,
            travel_mode=travel_mode,
            accommodation_type=accommodation_type,
            destination_category=destination_category,
        )
        return self.save_budget(
            db, trip, breakdown, accommodation_type,
            travel_mode, destination_category,
        )

    def save_budget(
        self,
        db: Session,
        trip: Trip,
        breakdown: BudgetBreakdown,
        accommodation_type:   str = "mid-range",
        travel_mode:          str = "flight",
        destination_category: str = "general",
    ) -> TripExpenses:
        """Upsert TripExpenses — create if not exists, update if it does."""
        expense = db.query(TripExpenses).filter(
            TripExpenses.trip_id == trip.id
        ).first()

        values = dict(
            transport_cost=breakdown.transport_cost,
            accommodation_cost=breakdown.accommodation_cost,
            food_cost=breakdown.food_cost,
            activity_cost=breakdown.activity_cost,
            miscellaneous_cost=breakdown.miscellaneous_cost,
            total_cost=breakdown.total,
            budget_remaining=breakdown.budget_remaining,
            accommodation_type=accommodation_type,
            travel_mode=travel_mode,
            destination_category=destination_category,
        )

        if expense:
            for k, v in values.items():
                setattr(expense, k, v)
        else:
            expense = TripExpenses(trip_id=trip.id, **values)
            db.add(expense)

        # Sync total_estimated_cost on the trip itself
        trip.total_estimated_cost = breakdown.total
        db.commit()
        db.refresh(expense)
        logger.info(f"Budget saved for trip {trip.id}: total={breakdown.total}")
        return expense

    def get_budget(self, db: Session, trip_id: str, user: User) -> TripExpenses:
        """Return the saved TripExpenses for a trip."""
        self._get_trip(db, trip_id, user)   # ownership check
        expense = db.query(TripExpenses).filter(
            TripExpenses.trip_id == trip_id
        ).first()
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No budget found for this trip. Call POST /budget/calculate/{trip_id} first.",
            )
        return expense

    def update_budget(
        self,
        db: Session,
        trip_id: str,
        user: User,
        accommodation_type:   Optional[str] = None,
        destination_category: Optional[str] = None,
        override_travel_mode: Optional[str] = None,
    ) -> TripExpenses:
        """Recalculate and update budget after trip changes."""
        expense = self.get_budget(db, trip_id, user)
        return self.calculate_budget(
            db=db,
            trip_id=trip_id,
            user=user,
            accommodation_type=accommodation_type or expense.accommodation_type or "mid-range",
            destination_category=destination_category or expense.destination_category or "general",
            override_travel_mode=override_travel_mode,
        )

    def generate_budget_breakdown(
        self,
        db: Session,
        trip_id: str,
        user: User,
    ) -> dict:
        """Return a detailed breakdown dict for display."""
        expense = self.get_budget(db, trip_id, user)
        trip = self._get_trip(db, trip_id, user)
        return {
            "trip_id":             str(trip.id),
            "destination":         trip.destination_location,
            "total_budget":        float(trip.budget),
            "transport_cost":      float(expense.transport_cost),
            "accommodation_cost":  float(expense.accommodation_cost),
            "food_cost":           float(expense.food_cost),
            "activity_cost":       float(expense.activity_cost),
            "miscellaneous_cost":  float(expense.miscellaneous_cost),
            "total_cost":          float(expense.total_cost),
            "budget_remaining":    float(expense.budget_remaining),
            "accommodation_type":  expense.accommodation_type,
            "travel_mode":         expense.travel_mode,
            "destination_category": expense.destination_category,
        }

    # ── Budget insights ───────────────────────────────────────────────────────

    def get_insights(self, db: Session, trip_id: str, user: User) -> BudgetInsightsOut:
        """Generate smart budget insights and recommendations."""
        expense = self.get_budget(db, trip_id, user)
        trip    = self._get_trip(db, trip_id, user)

        total_budget     = float(trip.budget)
        total_cost       = float(expense.total_cost)
        remaining        = float(expense.budget_remaining)
        utilisation_pct  = round((total_cost / total_budget) * 100, 1) if total_budget else 0
        cost_per_day     = round(total_cost / max(trip.number_of_days, 1), 2)
        cost_per_person  = round(total_cost / max(trip.number_of_travelers, 1), 2)

        # Status
        if remaining >= total_budget * 0.15:
            budget_status = "Within Budget"
        elif remaining >= 0:
            budget_status = "Tight Budget"
        else:
            budget_status = "Over Budget"

        # Category breakdown
        category_breakdown = {
            "Transport":     float(expense.transport_cost),
            "Accommodation": float(expense.accommodation_cost),
            "Food":          float(expense.food_cost),
            "Activities":    float(expense.activity_cost),
            "Miscellaneous": float(expense.miscellaneous_cost),
        }

        # Smart recommendations
        recommendations: list[str] = []
        mode = (expense.travel_mode or "flight").lower()
        accom = (expense.accommodation_type or "mid-range").lower()

        if mode == "flight":
            recommendations.append(
                "✈️ Switch to train to save up to 50% on transport costs."
            )
        if mode == "car" or mode == "road":
            recommendations.append(
                "🚌 Carpooling or taking a bus can reduce transport costs significantly."
            )
        if accom == "luxury":
            recommendations.append(
                "🏨 Switching to mid-range hotels can save 30-40% on accommodation."
            )
        if accom == "mid-range" and utilisation_pct > 85:
            recommendations.append(
                "🛏️ Budget hostels or guesthouses can free up budget for activities."
            )
        if float(expense.food_cost) / total_budget > 0.22:
            recommendations.append(
                "🍽️ Eating at local restaurants instead of tourist spots saves 40% on food."
            )
        if utilisation_pct > 90:
            recommendations.append(
                "⚠️ You're close to your budget limit. Consider reducing activity spending."
            )
        if remaining > total_budget * 0.25:
            recommendations.append(
                "💰 You have room in your budget — consider upgrading your accommodation."
            )
        if not recommendations:
            recommendations.append(
                "✅ Your budget looks well-balanced across all categories."
            )

        return BudgetInsightsOut(
            budget_status=budget_status,
            total_budget=total_budget,
            total_cost=total_cost,
            remaining_amount=remaining,
            utilisation_pct=utilisation_pct,
            recommendations=recommendations,
            category_breakdown=category_breakdown,
            cost_per_day=cost_per_day,
            cost_per_person=cost_per_person,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _get_trip(db: Session, trip_id: str, user: User) -> Trip:
        trip = db.query(Trip).filter(
            Trip.id == trip_id,
            Trip.user_id == user.id,
        ).first()
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found or not owned by you",
            )
        return trip
