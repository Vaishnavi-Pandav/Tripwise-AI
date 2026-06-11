from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.hotel import HotelCreate, HotelOut, HotelUpdate
from app.schemas.package import PackageCreate, PackageOut, PackageUpdate
from app.services.hotel_service import HotelService
from app.services.package_service import PackageService

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Hotels ────────────────────────────────────────────────────────────────────

@router.post("/hotels", response_model=HotelOut, status_code=status.HTTP_201_CREATED,
             summary="[Admin] Add a hotel")
def create_hotel(
    payload: HotelCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return HotelService.create(db, payload)


@router.put("/hotels/{hotel_id}", response_model=HotelOut, summary="[Admin] Update a hotel")
def update_hotel(
    hotel_id: str,
    payload: HotelUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return HotelService.update(db, hotel_id, payload)


@router.delete("/hotels/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="[Admin] Delete a hotel")
def delete_hotel(hotel_id: str, db: Session = Depends(get_db),
                 admin: User = Depends(get_current_admin)):
    HotelService.delete(db, hotel_id)


# ── Packages ──────────────────────────────────────────────────────────────────

@router.post("/packages", response_model=PackageOut, status_code=status.HTTP_201_CREATED,
             summary="[Admin] Add a travel package")
def create_package(
    payload: PackageCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return PackageService.create(db, payload)


@router.put("/packages/{package_id}", response_model=PackageOut, summary="[Admin] Update a package")
def update_package(
    package_id: str,
    payload: PackageUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return PackageService.update(db, package_id, payload)


@router.delete("/packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="[Admin] Delete a package")
def delete_package(package_id: str, db: Session = Depends(get_db),
                   admin: User = Depends(get_current_admin)):
    PackageService.delete(db, package_id)
