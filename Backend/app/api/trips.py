import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.trip import (
    TripCreate,
    TripDashboardStats,
    TripListResponse,
    TripResponse,
    TripUpdate,
)
from app.services.trip_service import TripService

logger = logging.getLogger("tripwise")

router = APIRouter(prefix="/trips", tags=["Trips"])


# ── POST /trips ────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trip",
    description="""
Create a new trip. Budget is auto-split into cost categories.

**Status after creation:** `planned`

**Example request:**
```json
{
  "source_location": "Mumbai",
  "destination_location": "Goa",
  "budget": 15000,
  "number_of_days": 4,
  "number_of_travelers": 2,
  "travel_mode": "flight"
}
```
""",
)
def create_trip(
    payload: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TripService.create_trip(db, payload, current_user)


# ── GET /trips ─────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=TripListResponse,
    summary="List trips with pagination and filters",
    description="""
Returns a paginated list of all trips belonging to the authenticated user.

**Filters:** `status`, `destination`  
**Pagination:** `page` (default 1), `page_size` (default 10, max 50)
""",
)
def list_trips(
    page:        int           = Query(1,    ge=1,           description="Page number"),
    page_size:   int           = Query(10,   ge=1,  le=50,   description="Results per page"),
    trip_status: Optional[str] = Query(None, description="Filter by status: draft|planned|completed|cancelled"),
    destination: Optional[str] = Query(None, description="Filter by destination (partial match)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TripService.get_user_trips(
        db, current_user, page, page_size, trip_status, destination
    )


# ── GET /trips/dashboard ───────────────────────────────────────────────────────

@router.get(
    "/dashboard",
    response_model=TripDashboardStats,
    summary="Get trip dashboard statistics",
    description="""
Returns aggregated stats for the current user's trips.

**Example response:**
```json
{
  "total_trips": 10,
  "draft_trips": 0,
  "planned_trips": 5,
  "completed_trips": 3,
  "cancelled_trips": 2,
  "total_budget": 150000.0,
  "avg_days": 5.2
}
```
""",
)
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TripService.dashboard_stats(db, current_user)


# ── GET /trips/{trip_id} ───────────────────────────────────────────────────────

@router.get(
    "/{trip_id}",
    response_model=TripResponse,
    summary="Get a single trip by ID",
)
def get_trip(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TripService.get_trip(db, trip_id, current_user)


# ── PUT /trips/{trip_id} ───────────────────────────────────────────────────────

@router.put(
    "/{trip_id}",
    response_model=TripResponse,
    summary="Update a trip",
    description="""
Update any field of a trip. Budget cost is automatically recalculated
if budget, days, travelers or travel_mode changes.

**Status transitions allowed:**
- `draft` → `planned`, `cancelled`
- `planned` → `completed`, `cancelled`
- `completed` → _(no further changes)_
- `cancelled` → _(no further changes)_
""",
)
def update_trip(
    trip_id: str,
    payload: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TripService.update_trip(db, trip_id, payload, current_user)


# ── DELETE /trips/{trip_id} ────────────────────────────────────────────────────

@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a trip",
)
def delete_trip(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    TripService.delete_trip(db, trip_id, current_user)
