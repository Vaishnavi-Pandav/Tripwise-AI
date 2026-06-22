import logging, math
from typing import Optional
from sqlalchemy.orm import Session
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.package import TravelPackage
from app.models.hidden_gem import HiddenGem
from app.models.attraction import Attraction
from app.schemas.search import SearchResponse, SearchResultItem

logger = logging.getLogger("tripwise")

class SearchService:
    @staticmethod
    def search(
        db: Session, query: str,
        entity_type: Optional[str] = None,
        page: int = 1, page_size: int = 20,
    ) -> SearchResponse:
        results: list[SearchResultItem] = []
        q = f"%{query}%"

        if not entity_type or entity_type == "destination":
            for d in db.query(Destination).filter(Destination.city_name.ilike(q)).limit(10).all():
                results.append(SearchResultItem(
                    id=str(d.id), name=d.city_name, type="destination",
                    city=d.city_name, description=d.description,
                    price=None, rating=d.safety_score, image_url=d.image_url,
                ))

        if not entity_type or entity_type == "hotel":
            for h in db.query(Hotel).filter(Hotel.hotel_name.ilike(q) | Hotel.city.ilike(q)).limit(10).all():
                results.append(SearchResultItem(
                    id=str(h.id), name=h.hotel_name, type="hotel",
                    city=h.city, description=h.description,
                    price=float(h.price_per_night), rating=float(h.rating) if h.rating else None,
                    image_url=h.image_url,
                ))

        if not entity_type or entity_type == "package":
            for p in db.query(TravelPackage).filter(
                TravelPackage.package_name.ilike(q) | TravelPackage.destination.ilike(q)
            ).limit(10).all():
                results.append(SearchResultItem(
                    id=str(p.id), name=p.package_name, type="package",
                    city=p.destination, description=p.package_description,
                    price=float(p.price), rating=p.rating, image_url=p.image_url,
                ))

        if not entity_type or entity_type == "hidden_gem":
            for g in db.query(HiddenGem).filter(
                HiddenGem.place_name.ilike(q) | HiddenGem.city.ilike(q)
            ).limit(10).all():
                results.append(SearchResultItem(
                    id=str(g.id), name=g.place_name, type="hidden_gem",
                    city=g.city, description=g.description,
                    price=float(g.estimated_cost) if g.estimated_cost else None,
                    rating=None, image_url=g.image_url,
                ))

        total = len(results)
        start = (page - 1) * page_size
        return SearchResponse(query=query, results=results[start:start+page_size],
                              total=total, page=page, page_size=page_size)
