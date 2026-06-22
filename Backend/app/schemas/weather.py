from datetime import date
from typing import Optional
from pydantic import BaseModel


# ── Current weather ────────────────────────────────────────────────────────────

class WeatherResponse(BaseModel):
    city:              str
    temperature:       Optional[float]     # °C
    feels_like:        Optional[float]     # °C
    humidity:          Optional[float]     # %
    wind_speed:        Optional[float]     # km/h
    weather_condition: Optional[str]
    weather_icon:      Optional[str]
    rain_probability:  Optional[float]     # 0–100
    forecast_date:     Optional[date]
    travel_recommendation: str
    source:            str = "live"        # "live" | "cache" | "unavailable"

    # Backwards compat
    @property
    def condition(self) -> Optional[str]:
        return self.weather_condition


# ── Forecast ───────────────────────────────────────────────────────────────────

class ForecastDay(BaseModel):
    forecast_date:     date
    temperature_max:   Optional[float]
    temperature_min:   Optional[float]
    humidity:          Optional[float]
    wind_speed:        Optional[float]
    weather_condition: Optional[str]
    weather_icon:      Optional[str]
    rain_probability:  Optional[float]
    summary:           str               # one-line human description


class ForecastResponse(BaseModel):
    city:      str
    days:      list[ForecastDay]
    source:    str = "live"
    best_days: list[date]               # dates with best weather
    avoid_days: list[date]              # dates with worst weather


# ── Travel advisory ────────────────────────────────────────────────────────────

class TravelAdvisoryResponse(BaseModel):
    trip_id:               str
    destination:           str
    travel_dates:          str           # "Day 1 – Day N"
    risk_level:            str           # "Low" | "Moderate" | "High"
    risk_color:            str           # "green" | "amber" | "red"
    weather_summary:       str
    recommended_activities: list[str]
    activities_to_avoid:   list[str]
    packing_suggestions:   list[str]
    best_time_of_day:      str
    overall_advice:        str


# ── Backwards compat alias ────────────────────────────────────────────────────
WeatherOut = WeatherResponse
