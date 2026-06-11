from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.package import Package

router = APIRouter(prefix="/api/packages", tags=["Packages"])


class PackageOut(BaseModel):
    id: int
    title: str
    destination: str
    duration_days: int
    price: float
    description: Optional[str]
    highlights: Optional[str]
    image_url: Optional[str]
    category: Optional[str]

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[PackageOut])
def list_packages(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Return all travel packages, optionally filtered by category."""
    query = db.query(Package)
    if category:
        query = query.filter(Package.category.ilike(f"%{category}%"))
    return query.all()


@router.get("/{package_id}", response_model=PackageOut)
def get_package(package_id: int, db: Session = Depends(get_db)):
    pkg = db.query(Package).filter(Package.id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    return pkg
