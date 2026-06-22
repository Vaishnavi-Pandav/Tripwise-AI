"""
Unit tests for HotelService recommendation engine scoring.
Run with: pytest tests/test_hotel_service.py -v
"""
import pytest
from unittest.mock import MagicMock
from app.services.hotel_service import HotelService
from app.models.hotel import Hotel


def make_hotel(price, rating, category="standard", amenities=None) -> Hotel:
    h = Hotel()
    h.price_per_night = price
    h.rating          = rating
    h.hotel_category  = category
    h.amenities       = '["WiFi","Pool","Restaurant","AC","Gym","Spa"]' if amenities is None else amenities
    return h


class TestScoringEngine:

    def test_score_within_0_to_100(self):
        hotel = make_hotel(2000, 4.5)
        score = HotelService._score_hotel(hotel, 2000)
        assert 0 <= score.total <= 100

    def test_perfect_budget_match_scores_high(self):
        hotel = make_hotel(2000, 5.0, "luxury")
        score = HotelService._score_hotel(hotel, 2000)
        assert score.total >= 80

    def test_over_budget_hotel_scores_lower(self):
        affordable = make_hotel(1000, 4.0)
        expensive  = make_hotel(5000, 4.0)
        s1 = HotelService._score_hotel(affordable, 1000)
        s2 = HotelService._score_hotel(expensive,  1000)
        assert s1.budget_match > s2.budget_match

    def test_higher_rating_scores_higher(self):
        low  = make_hotel(2000, 2.0)
        high = make_hotel(2000, 5.0)
        s1 = HotelService._score_hotel(low,  2000)
        s2 = HotelService._score_hotel(high, 2000)
        assert s2.rating > s1.rating

    def test_more_amenities_scores_higher(self):
        few  = make_hotel(2000, 4.0, amenities='["WiFi"]')
        many = make_hotel(2000, 4.0, amenities='["WiFi","Pool","Spa","Gym","Restaurant","AC"]')
        s1 = HotelService._score_hotel(few,  2000)
        s2 = HotelService._score_hotel(many, 2000)
        assert s2.amenities >= s1.amenities

    def test_score_components_sum_to_total(self):
        hotel = make_hotel(2000, 4.0)
        s = HotelService._score_hotel(hotel, 2000)
        computed = round(s.budget_match + s.rating + s.amenities + s.distance, 2)
        assert abs(computed - s.total) < 0.1

    def test_no_amenities_still_scores(self):
        hotel = make_hotel(2000, 3.5, amenities="[]")
        score = HotelService._score_hotel(hotel, 2000)
        assert score.amenities >= 0
        assert score.total > 0

    def test_zero_budget_does_not_crash(self):
        hotel = make_hotel(2000, 4.0)
        score = HotelService._score_hotel(hotel, 0)
        assert 0 <= score.total <= 100

    def test_luxury_category_has_distance_score(self):
        hotel = make_hotel(5000, 4.8, "luxury")
        score = HotelService._score_hotel(hotel, 5000)
        assert score.distance > 0

    def test_budget_category_lower_distance_than_premium(self):
        budget  = make_hotel(500, 3.5, "budget")
        premium = make_hotel(500, 3.5, "premium")
        sb = HotelService._score_hotel(budget,  500)
        sp = HotelService._score_hotel(premium, 500)
        assert sp.distance > sb.distance
