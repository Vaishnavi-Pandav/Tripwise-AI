from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Trip, User
from app.routers.auth import get_current_user
from app.schemas import TripCreate, TripOut
from app.services.openai_service import generate_itinerary

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("/generate", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def generate_trip(
    payload: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI itinerary and save the trip to the database."""
    itinerary_json = generate_itinerary(
        destination=payload.destination,
        duration_days=payload.duration_days,
        budget=payload.budget,
        travel_style=payload.travel_style,
        num_travelers=payload.num_travelers,
    )

    trip = Trip(
        user_id=current_user.id,
        destination=payload.destination,
        duration_days=payload.duration_days,
        budget=payload.budget,
        travel_style=payload.travel_style,
        num_travelers=payload.num_travelers,
        itinerary=itinerary_json,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("/", response_model=list[TripOut])
def list_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all trips belonging to the current user."""
    return db.query(Trip).filter(Trip.user_id == current_user.id).all()


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    db.delete(trip)
    db.commit()
