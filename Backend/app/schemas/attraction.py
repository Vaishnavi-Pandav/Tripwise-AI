from typing import Any, Optional
from pydantic import BaseModel


class AttractionOut(BaseModel):
    id: str
    city: str
    attraction_name: str
    category: Optional[str]
    description: Optional[str]
    entry_fee: Optional[float]
    rating: Optional[float]
    location_coordinates: Optional[Any]
    image_url: Optional[str]

    model_config = {"from_attributes": True}


class HiddenGemOut(BaseModel):
    id: str
    city: str
    place_name: str
    description: Optional[str]
    recommended_for: Optional[str]
    image_url: Optional[str]

    model_config = {"from_attributes": True}
