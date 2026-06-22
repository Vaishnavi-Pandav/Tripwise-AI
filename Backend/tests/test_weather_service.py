"""
Unit tests for WeatherService — fully mocked, no real API calls.
Run with: pytest tests/test_weather_service.py -v
"""
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.services.weather_service import WeatherService, ADVISORY_RULES, CACHE_TTL_HOURS
from app.schemas.weather import ForecastDay


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def svc():
    return WeatherService()


@pytest.fixture
def mock_db():
    return MagicMock()


# ── Advisory rule engine ───────────────────────────────────────────────────────

class TestAdvisoryRules:

    def test_storm_gives_high_risk(self, svc):
        rule = svc._match_rule("Thunderstorm", 28)
        assert rule["risk"] == "High"
        assert rule["color"] == "red"

    def test_rain_gives_moderate_risk(self, svc):
        rule = svc._match_rule("Light rain", 26)
        assert rule["risk"] == "Moderate"
        assert rule["color"] == "amber"

    def test_extreme_heat_gives_moderate_risk(self, svc):
        rule = svc._match_rule("Clear sky", 38)
        assert rule["risk"] == "Moderate"
        assert rule["color"] == "amber"

    def test_cold_gives_low_risk(self, svc):
        rule = svc._match_rule("Clear sky", 5)
        assert rule["risk"] == "Low"

    def test_clear_good_weather_gives_low_risk(self, svc):
        rule = svc._match_rule("Clear sky", 28)
        assert rule["risk"] == "Low"
        assert rule["color"] == "green"

    def test_drizzle_matches_rain_rule(self, svc):
        rule = svc._match_rule("Drizzle", 24)
        assert rule["risk"] == "Moderate"

    def test_rain_rule_has_avoid_list(self):
        assert len(ADVISORY_RULES["rain"]["avoid"]) > 0

    def test_rain_rule_has_packing_suggestions(self):
        assert "Umbrella" in ADVISORY_RULES["rain"]["pack"] or \
               any("umbrella" in p.lower() for p in ADVISORY_RULES["rain"]["pack"])

    def test_hot_rule_avoids_afternoon(self):
        assert any("afternoon" in a.lower() for a in ADVISORY_RULES["hot"]["avoid"])

    def test_none_condition_defaults_to_clear(self, svc):
        rule = svc._match_rule(None, 25)
        assert rule["risk"] == "Low"


# ── Cache freshness ────────────────────────────────────────────────────────────

class TestCacheFreshness:

    def test_fresh_cache_returns_true(self, svc):
        from datetime import datetime, timezone
        cached = MagicMock()
        cached.fetched_at = datetime.utcnow().replace(tzinfo=None)
        assert svc._is_fresh(cached) is True

    def test_stale_cache_returns_false(self, svc):
        from datetime import datetime, timedelta
        cached = MagicMock()
        cached.fetched_at = (
            __import__("datetime").datetime.utcnow()
            - __import__("datetime").timedelta(hours=CACHE_TTL_HOURS + 1)
        )
        assert svc._is_fresh(cached) is False


# ── Unavailable response ───────────────────────────────────────────────────────

class TestUnavailableResponse:

    def test_unavailable_has_correct_source(self, svc):
        resp = svc._unavailable_response("Goa", date.today())
        assert resp.source == "unavailable"
        assert resp.city == "Goa"

    def test_unavailable_has_advice(self, svc):
        resp = svc._unavailable_response("Goa", date.today())
        assert len(resp.travel_recommendation) > 0


# ── Forecast helpers ───────────────────────────────────────────────────────────

class TestForecastHelpers:

    def test_good_day_low_rain_mild_temp(self, svc):
        fd = ForecastDay(
            forecast_date=date.today(),
            temperature_max=28, temperature_min=22,
            humidity=60, wind_speed=12,
            weather_condition="Clear", weather_icon="01d",
            rain_probability=10,
            summary="Clear and warm",
        )
        assert svc._is_good_day(fd) is True

    def test_bad_day_heavy_rain(self, svc):
        fd = ForecastDay(
            forecast_date=date.today(),
            temperature_max=28, temperature_min=24,
            humidity=90, wind_speed=20,
            weather_condition="Heavy Rain", weather_icon="10d",
            rain_probability=90,
            summary="Heavy rain",
        )
        assert svc._is_bad_day(fd) is True

    def test_mock_forecast_returns_correct_days(self, svc):
        result = svc._mock_forecast("Goa", 5)
        assert len(result.days) == 5
        assert result.city == "Goa"
        assert result.source == "unavailable"

    def test_day_summary_rain(self, svc):
        summary = svc._day_summary("Rainy", 28, 80)
        assert "rain" in summary.lower() or "gear" in summary.lower()

    def test_day_summary_hot(self, svc):
        summary = svc._day_summary("Clear", 40, 10)
        assert "hot" in summary.lower() or "afternoon" in summary.lower()


# ── Get current weather — no API key ──────────────────────────────────────────

class TestGetCurrentWeather:

    def test_no_api_key_returns_unavailable(self, svc, mock_db, monkeypatch):
        monkeypatch.setattr("app.services.weather_service.settings.WEATHER_API_KEY", "")
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = svc.get_current_weather(mock_db, "Goa")
        assert result.source == "unavailable"

    def test_returns_cache_when_fresh(self, svc, mock_db):
        from datetime import datetime
        cached = MagicMock()
        cached.city              = "Goa"
        cached.temperature       = 29
        cached.feels_like        = 32
        cached.humidity          = 75
        cached.wind_speed        = 15
        cached.weather_condition = "Clear sky"
        cached.weather_icon      = "01d"
        cached.rain_probability  = 10
        cached.forecast_date     = date.today()
        cached.fetched_at        = datetime.utcnow()
        mock_db.query.return_value.filter.return_value.first.return_value = cached
        result = svc.get_current_weather(mock_db, "Goa")
        assert result.source == "cache"
        assert result.city == "Goa"
