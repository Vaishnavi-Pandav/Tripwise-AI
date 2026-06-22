from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.favorite import FavoriteCreate, FavoriteOut
from app.services.favorite_service import FavoriteService

router = APIRouter(prefix="/favorites", tags=["Favorites & Wishlist"])

@router.post("/{entity_type}", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED,
             summary="Add to favorites (entity_type: destination|hotel|trip|package)")
def add_favorite(entity_type: str, payload: FavoriteCreate,
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return FavoriteService.add(db, current_user, entity_type, payload.entity_id)

@router.get("/", response_model=list[FavoriteOut], summary="Get all favorites")
def get_favorites(entity_type: Optional[str] = Query(None),
                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return FavoriteService.get_all(db, current_user, entity_type)

@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove from favorites")
def remove_favorite(favorite_id: str, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    FavoriteService.remove(db, current_user, favorite_id)
