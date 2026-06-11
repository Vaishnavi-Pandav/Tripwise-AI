from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.package import TravelPackage
from app.schemas.package import PackageCreate, PackageUpdate


class PackageService:

    @staticmethod
    def get_all(db: Session) -> list[TravelPackage]:
        return db.query(TravelPackage).all()

    @staticmethod
    def get_by_id(db: Session, package_id: str) -> TravelPackage:
        pkg = db.query(TravelPackage).filter(TravelPackage.id == package_id).first()
        if not pkg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
        return pkg

    @staticmethod
    def get_by_destination(db: Session, destination: str) -> list[TravelPackage]:
        return db.query(TravelPackage).filter(
            TravelPackage.destination.ilike(f"%{destination}%")
        ).all()

    @staticmethod
    def create(db: Session, payload: PackageCreate) -> TravelPackage:
        pkg = TravelPackage(**payload.model_dump())
        db.add(pkg)
        db.commit()
        db.refresh(pkg)
        return pkg

    @staticmethod
    def update(db: Session, package_id: str, payload: PackageUpdate) -> TravelPackage:
        pkg = PackageService.get_by_id(db, package_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(pkg, field, value)
        db.commit()
        db.refresh(pkg)
        return pkg

    @staticmethod
    def delete(db: Session, package_id: str) -> None:
        pkg = PackageService.get_by_id(db, package_id)
        db.delete(pkg)
        db.commit()
