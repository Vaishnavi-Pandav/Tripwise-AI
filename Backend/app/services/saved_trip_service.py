from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.saved_trip import SavedTrip
from app.models.user import User


class SavedTripService:

    @staticmethod
    def save(db: Session, trip_id: str, user: User) -> SavedTrip:
        existing = db.query(SavedTrip).filter(
            SavedTrip.user_id == user.id,
            SavedTrip.trip_id == trip_id,
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Trip already saved")
        saved = SavedTrip(user_id=user.id, trip_id=trip_id)
        db.add(saved)
        db.commit()
        db.refresh(saved)
        return saved

    @staticmethod
    def get_all(db: Session, user: User) -> list[SavedTrip]:
        return (
            db.query(SavedTrip)
            .filter(SavedTrip.user_id == user.id)
            .all()
        )

    @staticmethod
    def delete(db: Session, saved_id: str, user: User) -> None:
        saved = db.query(SavedTrip).filter(
            SavedTrip.id == saved_id,
            SavedTrip.user_id == user.id,
        ).first()
        if not saved:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved trip not found")
        db.delete(saved)
        db.commit()
