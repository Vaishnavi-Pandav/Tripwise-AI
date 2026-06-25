from typing import Optional
from pydantic import BaseModel

class SearchResultItem(BaseModel):
    id: str
    name: str
    type: str        # destination|hotel|package|hidden_gem
    city: Optional[str]
    description: Optional[str]
    price: Optional[float]
    rating: Optional[float]
    image_url: Optional[str]

class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
    total: int
    page: int
    page_size: int
