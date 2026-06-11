from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.hotel import Hotel
from app.models.hotel_recommendation import HotelRecommendation
from app.schemas.hotel import HotelCreate, HotelUpdate


class HotelService:

    @staticmethod
    def get_all(db: Session, city: Optional[str] = None, min_rating: Optional[float] = None,
                max_price: Optional[float] = None) -> list[Hotel]:
        q = db.query(Hotel)
        if city:
            q = q.filter(Hotel.city.ilike(f"%{city}%"))
        if min_rating:
            q = q.filter(Hotel.rating >= min_rating)
        if max_price:
            q = q.filter(Hotel.price_per_night <= max_price)
        return q.all()

    @staticmethod
    def get_by_id(db: Session, hotel_id: str) -> Hotel:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
        return hotel

    @staticmethod
    def get_recommendations_for_trip(db: Session, trip_id: str) -> list[Hotel]:
        recs = (
            db.query(HotelRecommendation)
            .filter(HotelRecommendation.trip_id == trip_id)
            .order_by(HotelRecommendation.recommendation_score.desc())
            .all()
        )
        return [r.hotel for r in recs]

    @staticmethod
    def create(db: Session, payload: HotelCreate) -> Hotel:
        hotel = Hotel(**payload.model_dump())
        db.add(hotel)
        db.commit()
        db.refresh(hotel)
        return hotel

    @staticmethod
    def update(db: Session, hotel_id: str, payload: HotelUpdate) -> Hotel:
        hotel = HotelService.get_by_id(db, hotel_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(hotel, field, value)
        db.commit()
        db.refresh(hotel)
        return hotel

    @staticmethod
    def delete(db: Session, hotel_id: str) -> None:
        hotel = HotelService.get_by_id(db, hotel_id)
        db.delete(hotel)
        db.commit()
