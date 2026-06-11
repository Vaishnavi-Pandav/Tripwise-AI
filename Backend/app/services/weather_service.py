from datetime import date
from sqlalchemy.orm import Session

from app.models.weather import WeatherDataCache
from app.schemas.weather import WeatherOut


class WeatherService:

    @staticmethod
    def _travel_recommendation(condition: str | None, temp: float | None) -> str:
        if not condition or not temp:
            return "Check local forecasts before travelling."
        cond = condition.lower()
        if "rain" in cond or "storm" in cond:
            return "Carry rain gear. Travel may be affected by weather."
        if temp < 5:
            return "Very cold — pack heavy winter clothing."
        if temp < 15:
            return "Cool weather — a jacket is recommended."
        if temp > 35:
            return "Very hot — stay hydrated and avoid midday sun."
        return "Great weather for travelling! Enjoy your trip."

    def get_weather(self, db: Session, city: str) -> WeatherOut:
        today = date.today()
        cached = db.query(WeatherDataCache).filter(
            WeatherDataCache.city.ilike(city),
            WeatherDataCache.forecast_date == today,
        ).first()

        if cached:
            return WeatherOut(
                city=cached.city,
                temperature=float(cached.temperature) if cached.temperature else None,
                feels_like=None,
                weather_condition=cached.weather_condition,
                humidity=float(cached.humidity) if cached.humidity else None,
                forecast_date=cached.forecast_date,
                travel_recommendation=self._travel_recommendation(
                    cached.weather_condition, float(cached.temperature) if cached.temperature else None
                ),
                source="cache",
            )

        # No live API key wired — return instructive placeholder
        return WeatherOut(
            city=city,
            temperature=None,
            feels_like=None,
            weather_condition="Data not available",
            humidity=None,
            forecast_date=today,
            travel_recommendation="Set WEATHER_API_KEY in .env for live weather data.",
            source="unavailable",
        )
