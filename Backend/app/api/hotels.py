from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.hotel import HotelOut
from app.services.hotel_service import HotelService

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("/", response_model=list[HotelOut], summary="List hotels with optional filters")
def list_hotels(
    city: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return HotelService.get_all(db, city, min_rating, max_price)


@router.get("/recommendations/{trip_id}", response_model=list[HotelOut],
            summary="Get hotel recommendations for a trip")
def get_recommendations(trip_id: str, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    return HotelService.get_recommendations_for_trip(db, trip_id)


@router.get("/{hotel_id}", response_model=HotelOut, summary="Get hotel by ID")
def get_hotel(hotel_id: str, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    return HotelService.get_by_id(db, hotel_id)
