"""
Unit tests for PackageService recommendation scoring engine.
Run with: pytest tests/test_package_service.py -v
"""
import pytest
from app.services.package_service import PackageService
from app.models.package import TravelPackage


def make_pkg(price, rating, days, inclusions=None) -> TravelPackage:
    import json
    p = TravelPackage()
    p.price        = price
    p.rating       = rating
    p.duration_days = days
    p.inclusions   = json.dumps(inclusions or ["WiFi", "Meals", "Hotel", "Transport"])
    p.exclusions   = "[]"
    return p


class TestPackageScoring:

    def test_score_within_0_to_100(self):
        pkg = make_pkg(12000, 4.2, 5)
        s = PackageService._score_package(pkg, 15000, 5)
        assert 0 <= s.total <= 100

    def test_within_budget_scores_high(self):
        pkg = make_pkg(10000, 4.5, 5)
        s = PackageService._score_package(pkg, 12000, 5)
        assert s.budget_match >= 35   # 40% weight * ~90% raw = ~36

    def test_over_budget_scores_lower(self):
        affordable = make_pkg(10000, 4.0, 5)
        expensive  = make_pkg(25000, 4.0, 5)
        s1 = PackageService._score_package(affordable, 12000, 5)
        s2 = PackageService._score_package(expensive,  12000, 5)
        assert s1.budget_match > s2.budget_match

    def test_higher_rating_scores_more(self):
        low  = make_pkg(10000, 2.0, 5)
        high = make_pkg(10000, 5.0, 5)
        s1 = PackageService._score_package(low,  10000, 5)
        s2 = PackageService._score_package(high, 10000, 5)
        assert s2.rating > s1.rating

    def test_exact_duration_match_full_score(self):
        pkg = make_pkg(10000, 4.0, 5)
        s = PackageService._score_package(pkg, 10000, 5)
        assert s.duration_match == pytest.approx(20.0, abs=0.1)

    def test_duration_mismatch_reduces_score(self):
        exact   = make_pkg(10000, 4.0, 5)
        mismatch = make_pkg(10000, 4.0, 10)
        s1 = PackageService._score_package(exact,    10000, 5)
        s2 = PackageService._score_package(mismatch, 10000, 5)
        assert s1.duration_match > s2.duration_match

    def test_more_inclusions_higher_popularity(self):
        import json
        few  = make_pkg(10000, 4.0, 5, inclusions=["WiFi"])
        many = make_pkg(10000, 4.0, 5, inclusions=["WiFi","Meals","Hotel","Flights","Spa","Gym","Pool","Tours"])
        s1 = PackageService._score_package(few,  10000, 5)
        s2 = PackageService._score_package(many, 10000, 5)
        assert s2.popularity > s1.popularity

    def test_components_sum_to_total(self):
        pkg = make_pkg(10000, 4.0, 5)
        s = PackageService._score_package(pkg, 10000, 5)
        computed = round(s.budget_match + s.rating + s.duration_match + s.popularity, 2)
        assert abs(computed - s.total) < 0.1

    def test_zero_budget_no_crash(self):
        pkg = make_pkg(10000, 4.0, 5)
        s = PackageService._score_package(pkg, 0, 5)
        assert 0 <= s.total <= 100

    def test_zero_days_no_crash(self):
        pkg = make_pkg(10000, 4.0, 5)
        s = PackageService._score_package(pkg, 10000, 0)
        assert 0 <= s.total <= 100
