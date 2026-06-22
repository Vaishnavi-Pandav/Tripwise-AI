import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.package import (
    PackageCompareOut,
    PackageCompareRequest,
    PackageListResponse,
    PackageOut,
    PackageRecommendationsOut,
)
from app.services.package_service import PackageService

logger = logging.getLogger("tripwise")
router = APIRouter(prefix="/packages", tags=["Packages"])


# ── GET /packages ──────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=PackageListResponse,
    summary="List travel packages with filters and pagination",
    description="""
Returns a paginated list of travel packages.

**Filters:**
- `destination` — partial match
- `package_type` — budget | standard | premium | luxury
- `min_price` / `max_price` — price range
- `duration_days` — exact match
- `min_rating` — minimum rating (0–5)
""",
)
def list_packages(
    destination:   Optional[str]   = Query(None, description="Destination (partial match)"),
    package_type:  Optional[str]   = Query(None, description="budget | standard | premium | luxury"),
    min_price:     Optional[float] = Query(None, ge=0),
    max_price:     Optional[float] = Query(None, ge=0),
    duration_days: Optional[int]   = Query(None, ge=1, description="Exact duration in days"),
    min_rating:    Optional[float] = Query(None, ge=0, le=5),
    page:          int             = Query(1,  ge=1),
    page_size:     int             = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PackageService.get_packages(
        db, destination, package_type, min_price,
        max_price, duration_days, min_rating, page, page_size,
    )


# ── GET /packages/recommendations/{trip_id} ───────────────────────────────────
# MUST be before /{package_id} to avoid route conflict

@router.get(
    "/recommendations/{trip_id}",
    response_model=PackageRecommendationsOut,
    summary="Get recommended packages for a trip",
    description="""
Scores and returns best-fit packages for a trip using:
- **40%** Budget match (package price vs trip budget)
- **30%** Package rating
- **20%** Duration match (package days vs trip days)
- **10%** Popularity (number of inclusions)

**Example response:**
```json
{
  "trip_id": "uuid",
  "destination": "Goa",
  "trip_budget": 15000,
  "trip_days": 5,
  "recommended_packages": [
    {
      "package_name": "Goa Beach Getaway 4N/5D",
      "price": 12999,
      "rating": 4.3,
      "recommendation_score": 88.5,
      "score_breakdown": {
        "budget_match": 35.2,
        "rating": 25.8,
        "duration_match": 20.0,
        "popularity": 7.5
      }
    }
  ]
}
```
""",
)
def recommend_packages(
    trip_id: str,
    top_n: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PackageService.recommend_packages(db, trip_id, top_n)


# ── POST /packages/compare ────────────────────────────────────────────────────

@router.post(
    "/compare",
    response_model=PackageCompareOut,
    summary="Compare 2–5 packages side by side",
    description="""
Compares multiple packages and returns:
- Price, duration, rating comparison
- Cheapest / highest rated / best value
- Common inclusions
- Unique inclusions per package
- Narrative recommendation

**Example request:**
```json
{"package_ids": ["uuid1", "uuid2", "uuid3"]}
```
""",
)
def compare_packages(
    payload: PackageCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PackageService.compare_packages(db, payload.package_ids)


# ── GET /packages/{package_id} ────────────────────────────────────────────────

@router.get(
    "/{package_id}",
    response_model=PackageOut,
    summary="Get complete package details by ID",
)
def get_package(
    package_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PackageService.get_package(db, package_id)
