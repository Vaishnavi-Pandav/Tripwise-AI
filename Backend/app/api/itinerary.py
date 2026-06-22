import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.itinerary import (
    GenerateItineraryRequest,
    ItineraryResponse,
)
from app.services.itinerary_service import ItineraryService

logger = logging.getLogger("tripwise")
router = APIRouter(prefix="/itinerary", tags=["Itinerary"])

_svc = ItineraryService()


# ── POST /itinerary/generate ───────────────────────────────────────────────────

@router.post(
    "/generate",
    response_model=ItineraryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI day-wise itinerary for a trip",
    description="""
Generates a complete day-by-day itinerary using Gemini AI.

The AI uses:
- Trip destination, budget, duration, travelers, travel mode
- Saved hotel recommendations (if any)
- Saved budget breakdown (if any)
- Budget category (low / mid / high) to tune activity recommendations

**Budget rules:**
- **Low** (<₹1500/day): free attractions, street food, public transport
- **Mid** (₹1500–₹4000/day): mixed paid/free, mid-range restaurants
- **High** (>₹4000/day): premium experiences, fine dining, private transfers

**Example request:**
```json
{"trip_id": "your-trip-uuid"}
```

**Example response:**
```json
{
  "trip_id": "uuid",
  "destination": "Goa",
  "total_days": 4,
  "total_cost": 12400,
  "days": [
    {
      "day_number": 1,
      "title": "Arrival & North Goa Beaches",
      "activities": [
        {
          "time": "Morning",
          "name": "Calangute Beach",
          "description": "Most popular beach in Goa",
          "location": "Calangute",
          "cost": "Free",
          "tips": "Arrive early to avoid crowds"
        }
      ],
      "estimated_cost": 3200,
      "notes": "Keep travel documents handy for hotel check-in"
    }
  ]
}
```
""",
)
def generate_itinerary(
    payload: GenerateItineraryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.generate_itinerary(db, payload.trip_id, current_user)


# ── GET /itinerary/{trip_id} ───────────────────────────────────────────────────

@router.get(
    "/{trip_id}",
    response_model=ItineraryResponse,
    summary="Get saved itinerary for a trip",
    description="Returns the previously generated day-wise itinerary for a trip.",
)
def get_itinerary(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.get_itinerary(db, trip_id, current_user)


# ── DELETE /itinerary/{trip_id} ────────────────────────────────────────────────

@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete itinerary for a trip",
    description="Deletes all itinerary day records for the given trip.",
)
def delete_itinerary(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _svc.delete_itinerary(db, trip_id, current_user)
