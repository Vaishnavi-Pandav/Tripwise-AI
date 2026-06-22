import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.destination import Destination
from app.models.hidden_gem import HiddenGem
from app.models.user import User
from app.schemas.hotel import HotelCreate, HotelResponse, HotelUpdate
from app.schemas.package import PackageCreate, PackageOut, PackageUpdate
from app.schemas.user import UserOut
from app.services.hotel_service import HotelService
from app.services.package_service import PackageService

logger = logging.getLogger("tripwise")
router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Inline Admin Schemas ──────────────────────────────────────────────────────

class DestinationCreate(BaseModel):
    city_name:             str
    country:               str
    state:                 Optional[str]               = None
    description:           Optional[str]               = None
    best_season:           Optional[str]               = None
    known_for:             Optional[str]               = None
    image_url:             Optional[str]               = None
    avg_budget_score:      Optional[float]             = None
    safety_score:          Optional[float]             = None
    weather_score:         Optional[float]             = None
    crowd_score:           Optional[float]             = None
    nightlife_score:       Optional[float]             = None
    food_score:            Optional[float]             = None
    adventure_score:       Optional[float]             = None
    family_friendly_score: Optional[float]             = None


class DestinationUpdate(BaseModel):
    city_name:             Optional[str]               = None
    country:               Optional[str]               = None
    state:                 Optional[str]               = None
    description:           Optional[str]               = None
    best_season:           Optional[str]               = None
    known_for:             Optional[str]               = None
    image_url:             Optional[str]               = None
    avg_budget_score:      Optional[float]             = None
    safety_score:          Optional[float]             = None
    weather_score:         Optional[float]             = None
    crowd_score:           Optional[float]             = None
    nightlife_score:       Optional[float]             = None
    food_score:            Optional[float]             = None
    adventure_score:       Optional[float]             = None
    family_friendly_score: Optional[float]             = None


class DestinationOut(BaseModel):
    id:                    str
    city_name:             str
    country:               str
    state:                 Optional[str]
    description:           Optional[str]
    best_season:           Optional[str]
    known_for:             Optional[str]
    image_url:             Optional[str]
    avg_budget_score:      Optional[float]
    safety_score:          Optional[float]
    weather_score:         Optional[float]
    crowd_score:           Optional[float]
    nightlife_score:       Optional[float]
    food_score:            Optional[float]
    adventure_score:       Optional[float]
    family_friendly_score: Optional[float]

    model_config = {"from_attributes": True}


class HiddenGemCreate(BaseModel):
    city:               str
    place_name:         str
    category:           Optional[str]   = None
    description:        Optional[str]   = None
    estimated_cost:     Optional[float] = None
    crowd_level:        Optional[str]   = "low"
    best_time_to_visit: Optional[str]   = None
    traveler_type:      Optional[str]   = None
    image_url:          Optional[str]   = None
    latitude:           Optional[float] = None
    longitude:          Optional[float] = None


class HiddenGemUpdate(BaseModel):
    city:               Optional[str]   = None
    place_name:         Optional[str]   = None
    category:           Optional[str]   = None
    description:        Optional[str]   = None
    estimated_cost:     Optional[float] = None
    crowd_level:        Optional[str]   = None
    best_time_to_visit: Optional[str]   = None
    traveler_type:      Optional[str]   = None
    image_url:          Optional[str]   = None
    latitude:           Optional[float] = None
    longitude:          Optional[float] = None


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


# ────────────────────────────────────────────────────────────────────────────────
# DESTINATION ADMIN ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.post(
    "/destinations",
    response_model=DestinationOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Create a destination",
)
def create_destination(
    payload: DestinationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    dest = Destination(**payload.model_dump())
    db.add(dest)
    db.commit()
    db.refresh(dest)
    logger.info(f"Destination created: {dest.id} — {dest.city_name}")
    return dest


@router.put(
    "/destinations/{destination_id}",
    response_model=DestinationOut,
    summary="[Admin] Update a destination",
)
def update_destination(
    destination_id: str,
    payload: DestinationUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    dest = db.query(Destination).filter(Destination.id == destination_id).first()
    if not dest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(dest, field, value)
    db.commit()
    db.refresh(dest)
    logger.info(f"Destination updated: {destination_id}")
    return dest


@router.delete(
    "/destinations/{destination_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete a destination",
)
def delete_destination(
    destination_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    dest = db.query(Destination).filter(Destination.id == destination_id).first()
    if not dest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    db.delete(dest)
    db.commit()
    logger.info(f"Destination deleted: {destination_id}")


# ────────────────────────────────────────────────────────────────────────────────
# HIDDEN GEM ADMIN ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.post(
    "/hidden-gems",
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Create a hidden gem",
)
def create_hidden_gem(
    payload: HiddenGemCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    gem = HiddenGem(**payload.model_dump())
    db.add(gem)
    db.commit()
    db.refresh(gem)
    logger.info(f"HiddenGem created: {gem.id} — {gem.place_name}")
    return {"id": str(gem.id), "place_name": gem.place_name, "city": gem.city}


@router.put(
    "/hidden-gems/{gem_id}",
    summary="[Admin] Update a hidden gem",
)
def update_hidden_gem(
    gem_id: str,
    payload: HiddenGemUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    gem = db.query(HiddenGem).filter(HiddenGem.id == gem_id).first()
    if not gem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hidden gem not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(gem, field, value)
    db.commit()
    db.refresh(gem)
    logger.info(f"HiddenGem updated: {gem_id}")
    return {"id": str(gem.id), "place_name": gem.place_name, "city": gem.city}


@router.delete(
    "/hidden-gems/{gem_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete a hidden gem",
)
def delete_hidden_gem(
    gem_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    gem = db.query(HiddenGem).filter(HiddenGem.id == gem_id).first()
    if not gem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hidden gem not found")
    db.delete(gem)
    db.commit()
    logger.info(f"HiddenGem deleted: {gem_id}")


# ────────────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get(
    "/users",
    summary="[Admin] List all users",
)
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    logger.info(f"Admin listed {len(users)} users")
    return [
        {
            "id":         str(u.id),
            "full_name":  u.full_name,
            "email":      u.email,
            "is_admin":   u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.get(
    "/users/{user_id}",
    summary="[Admin] Get a specific user",
)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"Admin fetched user: {user_id}")
    return {
        "id":           str(user.id),
        "full_name":    user.full_name,
        "email":        user.email,
        "is_admin":     user.is_admin,
        "profile_image": user.profile_image,
        "created_at":   user.created_at.isoformat() if user.created_at else None,
        "updated_at":   user.updated_at.isoformat() if user.updated_at else None,
    }


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete a user",
)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own admin account",
        )
    db.delete(user)
    db.commit()
    logger.info(f"Admin deleted user: {user_id}")
