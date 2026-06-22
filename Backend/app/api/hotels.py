import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.hotel import (
    HotelListResponse,
    HotelResponse,
    HotelRecommendationsOut,
)
from app.services.hotel_service import HotelService

logger = logging.getLogger("tripwise")
router = APIRouter(prefix="/hotels", tags=["Hotels"])


# ── GET /hotels ────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=HotelListResponse,
    summary="List hotels with filters and pagination",
    description="""
Returns a paginated list of hotels with optional filters.

**Filters:**
- `city` — partial match
- `category` — budget | standard | premium | luxury
- `min_price` / `max_price` — price per night range
- `min_rating` — minimum star rating (0–5)
""",
)
def list_hotels(
    city:       Optional[str]   = Query(None, description="City name (partial match)"),
    category:   Optional[str]   = Query(None, description="budget | standard | premium | luxury"),
    min_price:  Optional[float] = Query(None, ge=0,  description="Min price per night"),
    max_price:  Optional[float] = Query(None, ge=0,  description="Max price per night"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Min rating (0-5)"),
    page:       int             = Query(1,  ge=1, description="Page number"),
    page_size:  int             = Query(10, ge=1, le=50, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return HotelService.get_hotels(
        db, city, category, min_price, max_price, min_rating, page, page_size
    )


# ── GET /hotels/recommendations/{trip_id} ─────────────────────────────────────
# NOTE: This route MUST come before /{hotel_id} to avoid FastAPI treating
#       "recommendations" as a hotel_id path param.

@router.get(
    "/recommendations/{trip_id}",
    response_model=HotelRecommendationsOut,
    summary="Get AI hotel recommendations for a trip",
    description="""
Returns scored hotel recommendations for a trip based on:
- **40%** Budget match (price per night vs trip budget/days)
- **30%** Hotel rating
- **20%** Amenities coverage
- **10%** Location proximity proxy

Recommendations are saved to the database for future retrieval.

**Example response:**
```json
{
  "trip_id": "uuid",
  "destination": "Goa",
  "budget_per_night": 2100.0,
  "recommended_hotels": [
    {
      "hotel_name": "Sea View Resort",
      "price_per_night": 2500,
      "rating": 4.5,
      "recommendation_score": 87.5,
      "score_breakdown": {
        "budget_match": 34.2,
        "rating": 27.0,
        "amenities": 18.0,
        "distance": 8.0
      }
    }
  ],
  "total_found": 12
}
```
""",
)
def get_recommendations(
    trip_id: str,
    top_n: int = Query(5, ge=1, le=20, description="Max hotels to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return HotelService.recommend_hotels(db, trip_id, top_n)


# ── GET /hotels/{hotel_id} ────────────────────────────────────────────────────

@router.get(
    "/{hotel_id}",
    response_model=HotelResponse,
    summary="Get complete hotel details by ID",
)
def get_hotel(
    hotel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return HotelService.get_hotel_by_id(db, hotel_id)
