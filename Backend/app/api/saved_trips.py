from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.saved_trip import SavedTripCreate, SavedTripOut
from app.services.saved_trip_service import SavedTripService

router = APIRouter(prefix="/saved-trips", tags=["Saved Trips"])


@router.post("/", response_model=SavedTripOut, status_code=status.HTTP_201_CREATED,
             summary="Save a trip")
def save_trip(
    payload: SavedTripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SavedTripService.save(db, payload.trip_id, current_user)


@router.get("/", response_model=list[SavedTripOut], summary="Get all saved trips")
def list_saved(db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    return SavedTripService.get_all(db, current_user)


@router.delete("/{saved_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Remove a saved trip")
def remove_saved(saved_id: str, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    SavedTripService.delete(db, saved_id, current_user)
