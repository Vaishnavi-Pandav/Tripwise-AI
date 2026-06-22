"""
Unit tests for RouteService.
Run with: pytest tests/test_route_service.py -v
"""
import pytest
from unittest.mock import MagicMock
from app.services.route_service import RouteService, ROUTE_DATA, COST_PER_KM


@pytest.fixture
def svc():
    return RouteService()


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []
    db.query.return_value.filter.return_value.first.return_value = None
    db.add = MagicMock()
    db.commit = MagicMock()
    return db


@pytest.fixture
def mock_user():
    u = MagicMock(); u.id = "user-uuid"; return u


class TestRouteData:
    def test_known_pairs_have_required_keys(self):
        for pair, data in ROUTE_DATA.items():
            assert "km" in data
            assert "road_h" in data
            assert "train_h" in data

    def test_distances_are_positive(self):
        for _, data in ROUTE_DATA.items():
            assert data["km"] > 0

    def test_pune_goa_exists(self):
        assert ("pune", "goa") in ROUTE_DATA


class TestBuildModes:
    def test_returns_multiple_modes(self, svc):
        data = ROUTE_DATA[("pune", "goa")]
        modes = svc._build_modes(450, data, 2, None)
        assert len(modes) >= 3

    def test_all_modes_have_cost(self, svc):
        data = ROUTE_DATA[("pune", "goa")]
        modes = svc._build_modes(450, data, 2, None)
        for m in modes:
            assert m.estimated_cost > 0
            assert m.total_cost > 0

    def test_total_cost_is_per_person_times_travelers(self, svc):
        data = ROUTE_DATA[("pune", "goa")]
        modes = svc._build_modes(450, data, 3, None)
        for m in modes:
            assert abs(m.total_cost - m.estimated_cost * 3) < 1

    def test_duration_label_has_h_or_m(self, svc):
        data = ROUTE_DATA[("pune", "goa")]
        modes = svc._build_modes(450, data, 1, None)
        for m in modes:
            assert "h" in m.duration_label or "m" in m.duration_label

    def test_flight_not_included_for_short_route(self, svc):
        data = {"km": 150, "road_h": 3.0, "train_h": 3.5, "flight_h": None}
        modes = svc._build_modes(150, data, 1, None)
        modes_names = [m.mode for m in modes]
        assert "flight" not in modes_names


class TestPickBest:
    def test_flight_best_for_very_long_route(self, svc):
        modes = svc._build_modes(1500, {
            "km": 1500, "road_h": 25, "train_h": 18, "flight_h": 2.5
        }, 1, None)
        best = svc._pick_best(modes, None, 1500)
        assert best == "flight"

    def test_train_best_for_medium_route_with_budget(self, svc):
        modes = svc._build_modes(450, ROUTE_DATA[("pune", "goa")], 2, 5000)
        best = svc._pick_best(modes, 5000, 450)
        assert best in ("train", "bus", "car")

    def test_bus_for_low_budget(self, svc):
        modes = svc._build_modes(450, ROUTE_DATA[("pune", "goa")], 2, 1000)
        best = svc._pick_best(modes, 1000, 450)
        assert best in ("bus", "train")


class TestCostEstimation:
    def test_flight_has_minimum_cost(self, svc):
        cost = svc.estimate_cost(100, "flight", 1)
        assert cost >= 2500

    def test_bus_cheaper_than_flight(self, svc):
        bus_cost    = svc.estimate_cost(450, "bus",    2)
        flight_cost = svc.estimate_cost(450, "flight", 2)
        assert bus_cost < flight_cost

    def test_more_travelers_higher_cost(self, svc):
        c1 = svc.estimate_cost(450, "train", 1)
        c2 = svc.estimate_cost(450, "train", 4)
        assert c2 > c1


class TestHaversine:
    def test_same_point_zero_distance(self, svc):
        assert svc._haversine(15.0, 74.0, 15.0, 74.0) == 0.0

    def test_pune_to_goa_approx(self, svc):
        # Pune ~18.5°N 73.9°E, Goa ~15.5°N 73.8°E
        dist = svc._haversine(18.5, 73.9, 15.5, 73.8)
        assert 300 < dist < 400


class TestCalculateRoute:
    def test_known_route_returns_response(self, svc, mock_db, mock_user):
        result = svc.calculate_route(mock_db, "Pune", "Goa", 2, 5000, mock_user)
        assert result.distance_km == 450
        assert len(result.suggested_modes) >= 3
        assert result.best_mode in ("car", "bus", "train", "flight")

    def test_recommendation_mentions_best_mode(self, svc, mock_db, mock_user):
        result = svc.calculate_route(mock_db, "Pune", "Goa", 2, 5000, mock_user)
        assert result.best_mode.capitalize() in result.recommendation or \
               result.best_mode in result.recommendation.lower()

    def test_unknown_route_uses_estimate(self, svc, mock_db, mock_user):
        result = svc.calculate_route(mock_db, "Nowhere", "Anywhere", 1, None, mock_user)
        assert result.distance_km > 0
