from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.weather import WeatherOut
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather"])

_svc = WeatherService()


@router.get("/{city}", response_model=WeatherOut, summary="Get weather info for a city")
def get_weather(city: str, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return _svc.get_weather(db, city)
