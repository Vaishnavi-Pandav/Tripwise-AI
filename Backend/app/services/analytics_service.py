import logging
from collections import Counter
from sqlalchemy.orm import Session
from app.models.trip import Trip, TripStatus
from app.models.expenses import TripExpenses
from app.models.user import User
from app.schemas.analytics import AnalyticsDashboardOut, DestinationFrequency

logger = logging.getLogger("tripwise")

class AnalyticsService:
    @staticmethod
    def get_dashboard(db: Session, user: User) -> AnalyticsDashboardOut:
        trips = db.query(Trip).filter(Trip.user_id == user.id).all()
        total     = len(trips)
        completed = sum(1 for t in trips if t.trip_status == TripStatus.COMPLETED)
        planned   = sum(1 for t in trips if t.trip_status == TripStatus.PLANNED)
        cancelled = sum(1 for t in trips if t.trip_status == TripStatus.CANCELLED)
        draft     = sum(1 for t in trips if t.trip_status == TripStatus.DRAFT)

        # Budget stats from expenses
        expenses = db.query(TripExpenses).join(Trip, TripExpenses.trip_id == Trip.id).filter(
            Trip.user_id == user.id
        ).all()
        total_spent = sum(float(e.total_cost or 0) for e in expenses)
        avg_cost    = round(total_spent / max(total, 1), 2)

        # Total days
        total_days = sum(t.number_of_days or 0 for t in trips if t.trip_status == TripStatus.COMPLETED)

        # Top destinations
        dest_counter = Counter(t.destination_location for t in trips)
        top_dests = [DestinationFrequency(destination=d, count=c)
                     for d, c in dest_counter.most_common(5)]
        fav_dest = top_dests[0].destination if top_dests else None

        # Most used travel mode
        modes = [t.travel_mode for t in trips if t.travel_mode]
        mode_counter = Counter(modes)
        top_mode = mode_counter.most_common(1)[0][0] if mode_counter else None

        return AnalyticsDashboardOut(
            total_trips=total,
            completed_trips=completed,
            planned_trips=planned,
            cancelled_trips=cancelled,
            draft_trips=draft,
            favorite_destination=fav_dest,
            total_budget_spent=round(total_spent, 2),
            average_trip_cost=avg_cost,
            total_days_travelled=total_days,
            top_destinations=top_dests,
            most_used_travel_mode=top_mode,
        )
