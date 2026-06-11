"""
Unit tests for BudgetService.calculate_breakdown()
Run with: pytest tests/test_budget_service.py -v
"""
import pytest
from app.services.budget_service import BudgetService


@pytest.fixture
def svc():
    return BudgetService()


class TestCalculateBreakdown:

    def test_totals_within_budget(self, svc):
        b = svc.calculate_breakdown(15000, days=4, travelers=2, travel_mode="flight")
        assert b.total <= 15000
        assert b.budget_remaining >= 0

    def test_all_costs_positive(self, svc):
        b = svc.calculate_breakdown(10000, days=5, travelers=3, travel_mode="train")
        assert b.transport_cost > 0
        assert b.accommodation_cost > 0
        assert b.food_cost > 0
        assert b.activity_cost > 0
        assert b.miscellaneous_cost > 0

    def test_per_person_scales_with_travelers(self, svc):
        b1 = svc.calculate_breakdown(10000, days=3, travelers=1, travel_mode="road")
        b2 = svc.calculate_breakdown(10000, days=3, travelers=2, travel_mode="road")
        assert b1.per_person > b2.per_person

    def test_daily_cost_scales_with_days(self, svc):
        b1 = svc.calculate_breakdown(10000, days=2, travelers=1, travel_mode="bus")
        b2 = svc.calculate_breakdown(10000, days=7, travelers=1, travel_mode="bus")
        assert b1.daily_per_person > b2.daily_per_person

    def test_flight_higher_transport_than_bus(self, svc):
        bf = svc.calculate_breakdown(10000, days=4, travelers=2, travel_mode="flight")
        bb = svc.calculate_breakdown(10000, days=4, travelers=2, travel_mode="bus")
        assert bf.transport_cost > bb.transport_cost

    def test_luxury_higher_accommodation_than_budget(self, svc):
        bl = svc.calculate_breakdown(20000, days=4, travelers=2, accommodation_type="luxury")
        bb = svc.calculate_breakdown(20000, days=4, travelers=2, accommodation_type="budget")
        assert bl.accommodation_cost > bb.accommodation_cost

    def test_adventure_higher_activity_than_city(self, svc):
        ba = svc.calculate_breakdown(10000, days=4, travelers=2, destination_category="adventure")
        bc = svc.calculate_breakdown(10000, days=4, travelers=2, destination_category="city")
        assert ba.activity_cost >= bc.activity_cost

    def test_weights_normalised(self, svc):
        """Total should never exceed budget."""
        for mode in ["flight", "train", "bus", "road", "car", "mixed"]:
            for accom in ["budget", "mid-range", "luxury"]:
                b = svc.calculate_breakdown(
                    5000, days=3, travelers=1,
                    travel_mode=mode, accommodation_type=accom,
                )
                assert b.total <= 5000 + 1, f"Over budget for {mode}/{accom}"

    def test_zero_budget_returns_zero_costs(self, svc):
        """Zero budget produces zero costs — validation is at schema layer."""
        b = svc.calculate_breakdown(0, days=3, travelers=1)
        assert b.total == 0
        assert b.transport_cost == 0

    def test_hotel_cost_alias(self, svc):
        b = svc.calculate_breakdown(10000, days=3, travelers=2)
        assert b.hotel_cost == b.accommodation_cost
