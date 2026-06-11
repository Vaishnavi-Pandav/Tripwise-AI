from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.attraction import AttractionOut, HiddenGemOut
from app.services.attraction_service import AttractionService

router = APIRouter(tags=["Attractions"])


@router.get("/attractions", response_model=list[AttractionOut], summary="List all attractions")
def list_attractions(
    city: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AttractionService.get_all(db, city)


@router.get("/attractions/{city}", response_model=list[AttractionOut],
            summary="Get attractions by city")
def attractions_by_city(city: str, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    return AttractionService.get_by_city(db, city)


@router.get("/hidden-gems/{city}", response_model=list[HiddenGemOut],
            summary="Get hidden gems for a city")
def hidden_gems(city: str, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return AttractionService.get_hidden_gems(db, city)
