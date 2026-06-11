from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class PackageCreate(BaseModel):
    destination: str
    agency_name: Optional[str] = None
    package_name: str
    duration_days: int
    price: float
    package_description: Optional[str] = None
    inclusions: Optional[list[str]] = None
    exclusions: Optional[list[str]] = None


class PackageOut(BaseModel):
    id: str
    destination: str
    agency_name: Optional[str]
    package_name: str
    duration_days: int
    price: float
    package_description: Optional[str]
    inclusions: Optional[Any]
    exclusions: Optional[Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class PackageUpdate(BaseModel):
    package_name: Optional[str] = None
    duration_days: Optional[int] = None
    price: Optional[float] = None
    package_description: Optional[str] = None
    inclusions: Optional[list[str]] = None
    exclusions: Optional[list[str]] = None
