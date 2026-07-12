import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.weather import ForecastResponse, TravelAdvisoryResponse, WeatherResponse
from app.services.weather_service import WeatherService
from app.core.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger("tripwise")
router = APIRouter(prefix="/weather", tags=["Weather"])
_svc   = WeatherService()


# ── GET /weather/{city} — PUBLIC (no auth needed) ─────────────────────────────

@router.get(
    "/{city}",
    response_model=WeatherResponse,
    summary="Get current weather for a city (public)",
    description="""
Returns current weather data for any city.

- Uses **OpenWeatherMap** API if `WEATHER_API_KEY` is set in `.env`
- Falls back to **cache** (up to 3 hours old)
- Returns `source: "unavailable"` if key not configured

**Example response:**
```json
{
  "city": "Goa",
  "temperature": 29.5,
  "feels_like": 33.1,
  "humidity": 78,
  "wind_speed": 18.5,
  "condition": "Light rain",
  "rain_probability": 85,
  "travel_recommendation": "Carry rain gear. Travel may be affected."
}
```
""",
)
def get_current_weather(
    city: str,
    db: Session = Depends(get_db),
):
    return _svc.get_current_weather(db, city)


# ── GET /weather/forecast/{city} — PUBLIC ─────────────────────────────────────
# NOTE: Must be registered BEFORE /{city} to avoid route conflict

@router.get(
    "/forecast/{city}",
    response_model=ForecastResponse,
    summary="Get 7-day weather forecast for a city (public)",
    description="""
Returns a day-by-day weather forecast (up to 7 days).

Also returns:
- `best_days` — dates with ideal travel conditions
- `avoid_days` — dates with heavy rain or extreme heat

Uses OpenWeatherMap 5-day / 3-hour forecast API, aggregated to daily.
""",
)
def get_forecast(
    city: str,
    days: int = Query(7, ge=1, le=7),
    db: Session = Depends(get_db),
):
    return _svc.get_forecast(db, city, days)


# ── GET /weather/travel-advisory/{trip_id} ────────────────────────────────────

@router.get(
    "/travel-advisory/{trip_id}",
    response_model=TravelAdvisoryResponse,
    summary="Get weather-based travel advisory for a trip",
    description="""
Generates a personalised travel advisory based on destination weather.

**Risk Levels:**
- 🟢 `Low` — ideal conditions
- 🟡 `Moderate` — rain / heat — take precautions
- 🔴 `High` — storm / extreme weather — reschedule outdoor plans

**Returns:**
- Recommended and activities to avoid
- Packing suggestions
- Best time of day to sightsee
- Overall travel advice

**Example response:**
```json
{
  "destination": "Goa",
  "risk_level": "Moderate",
  "risk_color": "amber",
  "recommended_activities": ["Museums", "Indoor cafes"],
  "activities_to_avoid": ["Beach visits", "Outdoor trekking"],
  "packing_suggestions": ["Rain jacket", "Umbrella", "Waterproof bag"],
  "best_time_of_day": "Morning (before showers start)",
  "overall_advice": "Light rains are manageable — carry protection."
}
```
""",
)
def get_travel_advisory(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _svc.generate_travel_advisory(db, trip_id)
