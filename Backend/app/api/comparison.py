import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
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
