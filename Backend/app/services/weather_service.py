import logging
from datetime import date, datetime, timedelta
from typing import Optional

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.trip import Trip
from app.models.weather import WeatherDataCache
from app.schemas.weather import (
    ForecastDay,
    ForecastResponse,
    TravelAdvisoryResponse,
    WeatherResponse,
)

logger = logging.getLogger("tripwise")

# ── OpenWeatherMap endpoints ───────────────────────────────────────────────────
OWM_CURRENT  = "https://api.openweathermap.org/data/2.5/weather"
OWM_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"

# ── Cache TTL in hours ─────────────────────────────────────────────────────────
CACHE_TTL_HOURS = 3


# ── Advisory rule tables ───────────────────────────────────────────────────────

ADVISORY_RULES: dict[str, dict] = {
    "rain": {
        "risk":   "Moderate",
        "color":  "amber",
        "avoid":  ["Beach visits", "Outdoor trekking", "Open-air sightseeing"],
        "rec":    ["Museums", "Indoor cafes", "Shopping malls", "Temple visits"],
        "pack":   ["Rain jacket / poncho", "Waterproof bag", "Umbrella", "Quick-dry shoes"],
        "time":   "Morning (before showers start)",
        "advice": "Light rains are manageable — carry protection. Heavy rain: reschedule outdoor plans.",
    },
    "storm": {
        "risk":   "High",
        "color":  "red",
        "avoid":  ["All outdoor activities", "Beach", "Trekking", "Water sports"],
        "rec":    ["Stay indoors", "Plan indoor activities"],
        "pack":   ["Heavy rain gear", "Emergency supplies"],
        "time":   "Avoid travel during storm hours",
        "advice": "Postpone outdoor activities. Monitor local alerts.",
    },
    "hot": {
        "risk":   "Moderate",
        "color":  "amber",
        "avoid":  ["Afternoon sightseeing (12pm–4pm)", "Long outdoor walks", "Sports"],
        "rec":    ["Early morning sightseeing", "Evening walks", "Swimming", "Indoor attractions"],
        "pack":   ["Sunscreen SPF 50+", "Hat / cap", "Sunglasses", "Rehydration salts", "Light cotton clothes"],
        "time":   "Early morning or after 5pm",
        "advice": "Stay hydrated. Avoid midday sun. Wear light, breathable clothing.",
    },
    "cold": {
        "risk":   "Low",
        "color":  "green",
        "avoid":  ["Water sports", "Late-night outdoor activities"],
        "rec":    ["Warm cafes", "Historical sites", "Mountain treks", "Local cuisine"],
        "pack":   ["Thermal inner wear", "Jacket / parka", "Woollen socks", "Hand warmers"],
        "time":   "Midday when temperatures peak",
        "advice": "Bundle up for cold nights. Daytime is generally comfortable.",
    },
    "clear": {
        "risk":   "Low",
        "color":  "green",
        "avoid":  [],
        "rec":    ["Beach", "Sightseeing", "Trekking", "Photography", "Water sports"],
        "pack":   ["Sunscreen", "Light clothing", "Water bottle"],
        "time":   "All day — avoid peak afternoon heat",
        "advice": "Perfect weather! Enjoy outdoor activities.",
    },
}


class WeatherService:

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_current_weather(self, db: Optional[Session], city: str) -> WeatherResponse:
        """
        Fetch current weather for a city.
        Checks cache first (TTL = 3 hours). Falls back to OWM API.
        Returns placeholder if API key not configured.
        If db is None (DB unavailable), skips cache and goes direct to API.
        """
        today = date.today()

        # Only use cache if DB is available
        if db is not None:
            cached = self._get_from_cache(db, city, today)
            if cached and self._is_fresh(cached):
                return self._cache_to_response(cached, "cache")
        else:
            cached = None

        if not settings.WEATHER_API_KEY:
            return self._unavailable_response(city, today)

        try:
            data = self._fetch_current(city)
            if db is not None:
                cached = self.cache_weather(db, city, data, today)
                return self._cache_to_response(cached, "live")
            else:
                # No DB — return response directly without caching
                rule = self._match_rule(data.get("condition"), data.get("temperature"))
                return WeatherResponse(
                    city=city,
                    temperature=data.get("temperature"),
                    feels_like=data.get("feels_like"),
                    humidity=data.get("humidity"),
                    wind_speed=data.get("wind_speed"),
                    weather_condition=data.get("condition"),
                    weather_icon=data.get("icon"),
                    rain_probability=data.get("rain_prob"),
                    forecast_date=today,
                    travel_recommendation=rule["advice"],
                    source="live",
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Weather fetch error for {city}: {e}")
            if cached:
                return self._cache_to_response(cached, "cache")
            return self._unavailable_response(city, today)

    def get_forecast(self, db: Optional[Session], city: str, days: int = 7) -> ForecastResponse:
        """
        Return up to 7-day forecast. Uses OWM free tier (5-day / 3-hour).
        Aggregates to daily if live; uses cache if available.
        """
        if not settings.WEATHER_API_KEY:
            return self._mock_forecast(city, days)

        try:
            raw = self._fetch_forecast(city)
            forecast_days = self._aggregate_daily(raw, days)
            # Cache each day only if DB is available
            if db is not None:
                for fd in forecast_days:
                    self.cache_weather(db, city, {
                        "temperature": fd.temperature_max,
                        "feels_like":  fd.temperature_max,
                        "humidity":    fd.humidity,
                        "wind_speed":  fd.wind_speed,
                        "condition":   fd.weather_condition,
                        "icon":        fd.weather_icon,
                        "rain_prob":   fd.rain_probability,
                    }, fd.forecast_date)

            best  = [f.forecast_date for f in forecast_days if self._is_good_day(f)]
            avoid = [f.forecast_date for f in forecast_days if self._is_bad_day(f)]

            return ForecastResponse(city=city, days=forecast_days,
                                    source="live", best_days=best, avoid_days=avoid)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Forecast fetch error for {city}: {e}")
            return self._mock_forecast(city, days)

    def cache_weather(
        self,
        db: Session,
        city: str,
        data: dict,
        forecast_date: date,
    ) -> WeatherDataCache:
        """Upsert weather data into the cache table."""
        existing = self._get_from_cache(db, city, forecast_date)
        values = {
            "temperature":       data.get("temperature"),
            "feels_like":        data.get("feels_like"),
            "humidity":          data.get("humidity"),
            "wind_speed":        data.get("wind_speed"),
            "weather_condition": data.get("condition"),
            "weather_icon":      data.get("icon"),
            "rain_probability":  data.get("rain_prob"),
            "fetched_at":        datetime.utcnow(),
        }
        if existing:
            for k, v in values.items():
                setattr(existing, k, v)
        else:
            existing = WeatherDataCache(city=city, forecast_date=forecast_date, **values)
            db.add(existing)
        db.commit()
        db.refresh(existing)
        logger.info(f"Weather cached: {city} {forecast_date}")
        return existing

    def generate_travel_advisory(
        self, db: Session, trip_id: str
    ) -> TravelAdvisoryResponse:
        """
        Generate a weather-based travel advisory for a trip.
        Fetches current weather for the destination and applies rule engine.
        """
        trip: Optional[Trip] = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        city = trip.destination_location
        weather = self.get_current_weather(db, city)
        rule    = self._match_rule(weather.weather_condition, weather.temperature)

        travel_dates = (
            f"Day 1 – Day {trip.number_of_days}"
            if trip.number_of_days else "Full trip"
        )
        summary = (
            f"{weather.weather_condition or 'Unknown'}, "
            f"{weather.temperature or '--'}°C, "
            f"Humidity: {weather.humidity or '--'}%, "
            f"Rain Probability: {weather.rain_probability or 0:.0f}%"
        )

        return TravelAdvisoryResponse(
            trip_id=trip_id,
            destination=city,
            travel_dates=travel_dates,
            risk_level=rule["risk"],
            risk_color=rule["color"],
            weather_summary=summary,
            recommended_activities=rule["rec"],
            activities_to_avoid=rule["avoid"],
            packing_suggestions=rule["pack"],
            best_time_of_day=rule["time"],
            overall_advice=rule["advice"],
        )

    # ── OWM API calls ──────────────────────────────────────────────────────────

    @staticmethod
    def _fetch_current(city: str) -> dict:
        params = {
            "q":     city,
            "appid": settings.WEATHER_API_KEY,
            "units": "metric",
        }
        r = httpx.get(OWM_CURRENT, params=params, timeout=10)
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
        if r.status_code == 401:
            raise HTTPException(status_code=503, detail="Invalid Weather API key")
        r.raise_for_status()
        d = r.json()
        return {
            "temperature": d["main"]["temp"],
            "feels_like":  d["main"]["feels_like"],
            "humidity":    d["main"]["humidity"],
            "wind_speed":  round(d["wind"]["speed"] * 3.6, 1),  # m/s → km/h
            "condition":   d["weather"][0]["description"].capitalize(),
            "icon":        d["weather"][0]["icon"],
            "rain_prob":   d.get("rain", {}).get("1h", 0) * 10,
        }

    @staticmethod
    def _fetch_forecast(city: str) -> dict:
        params = {
            "q":     city,
            "appid": settings.WEATHER_API_KEY,
            "units": "metric",
            "cnt":   40,   # 5 days × 8 slots
        }
        r = httpx.get(OWM_FORECAST, params=params, timeout=10)
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _aggregate_daily(raw: dict, max_days: int) -> list[ForecastDay]:
        """Aggregate 3-hour OWM slots → one ForecastDay per calendar day."""
        from collections import defaultdict
        slots = raw.get("list", [])
        by_day: dict[str, list] = defaultdict(list)
        for slot in slots:
            day_str = slot["dt_txt"][:10]
            by_day[day_str].append(slot)

        days: list[ForecastDay] = []
        for day_str, slot_list in sorted(by_day.items()):
            if len(days) >= max_days:
                break
            temps = [s["main"]["temp"] for s in slot_list]
            hum   = [s["main"]["humidity"] for s in slot_list]
            wind  = [s["wind"]["speed"] * 3.6 for s in slot_list]
            midday = slot_list[min(4, len(slot_list) - 1)]
            cond  = midday["weather"][0]["description"].capitalize()
            icon  = midday["weather"][0]["icon"]
            rain  = max((s.get("pop", 0) * 100 for s in slot_list), default=0)

            days.append(ForecastDay(
                forecast_date=date.fromisoformat(day_str),
                temperature_max=round(max(temps), 1),
                temperature_min=round(min(temps), 1),
                humidity=round(sum(hum) / len(hum), 1),
                wind_speed=round(sum(wind) / len(wind), 1),
                weather_condition=cond,
                weather_icon=icon,
                rain_probability=round(rain, 1),
                summary=WeatherService._day_summary(cond, max(temps), rain),
            ))
        return days

    # ── Rule engine ────────────────────────────────────────────────────────────

    @staticmethod
    def _match_rule(condition: Optional[str], temp: Optional[float]) -> dict:
        cond = (condition or "").lower()
        if any(w in cond for w in ("storm", "thunder", "tornado")):
            return ADVISORY_RULES["storm"]
        if any(w in cond for w in ("rain", "drizzle", "shower")):
            return ADVISORY_RULES["rain"]
        if temp is not None and temp > 35:
            return ADVISORY_RULES["hot"]
        if temp is not None and temp < 10:
            return ADVISORY_RULES["cold"]
        return ADVISORY_RULES["clear"]

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _get_from_cache(db: Session, city: str, d: date) -> Optional[WeatherDataCache]:
        return db.query(WeatherDataCache).filter(
            WeatherDataCache.city.ilike(city),
            WeatherDataCache.forecast_date == d,
        ).first()

    @staticmethod
    def _is_fresh(cached: WeatherDataCache) -> bool:
        age = (datetime.utcnow() - cached.fetched_at.replace(tzinfo=None)).total_seconds()
        return age < CACHE_TTL_HOURS * 3600

    @staticmethod
    def _cache_to_response(cached: WeatherDataCache, source: str) -> WeatherResponse:
        temp = float(cached.temperature) if cached.temperature else None
        cond = cached.weather_condition
        rule = WeatherService._match_rule(cond, temp)
        return WeatherResponse(
            city=cached.city,
            temperature=temp,
            feels_like=float(cached.feels_like) if cached.feels_like else None,
            humidity=float(cached.humidity)     if cached.humidity    else None,
            wind_speed=cached.wind_speed,
            weather_condition=cond,
            weather_icon=cached.weather_icon,
            rain_probability=cached.rain_probability,
            forecast_date=cached.forecast_date,
            travel_recommendation=rule["advice"],
            source=source,
        )

    @staticmethod
    def _unavailable_response(city: str, d: date) -> WeatherResponse:
        return WeatherResponse(
            city=city,
            temperature=None, feels_like=None,
            humidity=None, wind_speed=None,
            weather_condition="Data unavailable",
            weather_icon=None, rain_probability=None,
            forecast_date=d,
            travel_recommendation="Add WEATHER_API_KEY to .env for live weather data.",
            source="unavailable",
        )

    @staticmethod
    def _mock_forecast(city: str, days: int) -> ForecastResponse:
        today = date.today()
        mock  = [
            ForecastDay(
                forecast_date=today + timedelta(days=i),
                temperature_max=30, temperature_min=24,
                humidity=70, wind_speed=15,
                weather_condition="Partly Cloudy",
                weather_icon="02d", rain_probability=20,
                summary="Partly cloudy, comfortable temperatures",
            )
            for i in range(days)
        ]
        return ForecastResponse(city=city, days=mock,
                                source="unavailable",
                                best_days=[today], avoid_days=[])

    @staticmethod
    def _day_summary(condition: str, temp_max: float, rain_prob: float) -> str:
        if rain_prob > 70:
            return f"Rainy day, {temp_max}°C — carry rain gear"
        if temp_max > 35:
            return f"Very hot, {temp_max}°C — avoid afternoon outdoors"
        if temp_max < 10:
            return f"Cold day, {temp_max}°C — dress warmly"
        return f"{condition}, {temp_max}°C — good travel conditions"

    @staticmethod
    def _is_good_day(fd: ForecastDay) -> bool:
        return (
            (fd.rain_probability or 0) < 30
            and (fd.temperature_max or 25) < 35
            and (fd.temperature_max or 25) > 10
        )

    @staticmethod
    def _is_bad_day(fd: ForecastDay) -> bool:
        return (
            (fd.rain_probability or 0) > 70
            or (fd.temperature_max or 25) > 40
        )

    # Backwards compat
    def get_weather(self, db: Session, city: str) -> WeatherResponse:
        return self.get_current_weather(db, city)
