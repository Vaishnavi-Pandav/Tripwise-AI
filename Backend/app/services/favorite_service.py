import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.favorite import Favorite
from app.models.user import User

logger = logging.getLogger("tripwise")

class FavoriteService:
    @staticmethod
    def add(db: Session, user: User, entity_type: str, entity_id: str) -> Favorite:
        existing = db.query(Favorite).filter(
            Favorite.user_id == user.id,
            Favorite.entity_type == entity_type,
            Favorite.entity_id == entity_id,
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already in favorites")
        fav = Favorite(user_id=user.id, entity_type=entity_type, entity_id=entity_id)
        db.add(fav); db.commit(); db.refresh(fav)
        logger.info(f"Favorite added: user={user.id} {entity_type}={entity_id}")
        return fav

    @staticmethod
    def remove(db: Session, user: User, favorite_id: str) -> None:
        fav = db.query(Favorite).filter(Favorite.id == favorite_id, Favorite.user_id == user.id).first()
        if not fav:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")
        db.delete(fav); db.commit()

    @staticmethod
    def get_all(db: Session, user: User, entity_type: str | None = None) -> list[Favorite]:
        q = db.query(Favorite).filter(Favorite.user_id == user.id)
        if entity_type:
            q = q.filter(Favorite.entity_type == entity_type)
        return q.order_by(Favorite.created_at.desc()).all()
