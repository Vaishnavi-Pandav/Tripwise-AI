import json
import logging
import math
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.hotel import Hotel, HotelCategory
from app.models.hotel_recommendation import HotelRecommendation
from app.models.trip import Trip
from app.schemas.hotel import (
    HotelCreate,
    HotelListResponse,
    HotelRecommendationResponse,
    HotelRecommendationsOut,
    HotelUpdate,
)

logger = logging.getLogger("tripwise")


# ── Recommendation weight config ───────────────────────────────────────────────

WEIGHTS = {
    "budget_match":  0.40,   # 40% — how well price fits budget
    "rating":        0.30,   # 30% — hotel star rating
    "amenities":     0.20,   # 20% — number / quality of amenities
    "distance":      0.10,   # 10% — proximity proxy (category-based heuristic)
}

# Preferred amenities for scoring
PREMIUM_AMENITIES = {
    "wifi", "pool", "spa", "gym", "restaurant", "bar",
    "parking", "ac", "breakfast", "room service",
    "beach access", "airport shuttle",
}

# Category distance score (proxy — beach/city hotels score higher)
CATEGORY_DISTANCE_SCORE: dict[str, float] = {
    "budget":   0.50,
    "standard": 0.65,
    "premium":  0.80,
    "luxury":   0.70,   # luxury may be more secluded
}


@dataclass
class ScoreBreakdown:
    budget_match:  float
    rating:        float
    amenities:     float
    distance:      float
    total:         float


# ── Service ────────────────────────────────────────────────────────────────────

class HotelService:

    # ── CRUD ─────────────────────────────────────────────────────────────────

    @staticmethod
    def create_hotel(db: Session, payload: HotelCreate) -> Hotel:
        data = payload.model_dump()
        # Serialise amenities list → JSON string for SQLite/PostgreSQL compat
        if data.get("amenities") is not None:
            data["amenities"] = json.dumps(data["amenities"])
        hotel = Hotel(**data)
        db.add(hotel)
        db.commit()
        db.refresh(hotel)
        logger.info(f"Hotel created: {hotel.id} — {hotel.hotel_name}")
        return hotel

    @staticmethod
    def update_hotel(db: Session, hotel_id: str, payload: HotelUpdate) -> Hotel:
        hotel = HotelService.get_hotel_by_id(db, hotel_id)
        data = payload.model_dump(exclude_unset=True)
        if "amenities" in data and data["amenities"] is not None:
            data["amenities"] = json.dumps(data["amenities"])
        for field, value in data.items():
            setattr(hotel, field, value)
        db.commit()
        db.refresh(hotel)
        logger.info(f"Hotel updated: {hotel_id}")
        return hotel

    @staticmethod
    def delete_hotel(db: Session, hotel_id: str) -> None:
        hotel = HotelService.get_hotel_by_id(db, hotel_id)
        db.delete(hotel)
        db.commit()
        logger.info(f"Hotel deleted: {hotel_id}")

    @staticmethod
    def get_hotels(
        db: Session,
        city: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> HotelListResponse:
        q = db.query(Hotel)
        if city:
            q = q.filter(Hotel.city.ilike(f"%{city}%"))
        if category:
            q = q.filter(Hotel.hotel_category == category.lower())
        if min_price is not None:
            q = q.filter(Hotel.price_per_night >= min_price)
        if max_price is not None:
            q = q.filter(Hotel.price_per_night <= max_price)
        if min_rating is not None:
            q = q.filter(Hotel.rating >= min_rating)

        total      = q.count()
        total_pages = max(1, math.ceil(total / page_size))
        hotels     = (
            q.order_by(Hotel.rating.desc().nulls_last(), Hotel.price_per_night)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return HotelListResponse(
            hotels=hotels,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    def get_hotel_by_id(db: Session, hotel_id: str) -> Hotel:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hotel {hotel_id} not found",
            )
        return hotel

    # ── Recommendation engine ─────────────────────────────────────────────────

    @staticmethod
    def recommend_hotels(
        db: Session,
        trip_id: str,
        top_n: int = 5,
    ) -> HotelRecommendationsOut:
        """
        Score all hotels in the destination city and return top N.

        Scoring formula (out of 100):
          40% Budget Match  — how well nightly price fits trip budget/days
          30% Rating        — normalised 0-5 star rating
          20% Amenities     — premium amenity coverage
          10% Distance      — category-based proximity proxy
        """
        trip: Optional[Trip] = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found",
            )

        city = trip.destination_location
        budget_per_night = float(trip.budget) / max(trip.number_of_days, 1) * 0.28  # ~28% of daily budget for hotel

        hotels = db.query(Hotel).filter(
            Hotel.city.ilike(f"%{city}%")
        ).all()

        if not hotels:
            # Return empty response — no hotels seeded yet
            return HotelRecommendationsOut(
                trip_id=str(trip.id),
                destination=city,
                budget_per_night=round(budget_per_night, 2),
                recommended_hotels=[],
                total_found=0,
            )

        scored: list[tuple[Hotel, ScoreBreakdown]] = []
        for hotel in hotels:
            breakdown = HotelService._score_hotel(hotel, budget_per_night)
            scored.append((hotel, breakdown))

        # Sort by total score descending
        scored.sort(key=lambda x: x[1].total, reverse=True)
        top = scored[:top_n]

        # Upsert recommendation records
        for hotel, breakdown in top:
            existing = db.query(HotelRecommendation).filter(
                HotelRecommendation.trip_id == trip.id,
                HotelRecommendation.hotel_id == hotel.id,
            ).first()
            if existing:
                existing.recommendation_score = breakdown.total
            else:
                db.add(HotelRecommendation(
                    trip_id=trip.id,
                    hotel_id=hotel.id,
                    recommendation_score=breakdown.total,
                ))
        db.commit()

        results = []
        for hotel, breakdown in top:
            amenities = hotel.amenities_list()
            results.append(
                HotelRecommendationResponse(
                    hotel_id=str(hotel.id),
                    hotel_name=hotel.hotel_name,
                    city=hotel.city,
                    price_per_night=float(hotel.price_per_night),
                    rating=float(hotel.rating) if hotel.rating else None,
                    hotel_category=hotel.hotel_category,
                    amenities=amenities,
                    image_url=hotel.image_url,
                    recommendation_score=round(breakdown.total, 2),
                    score_breakdown={
                        "budget_match":  round(breakdown.budget_match, 2),
                        "rating":        round(breakdown.rating, 2),
                        "amenities":     round(breakdown.amenities, 2),
                        "distance":      round(breakdown.distance, 2),
                    },
                )
            )

        return HotelRecommendationsOut(
            trip_id=str(trip.id),
            destination=city,
            budget_per_night=round(budget_per_night, 2),
            recommended_hotels=results,
            total_found=len(hotels),
        )

    # ── Scoring helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _score_hotel(hotel: Hotel, budget_per_night: float) -> ScoreBreakdown:
        price = float(hotel.price_per_night)

        # 1. Budget match (40%) — highest score when price ≈ budget, penalise over-budget
        if budget_per_night <= 0:
            bm_raw = 0.5
        else:
            ratio = price / budget_per_night
            if ratio <= 1.0:
                bm_raw = 1.0 - (ratio * 0.1)   # slight reward for cheaper
            elif ratio <= 1.3:
                bm_raw = 1.0 - (ratio - 1.0)   # linear penalty 0–30% over
            else:
                bm_raw = max(0.0, 1.0 - ratio * 0.5)  # steep penalty beyond 30%
        budget_score = min(bm_raw, 1.0) * 100 * WEIGHTS["budget_match"]

        # 2. Rating (30%) — normalised over 5
        rating = float(hotel.rating) if hotel.rating else 3.0
        rating_score = (rating / 5.0) * 100 * WEIGHTS["rating"]

        # 3. Amenities (20%) — premium amenity coverage
        amenities = {a.lower() for a in hotel.amenities_list()}
        if amenities:
            overlap = len(amenities & PREMIUM_AMENITIES)
            amenity_ratio = min(overlap / 6.0, 1.0)  # cap at 6 premium amenities
        else:
            amenity_ratio = 0.2  # minimal default
        amenity_score = amenity_ratio * 100 * WEIGHTS["amenities"]

        # 4. Distance proxy (10%) — based on hotel category
        cat = (hotel.hotel_category or "standard").lower()
        dist_ratio = CATEGORY_DISTANCE_SCORE.get(cat, 0.65)
        distance_score = dist_ratio * 100 * WEIGHTS["distance"]

        total = round(budget_score + rating_score + amenity_score + distance_score, 2)
        return ScoreBreakdown(
            budget_match=budget_score,
            rating=rating_score,
            amenities=amenity_score,
            distance=distance_score,
            total=min(total, 100.0),
        )

    # ── Backwards compat aliases ──────────────────────────────────────────────
    create  = staticmethod(lambda *a, **kw: HotelService.create_hotel(*a, **kw))
    update  = staticmethod(lambda *a, **kw: HotelService.update_hotel(*a, **kw))
    delete  = staticmethod(lambda *a, **kw: HotelService.delete_hotel(*a, **kw))
    get_all = staticmethod(lambda *a, **kw: HotelService.get_hotels(*a, **kw).hotels)
    get_by_id = staticmethod(lambda *a, **kw: HotelService.get_hotel_by_id(*a, **kw))
    get_recommendations_for_trip = staticmethod(
        lambda *a, **kw: HotelService.recommend_hotels(*a, **kw).recommended_hotels
    )
