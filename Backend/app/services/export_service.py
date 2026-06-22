import logging
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.export_history import ExportHistory
from app.models.trip import Trip
from app.models.expenses import TripExpenses
from app.models.itinerary import Itinerary
from app.models.hotel_recommendation import HotelRecommendation
from app.models.user import User
from app.schemas.export import TripExportData

logger = logging.getLogger("tripwise")

class ExportService:
    @staticmethod
    def generate_pdf_data(db: Session, trip_id: str, user: User) -> TripExportData:
        trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user.id).first()
        if not trip:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        expense = db.query(TripExpenses).filter(TripExpenses.trip_id == trip_id).first()
        budget_breakdown = None
        if expense:
            budget_breakdown = {
                "transport":     float(expense.transport_cost or 0),
                "accommodation": float(expense.accommodation_cost or 0),
                "food":          float(expense.food_cost or 0),
                "activities":    float(expense.activity_cost or 0),
                "miscellaneous": float(expense.miscellaneous_cost or 0),
                "total":         float(expense.total_cost or 0),
            }

        itineraries = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).order_by(Itinerary.day_number).all()
        itinerary_data = [
            {"day": i.day_number, "title": i.title, "estimated_cost": float(i.estimated_cost or 0), "notes": i.notes}
            for i in itineraries
        ]

        hotel_recs = db.query(HotelRecommendation).filter(
            HotelRecommendation.trip_id == trip_id
        ).order_by(HotelRecommendation.recommendation_score.desc()).limit(3).all()
        hotels_data = [
            {"name": r.hotel.hotel_name if r.hotel else "N/A",
             "price_per_night": float(r.hotel.price_per_night) if r.hotel else 0,
             "rating": float(r.hotel.rating) if r.hotel and r.hotel.rating else None,
             "score": float(r.recommendation_score or 0)}
            for r in hotel_recs
        ]

        # Save export history
        ExportService.save_export_history(db, user, trip_id)

        return TripExportData(
            trip_id=trip_id,
            destination=trip.destination_location,
            source=trip.source_location,
            budget=float(trip.budget),
            days=trip.number_of_days,
            travelers=trip.number_of_travelers,
            travel_mode=trip.travel_mode,
            trip_status=trip.trip_status,
            budget_breakdown=budget_breakdown,
            itinerary=itinerary_data,
            hotel_recommendations=hotels_data,
            weather_summary=None,
            hidden_gems=None,
            route_info=None,
            generated_at=datetime.utcnow(),
        )

    @staticmethod
    def save_export_history(db: Session, user: User, trip_id: str) -> ExportHistory:
        record = ExportHistory(user_id=user.id, trip_id=trip_id, file_url=f"/exports/{trip_id}.pdf")
        db.add(record); db.commit(); db.refresh(record)
        logger.info(f"Export saved: user={user.id} trip={trip_id}")
        return record
