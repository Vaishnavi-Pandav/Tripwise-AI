import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.destination import Destination
from app.models.user import User
from app.schemas.comparison import (
    CompareOut,
    CompareRequest,
    DestinationCompareOut,
    DestinationCompareRequest,
)
from app.services.comparison_service import ComparisonService

logger = logging.getLogger("tripwise")
router = APIRouter(tags=["Destination Comparison"])
_svc   = ComparisonService()


# ── GET /destinations/ — PUBLIC listing ───────────────────────────────────────

@router.get("/destinations/", summary="List destinations (public)")
def list_destinations(
    search:   Optional[str] = Query(None, description="Search by city name"),
    country:  Optional[str] = Query(None),
    limit:    int           = Query(20, ge=1, le=100),
    offset:   int           = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(Destination)
    if search:
        q = q.filter(Destination.city_name.ilike(f"%{search}%"))
    if country:
        q = q.filter(Destination.country.ilike(f"%{country}%"))
    total = q.count()
    items = q.order_by(Destination.city_name).offset(offset).limit(limit).all()
    return {
        "total": total,
        "destinations": [
            {
                "id":          str(d.id),
                "city_name":   d.city_name,
                "state":       d.state,
                "country":     d.country,
                "description": d.description,
                "best_season": d.best_season,
                "known_for":   d.known_for,
                "image_url":   d.image_url,
                "overall_score": d.overall_score(),
                "safety_score":  d.safety_score,
                "food_score":    d.food_score,
                "adventure_score": d.adventure_score,
            }
            for d in items
        ],
    }


# ── POST /destinations/compare ────────────────────────────────────────────────

@router.post(
    "/destinations/compare",
    response_model=DestinationCompareOut,
    summary="Compare two destinations with AI-powered scoring",
    description="""
Compare two destinations across 8 factors with personalised scoring
based on traveler type.

**Factors compared:**
Budget · Safety · Weather · Crowd Level · Nightlife · Food · Adventure · Family Friendliness

**Traveler types:** `solo` | `couple` | `family` | `friends` | `backpacker`

Each type re-weights the factors — e.g. family trips weight safety 2× higher.

**Example request:**
```json
{
  "destination1": "Goa",
  "destination2": "Gokarna",
  "traveler_type": "couple",
  "budget": 15000
}
```

**Example response:**
```json
{
  "winner": "Gokarna",
  "recommendation": "Gokarna is recommended for couple travelers, scoring 7.8/10...",
  "factor_comparisons": [
    {"factor": "Safety", "dest1_score": 7.0, "dest2_score": 8.5, "winner": "Gokarna"}
  ],
  "ai_insight": "Gokarna offers better value for money. Gokarna is the safer option."
}
```
""",
)
def compare_destinations(
    payload: DestinationCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.compare_destinations(db, payload)


# ── POST /compare-destinations (legacy) ───────────────────────────────────────

@router.post(
    "/compare-destinations",
    response_model=DestinationCompareOut,
    summary="Compare destinations (alias endpoint)",
    include_in_schema=True,
)
def compare_destinations_legacy(
    payload: DestinationCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.compare_destinations(db, payload)
