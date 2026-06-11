from sqlalchemy.orm import Session

from app.models.attraction import Attraction
from app.models.hidden_gem import HiddenGem


class AttractionService:

    @staticmethod
    def get_all(db: Session, city: str | None = None) -> list[Attraction]:
        q = db.query(Attraction)
        if city:
            q = q.filter(Attraction.city.ilike(f"%{city}%"))
        return q.all()

    @staticmethod
    def get_by_city(db: Session, city: str) -> list[Attraction]:
        return db.query(Attraction).filter(Attraction.city.ilike(f"%{city}%")).all()

    @staticmethod
    def get_hidden_gems(db: Session, city: str) -> list[HiddenGem]:
        return db.query(HiddenGem).filter(HiddenGem.city.ilike(f"%{city}%")).all()
