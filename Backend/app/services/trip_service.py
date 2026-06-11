import logging
import math
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.trip import Trip, TripStatus
from app.models.user import User
from app.schemas.trip import TripCreate, TripDashboardStats, TripListResponse, TripUpdate
from app.services.budget_service import BudgetService

logger = logging.getLogger("tripwise")


class TripService:

    # ── Create ────────────────────────────────────────────────────────────────

    @staticmethod
    def create_trip(db: Session, payload: TripCreate, user: User) -> Trip:
        """Create a new trip and auto-calculate estimated cost."""
        budget_svc = BudgetService()
        breakdown = budget_svc.calculate_breakdown(
            total_budget=float(payload.budget),
            days=payload.number_of_days,
            travelers=payload.number_of_travelers,
            travel_mode=payload.travel_mode or "default",
        )
        trip = Trip(
            user_id=user.id,
            source_location=payload.source_location,
            destination_location=payload.destination_location,
            budget=payload.budget,
            number_of_days=payload.number_of_days,
            number_of_travelers=payload.number_of_travelers,
            travel_mode=payload.travel_mode,
            total_estimated_cost=breakdown.total,
            trip_status=TripStatus.PLANNED,
        )
        db.add(trip)
        db.commit()
        db.refresh(trip)
        logger.info(f"Trip created: {trip.id} by user {user.id}")
        return trip

    # ── Read single ───────────────────────────────────────────────────────────

    @staticmethod
    def get_trip(db: Session, trip_id: str, user: User) -> Trip:
        """Get a single trip owned by the current user."""
        trip = (
            db.query(Trip)
            .filter(Trip.id == trip_id, Trip.user_id == user.id)
            .first()
        )
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip {trip_id} not found",
            )
        return trip

    # ── Read list with pagination ─────────────────────────────────────────────

    @staticmethod
    def get_user_trips(
        db: Session,
        user: User,
        page: int = 1,
        page_size: int = 10,
        trip_status: Optional[str] = None,
        destination: Optional[str] = None,
    ) -> TripListResponse:
        """Return paginated trips for the current user with optional filters."""
        query = db.query(Trip).filter(Trip.user_id == user.id)

        if trip_status:
            query = query.filter(Trip.trip_status == trip_status)
        if destination:
            query = query.filter(
                Trip.destination_location.ilike(f"%{destination}%")
            )

        total = query.count()
        total_pages = max(1, math.ceil(total / page_size))
        offset = (page - 1) * page_size

        trips = (
            query
            .order_by(Trip.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return TripListResponse(
            trips=trips,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    # ── Update ────────────────────────────────────────────────────────────────

    @staticmethod
    def update_trip(db: Session, trip_id: str, payload: TripUpdate, user: User) -> Trip:
        """Update allowed fields of a trip."""
        trip = TripService.get_trip(db, trip_id, user)

        # Validate status transitions
        if payload.trip_status:
            TripService._validate_status_transition(trip.trip_status, payload.trip_status)

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(trip, field, value)

        # Recalculate cost if budget/days/travelers/mode changed
        budget_fields = {"budget", "number_of_days", "number_of_travelers", "travel_mode"}
        if payload.model_dump(exclude_unset=True).keys() & budget_fields:
            budget_svc = BudgetService()
            breakdown = budget_svc.calculate_breakdown(
                total_budget=float(trip.budget),
                days=trip.number_of_days,
                travelers=trip.number_of_travelers,
                travel_mode=trip.travel_mode or "default",
            )
            trip.total_estimated_cost = breakdown.total

        db.commit()
        db.refresh(trip)
        logger.info(f"Trip updated: {trip.id}")
        return trip

    # ── Delete ────────────────────────────────────────────────────────────────

    @staticmethod
    def delete_trip(db: Session, trip_id: str, user: User) -> None:
        """Delete a trip owned by the current user."""
        trip = TripService.get_trip(db, trip_id, user)
        db.delete(trip)
        db.commit()
        logger.info(f"Trip deleted: {trip_id} by user {user.id}")

    # ── Dashboard stats ───────────────────────────────────────────────────────

    @staticmethod
    def dashboard_stats(db: Session, user: User) -> TripDashboardStats:
        """Return aggregated trip stats for the dashboard."""
        base = db.query(Trip).filter(Trip.user_id == user.id)

        total     = base.count()
        draft     = base.filter(Trip.trip_status == TripStatus.DRAFT).count()
        planned   = base.filter(Trip.trip_status == TripStatus.PLANNED).count()
        completed = base.filter(Trip.trip_status == TripStatus.COMPLETED).count()
        cancelled = base.filter(Trip.trip_status == TripStatus.CANCELLED).count()

        agg = db.query(
            func.coalesce(func.sum(Trip.budget), 0).label("total_budget"),
            func.coalesce(func.avg(Trip.number_of_days), 0).label("avg_days"),
        ).filter(Trip.user_id == user.id).one()

        return TripDashboardStats(
            total_trips=total,
            draft_trips=draft,
            planned_trips=planned,
            completed_trips=completed,
            cancelled_trips=cancelled,
            total_budget=float(agg.total_budget),
            avg_days=round(float(agg.avg_days), 1),
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_status_transition(current: str, new: str) -> None:
        """Enforce allowed status transitions."""
        allowed: dict[str, list[str]] = {
            TripStatus.DRAFT:      [TripStatus.PLANNED, TripStatus.CANCELLED],
            TripStatus.PLANNED:    [TripStatus.COMPLETED, TripStatus.CANCELLED],
            TripStatus.COMPLETED:  [],
            TripStatus.CANCELLED:  [],
        }
        if new not in allowed.get(current, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from '{current}' to '{new}'",
            )

    # ── Backwards-compat aliases ──────────────────────────────────────────────
    create  = staticmethod(lambda *a, **kw: TripService.create_trip(*a, **kw))
    get_all = staticmethod(lambda *a, **kw: TripService.get_user_trips(*a, **kw).trips)
    get_by_id = staticmethod(lambda *a, **kw: TripService.get_trip(*a, **kw))
    update  = staticmethod(lambda *a, **kw: TripService.update_trip(*a, **kw))
    delete  = staticmethod(lambda *a, **kw: TripService.delete_trip(*a, **kw))
