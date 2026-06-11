from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripOut
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/trips", tags=["Trips"])

_ai_service = AIService()


@router.post("/", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(payload: TripCreate, db: Session = Depends(get_db)):
    """Save a trip and generate its AI itinerary."""
    try:
        itinerary = _ai_service.generate_itinerary(
            source=payload.source,
            destination=payload.destination,
            days=payload.days,
            travelers=payload.travelers,
            budget=payload.budget,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    trip = Trip(
        user_id=1,  # replace with current_user.id once auth is wired
        source=payload.source,
        destination=payload.destination,
        days=payload.days,
        travelers=payload.travelers,
        budget=payload.budget,
        itinerary=itinerary,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("/", response_model=list[TripOut])
def list_trips(db: Session = Depends(get_db)):
    """Return all saved trips."""
    return db.query(Trip).all()


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    db.delete(trip)
    db.commit()
