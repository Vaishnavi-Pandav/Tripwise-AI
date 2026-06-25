"""
Tests for remaining modules: favorites, notifications, analytics,
search, optimizer, settings, export.
Run with: pytest tests/test_remaining_modules.py -v
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.favorite_service import FavoriteService
from app.services.notification_service import NotificationService
from app.services.analytics_service import AnalyticsService
from app.services.optimizer_service import OptimizerService
from app.services.search_service import SearchService
from app.services.settings_service import SettingsService
from app.models.trip import TripStatus


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_user():
    u = MagicMock(); u.id = "user-uuid"; return u

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.delete = MagicMock()
    return db


# ── Favorites ──────────────────────────────────────────────────────────────────

class TestFavoriteService:
    def test_add_favorite(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = FavoriteService.add(mock_db, mock_user, "hotel", "hotel-uuid")
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_add_duplicate_raises_409(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
        with pytest.raises(HTTPException) as exc:
            FavoriteService.add(mock_db, mock_user, "hotel", "hotel-uuid")
        assert exc.value.status_code == 409

    def test_remove_not_found_raises_404(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc:
            FavoriteService.remove(mock_db, mock_user, "bad-uuid")
        assert exc.value.status_code == 404

    def test_remove_success(self, mock_db, mock_user):
        fav = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = fav
        FavoriteService.remove(mock_db, mock_user, "fav-uuid")
        mock_db.delete.assert_called_once_with(fav)

    def test_get_all_returns_list(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        result = FavoriteService.get_all(mock_db, mock_user)
        assert isinstance(result, list)


# ── Notifications ──────────────────────────────────────────────────────────────

class TestNotificationService:
    def test_get_all_returns_response(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        result = NotificationService.get_all(mock_db, mock_user)
        assert result.total == 0
        assert result.unread == 0

    def test_mark_read_not_found_raises_404(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc:
            NotificationService.mark_read(mock_db, mock_user, "bad-uuid")
        assert exc.value.status_code == 404

    def test_mark_read_sets_is_read(self, mock_db, mock_user):
        notif = MagicMock(); notif.is_read = False
        mock_db.query.return_value.filter.return_value.first.return_value = notif
        NotificationService.mark_read(mock_db, mock_user, "notif-uuid")
        assert notif.is_read == True

    def test_create_notification(self, mock_db, mock_user):
        NotificationService.create_notification(mock_db, str(mock_user.id), "Test", "Message", "trip_reminder")
        mock_db.add.assert_called_once()


# ── Analytics ──────────────────────────────────────────────────────────────────

class TestAnalyticsService:
    def test_dashboard_empty_trips(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = []
        result = AnalyticsService.get_dashboard(mock_db, mock_user)
        assert result.total_trips == 0
        assert result.total_budget_spent == 0.0
        assert isinstance(result.top_destinations, list)

    def test_dashboard_counts_trips_correctly(self, mock_db, mock_user):
        trips = [
            MagicMock(trip_status=TripStatus.COMPLETED, destination_location="Goa", number_of_days=4, travel_mode="flight"),
            MagicMock(trip_status=TripStatus.PLANNED,   destination_location="Manali", number_of_days=5, travel_mode="train"),
            MagicMock(trip_status=TripStatus.COMPLETED, destination_location="Goa", number_of_days=3, travel_mode="flight"),
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = trips
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = []
        result = AnalyticsService.get_dashboard(mock_db, mock_user)
        assert result.total_trips == 3
        assert result.completed_trips == 2
        assert result.planned_trips == 1
        assert result.favorite_destination == "Goa"


# ── Search ─────────────────────────────────────────────────────────────────────

class TestSearchService:
    def test_returns_search_response(self, mock_db):
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        result = SearchService.search(mock_db, "goa")
        assert result.query == "goa"
        assert isinstance(result.results, list)
        assert result.total == 0

    def test_pagination(self, mock_db):
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        result = SearchService.search(mock_db, "test", page=2, page_size=10)
        assert result.page == 2
        assert result.page_size == 10


# ── Optimizer ─────────────────────────────────────────────────────────────────

class TestOptimizerService:
    def test_trip_not_found_raises_404(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc:
            OptimizerService.optimize(mock_db, "bad-trip", mock_user)
        assert exc.value.status_code == 404

    def test_flight_generates_savings(self, mock_db, mock_user):
        trip = MagicMock()
        trip.id = "trip-1"
        trip.destination_location = "Goa"
        trip.travel_mode = "flight"
        trip.total_estimated_cost = 25000
        trip.budget = 25000
        trip.user_id = mock_user.id
        mock_db.query.return_value.filter.return_value.first.side_effect = [trip, None]
        result = OptimizerService.optimize(mock_db, "trip-1", mock_user)
        assert result.savings > 0
        assert result.optimized_cost < result.current_cost
        assert len(result.recommendations) > 0

    def test_response_has_all_fields(self, mock_db, mock_user):
        trip = MagicMock()
        trip.destination_location = "Goa"
        trip.travel_mode = "train"
        trip.total_estimated_cost = 15000
        trip.budget = 15000
        trip.user_id = mock_user.id
        mock_db.query.return_value.filter.return_value.first.side_effect = [trip, None]
        result = OptimizerService.optimize(mock_db, "trip-1", mock_user)
        assert result.trip_id is not None
        assert isinstance(result.recommendations, list)
        assert isinstance(result.suggestions, list)


# ── Settings ──────────────────────────────────────────────────────────────────

class TestSettingsService:
    def test_get_settings_no_prefs(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = SettingsService.get_settings(mock_db, mock_user)
        assert result.preferred_budget is None
        assert result.travel_styles == []

    def test_update_settings_creates_prefs(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        from app.schemas.settings import UserSettingsUpdate
        payload = UserSettingsUpdate(preferred_budget="mid-range", travel_styles=["adventure"])
        # Should not raise
        mock_db.refresh.return_value = None
        SettingsService.update_settings(mock_db, mock_user, payload)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
