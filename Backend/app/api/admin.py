import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.hotel import HotelCreate, HotelResponse, HotelUpdate
from app.schemas.package import PackageCreate, PackageOut, PackageUpdate
from app.services.hotel_service import HotelService
from app.services.package_service import PackageService

logger = logging.getLogger("tripwise")
router = APIRouter(prefix="/admin", tags=["Admin"])


# ────────────────────────────────────────────────────────────────────────────────
# HOTEL ADMIN ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.post(
    "/hotels",
    response_model=HotelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Add a new hotel",
    description="""
Create a new hotel entry. All hotel data including location, pricing,
amenities, and category.

**Hotel categories:** `budget` | `standard` | `premium` | `luxury`

**Example:**
```json
{
  "city": "Goa",
  "hotel_name": "Sea View Resort",
  "price_per_night": 2500,
  "rating": 4.5,
  "hotel_category": "premium",
  "amenities": ["WiFi", "Pool", "Restaurant", "Beach Access"],
  "latitude": 15.2993,
  "longitude": 74.1240
}
```
""",
)
def create_hotel(
    payload: HotelCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return HotelService.create_hotel(db, payload)


@router.put(
    "/hotels/{hotel_id}",
    response_model=HotelResponse,
    summary="[Admin] Update hotel details",
    description="Update any hotel field. Only provided fields will be changed.",
)
def update_hotel(
    hotel_id: str,
    payload: HotelUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return HotelService.update_hotel(db, hotel_id, payload)


@router.delete(
    "/hotels/{hotel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete a hotel",
)
def delete_hotel(
    hotel_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    HotelService.delete_hotel(db, hotel_id)


# ────────────────────────────────────────────────────────────────────────────────
# PACKAGE ADMIN ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.post(
    "/packages",
    response_model=PackageOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Add a travel package",
)
def create_package(
    payload: PackageCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return PackageService.create(db, payload)


@router.put(
    "/packages/{package_id}",
    response_model=PackageOut,
    summary="[Admin] Update a travel package",
)
def update_package(
    package_id: str,
    payload: PackageUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return PackageService.update(db, package_id, payload)


@router.delete(
    "/packages/{package_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete a travel package",
)
def delete_package(
    package_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    PackageService.delete(db, package_id)
