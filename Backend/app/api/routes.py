import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.route import (
    NearbyAttractionResponse,
    RouteHistoryOut,
    RouteRequest,
    RouteResponse,
)
from app.services.route_service import RouteService

logger = logging.getLogger("tripwise")
router = APIRouter(prefix="/routes", tags=["Routes & Maps"])
_svc   = RouteService()


# ── POST /routes/calculate ─────────────────────────────────────────────────────

@router.post(
    "/calculate",
    response_model=RouteResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate route between two cities",
    description="""
Returns distance, duration, and cost for all travel modes (car, bus, train, flight).
Smart recommendation picks the best mode based on budget and distance.

**Example request:**
```json
{"source": "Pune", "destination": "Goa", "travelers": 2, "budget": 5000}
```

**Example response:**
```json
{
  "distance_km": 450,
  "best_mode": "train",
  "recommendation": "Train is best — saves ₹3500 vs flight.",
  "suggested_modes": [
    {"mode": "train", "estimated_cost": 720, "total_cost": 1440, "duration_label": "11h 00m"}
  ]
}
```
""",
)
def calculate_route(
    payload: RouteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.calculate_route(
        db=db,
        source=payload.source,
        destination=payload.destination,
        travelers=payload.travelers,
        budget=payload.budget,
        user=current_user,
    )


# ── GET /routes/history ────────────────────────────────────────────────────────

@router.get(
    "/history",
    response_model=list[RouteHistoryOut],
    summary="Get your route search history",
    description="Returns up to 50 most recent route calculations.",
)
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.get_history(db, current_user)


# ── GET /routes/nearby-attractions ────────────────────────────────────────────

@router.get(
    "/nearby-attractions",
    response_model=list[NearbyAttractionResponse],
    summary="Find attractions near a coordinate",
    description="""
Returns attractions and hidden gems within a given radius (km) of a coordinate.

Uses Haversine distance on database coordinates.
Results are sorted by distance (nearest first).

**Example:**
```
GET /routes/nearby-attractions?latitude=15.2993&longitude=74.1240&radius_km=20
```
""",
)
def get_nearby_attractions(
    latitude:  float = Query(..., ge=-90,  le=90,  description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(10.0, ge=1,  le=100, description="Search radius in km"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.get_nearby_attractions(db, latitude, longitude, radius_km)
