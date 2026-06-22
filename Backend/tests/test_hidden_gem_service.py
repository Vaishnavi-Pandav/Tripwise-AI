"""
Unit tests for HiddenGemService.
Run with: pytest tests/test_hidden_gem_service.py -v
"""
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.services.hidden_gem_service import (
    HiddenGemService, BUILT_IN_GEMS,
    TYPE_CATEGORY_PREFERENCE, BUDGET_TIERS,
)


@pytest.fixture
def svc():
    return HiddenGemService()


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.offset.return_value \
        .limit.return_value.all.return_value = []
    return db


@pytest.fixture
def mock_trip():
    t = MagicMock()
    t.id                   = "trip-uuid"
    t.destination_location = "Goa"
    t.budget               = 15000
    t.number_of_days       = 4
    t.number_of_travelers  = 2
    t.travel_mode          = "flight"
    return t


# ── Built-in knowledge base ────────────────────────────────────────────────────

class TestBuiltInGems:
    def test_goa_has_gems(self):
        assert "goa" in BUILT_IN_GEMS
        assert len(BUILT_IN_GEMS["goa"]) >= 3

    def test_all_gems_have_required_fields(self):
        for city, gems in BUILT_IN_GEMS.items():
            for g in gems:
                assert "name" in g, f"Missing name in {city}"
                assert "category" in g, f"Missing category in {city}"
                assert "crowd" in g, f"Missing crowd in {city}"

    def test_traveler_type_preferences_cover_all_types(self):
        for t in ["solo", "couple", "family", "friends", "backpacker"]:
            assert t in TYPE_CATEGORY_PREFERENCE
            assert len(TYPE_CATEGORY_PREFERENCE[t]) > 0


# ── Traveler type inference ────────────────────────────────────────────────────

class TestTravelerTypeInference:
    def test_solo_traveler(self, svc):
        trip = MagicMock(); trip.number_of_travelers = 1
        assert svc._infer_traveler_type(trip) == "solo"

    def test_couple(self, svc):
        trip = MagicMock(); trip.number_of_travelers = 2
        assert svc._infer_traveler_type(trip) == "couple"

    def test_group_friends(self, svc):
        trip = MagicMock(); trip.number_of_travelers = 5
        assert svc._infer_traveler_type(trip) == "friends"


# ── Scoring engine ─────────────────────────────────────────────────────────────

class TestScoringEngine:
    def test_preferred_category_scores_higher(self, svc):
        preferred_cat = TYPE_CATEGORY_PREFERENCE["couple"][0]
        gem_preferred = {"name": "A", "category": preferred_cat, "cost": 200,
                         "crowd": "low", "types": "couple"}
        gem_other     = {"name": "B", "category": "adventure",   "cost": 200,
                         "crowd": "high", "types": "friends"}
        candidates = [gem_other, gem_preferred]
        scored = svc._score_candidates(candidates, "couple", 3000)
        assert scored[0]["name"] == "A"

    def test_free_gem_scores_high_for_backpacker(self, svc):
        free_gem = {"name": "Free Spot", "category": "trek", "cost": 0,
                    "crowd": "low", "types": "backpacker"}
        expensive = {"name": "Costly",   "category": "trek", "cost": 5000,
                     "crowd": "low", "types": "backpacker"}
        scored = svc._score_candidates([expensive, free_gem], "backpacker", 500)
        assert scored[0]["name"] == "Free Spot"

    def test_low_crowd_preferred_for_solo(self, svc):
        low  = {"name": "Quiet", "category": "nature", "cost": 0,
                "crowd": "low",  "types": "solo"}
        high = {"name": "Busy",  "category": "nature", "cost": 0,
                "crowd": "high", "types": "solo"}
        scored = svc._score_candidates([high, low], "solo", 2000)
        assert scored[0]["name"] == "Quiet"


# ── Reasoning engine ───────────────────────────────────────────────────────────

class TestReasoningEngine:
    def test_reason_mentions_gem_name(self, svc):
        gem = {"name": "Butterfly Beach", "category": "beach",
               "cost": 500, "crowd": "low", "types": "couple"}
        reason = svc.generate_reasoning(gem, "couple", 3000)
        assert "Butterfly Beach" in reason

    def test_free_gem_mentioned_in_reason(self, svc):
        gem = {"name": "Chapora Fort", "category": "viewpoint",
               "cost": 0, "crowd": "low", "types": "solo"}
        reason = svc.generate_reasoning(gem, "solo", 2000)
        assert "free" in reason.lower() or "₹" not in reason

    def test_crowd_mentioned_for_low_crowd(self, svc):
        gem = {"name": "Hidden Lake", "category": "nature",
               "cost": 100, "crowd": "low", "types": "couple"}
        reason = svc.generate_reasoning(gem, "couple", 3000)
        assert "crowd" in reason.lower() or "tourist" in reason.lower()


# ── Recommendation endpoint ────────────────────────────────────────────────────

class TestRecommendHiddenGems:
    def test_trip_not_found_raises_404(self, svc, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc:
            svc.recommend_hidden_gems(mock_db, "bad-uuid")
        assert exc.value.status_code == 404

    def test_returns_recommendations_for_known_city(self, svc, mock_db, mock_trip):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_trip
        mock_db.query.return_value.filter.return_value.all.return_value = []
        result = svc.recommend_hidden_gems(mock_db, "trip-uuid")
        assert result.destination == "Goa"
        assert len(result.recommendations) > 0

    def test_response_has_reasons(self, svc, mock_db, mock_trip):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_trip
        mock_db.query.return_value.filter.return_value.all.return_value = []
        result = svc.recommend_hidden_gems(mock_db, "trip-uuid")
        for r in result.recommendations:
            assert len(r.reason) > 10

    def test_unknown_city_returns_empty(self, svc, mock_db):
        trip = MagicMock()
        trip.destination_location = "UnknownXYZCity"
        trip.budget = 10000; trip.number_of_days = 3
        trip.number_of_travelers = 2
        mock_db.query.return_value.filter.return_value.first.return_value = trip
        mock_db.query.return_value.filter.return_value.all.return_value = []
        result = svc.recommend_hidden_gems(mock_db, "trip-uuid")
        assert result.total_found == 0
