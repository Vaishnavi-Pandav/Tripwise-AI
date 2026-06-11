import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.itinerary import Itinerary
from app.services.ai_service import AIService

_ai = AIService()


class ItineraryService:

    @staticmethod
    def generate_and_save(
        db: Session,
        trip_id: str,
        source: str,
        destination: str,
        days: int,
        travelers: int,
        budget: float,
        travel_mode: str = "",
    ) -> str:
        """Call AI, store markdown as one record per trip, return markdown."""
        markdown = _ai.generate_itinerary(
            source=source,
            destination=destination,
            days=days,
            travelers=travelers,
            budget=budget,
        )
        # Store as a single itinerary record (day_number=0 → full itinerary)
        existing = db.query(Itinerary).filter(
            Itinerary.trip_id == trip_id, Itinerary.day_number == 0
        ).first()
        if existing:
            existing.activities = {"markdown": markdown}
            existing.title = f"{destination} — {days} Day Itinerary"
        else:
            record = Itinerary(
                trip_id=trip_id,
                day_number=0,
                title=f"{destination} — {days} Day Itinerary",
                activities={"markdown": markdown},
                estimated_cost=budget,
            )
            db.add(record)
        db.commit()
        return markdown

    @staticmethod
    def get_for_trip(db: Session, trip_id: str) -> list[Itinerary]:
        records = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).all()
        if not records:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No itinerary found for this trip")
        return records
