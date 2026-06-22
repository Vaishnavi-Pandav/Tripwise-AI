import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.attraction import (
    AttractionOut,
    HiddenGemOut,
    HiddenGemRecommendRequest,
    HiddenGemRecommendResponse,
)
from app.services.attraction_service import AttractionService
from app.services.hidden_gem_service import HiddenGemService

logger = logging.getLogger("tripwise")
router = APIRouter(tags=["Attractions & Hidden Gems"])

_gem_svc = HiddenGemService()


# ── Attraction endpoints ───────────────────────────────────────────────────────

@router.get(
    "/attractions",
    response_model=list[AttractionOut],
    summary="List all attractions",
)
def list_attractions(
    city: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AttractionService.get_all(db, city)


@router.get(
    "/attractions/{city}",
    response_model=list[AttractionOut],
    summary="Get attractions by city",
)
def attractions_by_city(
    city: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AttractionService.get_by_city(db, city)


# ── Hidden Gem endpoints ───────────────────────────────────────────────────────

@router.get(
    "/hidden-gems/{city}",
    response_model=list[HiddenGemOut],
    summary="Get hidden gems for a city",
    description="""
Returns lesser-known, off-the-beaten-path places for a city.
Includes DB-seeded gems and built-in curated data for popular destinations.

**Built-in cities:** Goa, Manali, Kerala, Rajasthan

**Optional filters:** `category`, `crowd_level`

**Categories:** beach | trek | waterfall | cafe | viewpoint | historical | adventure | nature
""",
)
def get_hidden_gems(
    city: str,
    category:    Optional[str] = Query(None, description="Filter by category"),
    crowd_level: Optional[str] = Query(None, description="low | medium | high"),
    page:        int            = Query(1,  ge=1),
    page_size:   int            = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _gem_svc.get_hidden_gems(db, city, category, crowd_level, page, page_size)


@router.post(
    "/hidden-gems/recommend",
    response_model=HiddenGemRecommendResponse,
    status_code=status.HTTP_200_OK,
    summary="Get personalised hidden gem recommendations for a trip",
    description="""
Recommends hidden gems based on trip context:
- **40%** Category match to traveler type
- **30%** Budget fit (cost vs daily budget)
- **20%** Crowd preference
- **10%** Traveler type tag match

Each recommendation includes a human-readable **reason** and **travel tips**.

**Example request:**
```json
{"trip_id": "your-trip-uuid"}
```

**Example response:**
```json
{
  "destination": "Goa",
  "traveler_type": "couple",
  "recommendations": [
    {
      "name": "Butterfly Beach",
      "category": "beach",
      "estimated_cost": 500,
      "crowd_level": "low",
      "reason": "Butterfly Beach is off the tourist trail with very few crowds, ideal for couple travelers.",
      "travel_tips": ["Hire a boat from Palolem for ₹400", "Carry snorkelling gear"]
    }
  ]
}
```
""",
)
def recommend_hidden_gems(
    payload: HiddenGemRecommendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _gem_svc.recommend_hidden_gems(db, payload.trip_id)
