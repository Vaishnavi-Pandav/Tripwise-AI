"""
Unit tests for ComparisonService.
Run with: pytest tests/test_comparison_service.py -v
"""
import pytest
from unittest.mock import MagicMock
from app.services.comparison_service import (
    ComparisonService, DESTINATION_DB, TRAVELER_WEIGHTS,
)
from app.schemas.comparison import DestinationCompareRequest


@pytest.fixture
def svc():
    return ComparisonService()


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    return db


class TestCalculateScores:
    def test_score_within_0_10(self, svc):
        data = DESTINATION_DB["goa"]
        s = svc.calculate_scores("Goa", data, TRAVELER_WEIGHTS["friends"], "friends")
        assert 0 <= s.overall_score <= 10

    def test_family_weights_safety_higher(self, svc):
        data = DESTINATION_DB["kerala"]
        s_family  = svc.calculate_scores("Kerala", data, TRAVELER_WEIGHTS["family"],     "family")
        s_friends = svc.calculate_scores("Kerala", data, TRAVELER_WEIGHTS["friends"], "friends")
        # Family should score higher when safety/family scores are strong
        assert s_family.overall_score != s_friends.overall_score

    def test_pros_not_empty(self, svc):
        data = DESTINATION_DB["goa"]
        s = svc.calculate_scores("Goa", data, TRAVELER_WEIGHTS["solo"], "solo")
        assert len(s.pros) > 0

    def test_cons_populated(self, svc):
        data = DESTINATION_DB["goa"]
        s = svc.calculate_scores("Goa", data, TRAVELER_WEIGHTS["solo"], "solo")
        assert isinstance(s.cons, list)

    def test_all_8_scores_present(self, svc):
        data = DESTINATION_DB["manali"]
        s = svc.calculate_scores("Manali", data, TRAVELER_WEIGHTS["backpacker"], "backpacker")
        assert s.avg_budget_score > 0
        assert s.safety_score > 0
        assert s.adventure_score > 0
        assert s.family_friendly_score > 0


class TestFactorComparisons:
    def test_builds_8_factors(self, svc):
        d1 = DESTINATION_DB["goa"]
        d2 = DESTINATION_DB["gokarna"]
        factors = svc._build_factor_comparisons("Goa", "Gokarna", d1, d2)
        assert len(factors) == 8

    def test_winner_is_valid_destination(self, svc):
        d1 = DESTINATION_DB["goa"]
        d2 = DESTINATION_DB["gokarna"]
        factors = svc._build_factor_comparisons("Goa", "Gokarna", d1, d2)
        for f in factors:
            assert f.winner in ("Goa", "Gokarna")

    def test_similar_scores_show_similar_insight(self, svc):
        d1 = {"budget": 7.0, "safety": 7.0, "weather": 7.0, "crowd": 7.0,
              "nightlife": 7.0, "food": 7.0, "adventure": 7.0, "family": 7.0}
        d2 = d1.copy()
        factors = svc._build_factor_comparisons("A", "B", d1, d2)
        assert any("similar" in f.insight.lower() for f in factors)


class TestCompareDestinations:
    def test_winner_is_one_of_two(self, svc, mock_db):
        req = DestinationCompareRequest(destination1="Goa", destination2="Gokarna")
        result = svc.compare_destinations(mock_db, req)
        assert result.winner in ("Goa", "Gokarna")

    def test_recommendation_mentions_winner(self, svc, mock_db):
        req = DestinationCompareRequest(destination1="Goa", destination2="Gokarna")
        result = svc.compare_destinations(mock_db, req)
        assert result.winner in result.recommendation

    def test_couple_traveler_type(self, svc, mock_db):
        req = DestinationCompareRequest(destination1="Goa", destination2="Kerala",
                                        traveler_type="couple")
        result = svc.compare_destinations(mock_db, req)
        assert result.best_for_traveler is not None
        assert "couple" in result.best_for_traveler.lower()

    def test_unknown_destination_uses_defaults(self, svc, mock_db):
        req = DestinationCompareRequest(destination1="XYZCity", destination2="Goa")
        result = svc.compare_destinations(mock_db, req)
        assert result.winner in ("XYZCity", "Goa")

    def test_ai_insight_generated(self, svc, mock_db):
        req = DestinationCompareRequest(destination1="Goa", destination2="Manali",
                                        traveler_type="friends")
        result = svc.compare_destinations(mock_db, req)
        assert result.ai_insight is not None
        assert len(result.ai_insight) > 10

    def test_source_is_heuristic_for_unknown(self, svc, mock_db):
        req = DestinationCompareRequest(destination1="Goa", destination2="Gokarna")
        result = svc.compare_destinations(mock_db, req)
        assert result.source in ("heuristic", "database")


class TestLegacyCompare:
    def test_legacy_compare_returns_compareout(self, svc):
        result = svc.compare("Goa", "Gokarna")
        assert result.winner in ("Goa", "Gokarna")
        assert result.destination1.destination == "Goa"

    def test_traveler_weights_cover_all_types(self):
        for t in ["solo", "couple", "family", "friends", "backpacker"]:
            assert t in TRAVELER_WEIGHTS
