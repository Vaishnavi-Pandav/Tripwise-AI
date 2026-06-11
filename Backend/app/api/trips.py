from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.trip import TripCreate, TripOut, TripUpdate
from app.services.trip_service import TripService

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("/", response_model=TripOut, status_code=status.HTTP_201_CREATED,
             summary="Create a new trip")
def create_trip(
    payload: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TripService.create(db, payload, current_user)


@router.get("/", response_model=list[TripOut], summary="List all trips for current user")
def list_trips(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TripService.get_all(db, current_user)


@router.get("/{trip_id}", response_model=TripOut, summary="Get a single trip")
def get_trip(trip_id: str, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    return TripService.get_by_id(db, trip_id, current_user)


@router.put("/{trip_id}", response_model=TripOut, summary="Update a trip")
def update_trip(
    trip_id: str,
    payload: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TripService.update(db, trip_id, payload, current_user)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a trip")
def delete_trip(trip_id: str, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    TripService.delete(db, trip_id, current_user)
