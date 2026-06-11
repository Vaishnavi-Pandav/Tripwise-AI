import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.saved_trip import SavedTrip
from app.models.trip import Trip
from app.models.user import User

logger = logging.getLogger("tripwise")


class SavedTripService:

    @staticmethod
    def save(db: Session, trip_id: str, user: User) -> SavedTrip:
        # Verify trip exists
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

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
        logger.info(f"Trip {trip_id} saved by user {user.id}")
        return saved

    @staticmethod
    def get_all(db: Session, user: User) -> list[SavedTrip]:
        return (
            db.query(SavedTrip)
            .options(joinedload(SavedTrip.trip))
            .filter(SavedTrip.user_id == user.id)
            .order_by(SavedTrip.created_at.desc())
            .all()
        )

    @staticmethod
    def delete(db: Session, saved_id: str, user: User) -> None:
        saved = db.query(SavedTrip).filter(
            SavedTrip.id == saved_id,
            SavedTrip.user_id == user.id,
        ).first()
        if not saved:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved trip not found",
            )
        db.delete(saved)
        db.commit()
        logger.info(f"Saved trip {saved_id} removed by user {user.id}")
