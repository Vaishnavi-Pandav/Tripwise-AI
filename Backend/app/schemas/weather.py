from datetime import date
from typing import Optional
from pydantic import BaseModel


class WeatherOut(BaseModel):
    city: str
    temperature: Optional[float]
    feels_like: Optional[float]
    weather_condition: Optional[str]
    humidity: Optional[float]
    forecast_date: Optional[date]
    travel_recommendation: str
    source: str = "cache"
