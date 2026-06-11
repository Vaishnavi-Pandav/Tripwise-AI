import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import TripCreate, TripUpdate
from app.services.budget_service import BudgetService


class TripService:

    @staticmethod
    def create(db: Session, payload: TripCreate, user: User) -> Trip:
        budget_svc = BudgetService()
        breakdown = budget_svc.calculate_breakdown(
            total_budget=float(payload.budget),
            days=payload.number_of_days,
            travelers=payload.number_of_travelers,
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
            trip_status="planned",
        )
        db.add(trip)
        db.commit()
        db.refresh(trip)
        return trip

    @staticmethod
    def get_all(db: Session, user: User) -> list[Trip]:
        return db.query(Trip).filter(Trip.user_id == user.id).all()

    @staticmethod
    def get_by_id(db: Session, trip_id: str, user: User) -> Trip:
        trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user.id).first()
        if not trip:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
        return trip

    @staticmethod
    def update(db: Session, trip_id: str, payload: TripUpdate, user: User) -> Trip:
        trip = TripService.get_by_id(db, trip_id, user)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(trip, field, value)
        db.commit()
        db.refresh(trip)
        return trip

    @staticmethod
    def delete(db: Session, trip_id: str, user: User) -> None:
        trip = TripService.get_by_id(db, trip_id, user)
        db.delete(trip)
        db.commit()
