from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.package import PackageOut
from app.services.package_service import PackageService

router = APIRouter(prefix="/packages", tags=["Packages"])


@router.get("/", response_model=list[PackageOut], summary="List all travel packages")
def list_packages(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    return PackageService.get_all(db)


@router.get("/destination/{destination}", response_model=list[PackageOut],
            summary="Get packages by destination")
def packages_by_destination(destination: str, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    return PackageService.get_by_destination(db, destination)


@router.get("/{package_id}", response_model=PackageOut, summary="Get package by ID")
def get_package(package_id: str, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return PackageService.get_by_id(db, package_id)
