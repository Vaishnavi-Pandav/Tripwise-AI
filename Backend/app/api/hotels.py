from fastapi import APIRouter, Query

from app.services.hotel_service import HotelService, HotelSuggestion

router = APIRouter(prefix="/api/hotels", tags=["Hotels"])

_hotel_service = HotelService()


@router.get("/suggestions", response_model=list[dict])
def get_hotel_suggestions(
    destination: str = Query(..., description="Destination city/country"),
    total_budget: float = Query(..., description="Total trip budget in USD"),
    days: int = Query(..., description="Number of trip days"),
):
    """Return budget, mid-range, and luxury hotel suggestions for a destination."""
    budget_per_night = _hotel_service.budget_per_night(total_budget, days)
    suggestions: list[HotelSuggestion] = _hotel_service.get_suggestions(destination, budget_per_night)
    return [
        {
            "name": s.name,
            "tier": s.tier,
            "price_per_night": s.price_per_night,
            "rating": s.rating,
            "amenities": s.amenities,
            "notes": s.notes,
        }
        for s in suggestions
    ]
