from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.itinerary import ItineraryGenerateRequest, ItineraryOut, ItineraryRawOut
from app.services.itinerary_service import ItineraryService
from app.services.trip_service import TripService

router = APIRouter(prefix="/itinerary", tags=["Itinerary"])


@router.post("/generate", response_model=ItineraryRawOut, summary="Generate AI itinerary for a trip")
def generate_itinerary(
    payload: ItineraryGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        markdown = ItineraryService.generate_and_save(
            db=db,
            trip_id=payload.trip_id,
            source=payload.source_location,
            destination=payload.destination_location,
            days=payload.number_of_days,
            travelers=payload.number_of_travelers,
            budget=payload.budget,
            travel_mode=payload.travel_mode or "",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    return ItineraryRawOut(trip_id=payload.trip_id, itinerary_markdown=markdown)


@router.get("/{trip_id}", response_model=list[ItineraryOut], summary="Get saved itinerary for a trip")
def get_itinerary(trip_id: str, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    return ItineraryService.get_for_trip(db, trip_id)
