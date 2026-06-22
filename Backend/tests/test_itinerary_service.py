"""
Unit tests for ItineraryService.
Run with: pytest tests/test_itinerary_service.py -v
"""
import json
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.services.itinerary_service import (
    ItineraryService,
    BUDGET_RULES,
    SYSTEM_ROLE,
    ITINERARY_PROMPT,
)
from app.schemas.itinerary import (
    ItineraryDayResponse,
    Activity,
    GenerateItineraryRequest,
)


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr("app.services.itinerary_service.settings.GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr("app.services.itinerary_service.settings.GEMINI_MODEL", "gemini-1.5-flash")


@pytest.fixture
def svc(mock_settings):
    with patch("app.services.itinerary_service.genai.Client"):
        service = ItineraryService()
        service.client = MagicMock()
        return service


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    u = MagicMock()
    u.id = "user-uuid-1"
    return u


@pytest.fixture
def mock_trip():
    t = MagicMock()
    t.id                    = "trip-uuid-1"
    t.user_id               = "user-uuid-1"
    t.destination_location  = "Goa"
    t.source_location       = "Mumbai"
    t.budget                = 15000
    t.number_of_days        = 3
    t.number_of_travelers   = 2
    t.travel_mode           = "flight"
    t.trip_status           = "planned"
    return t


@pytest.fixture
def sample_ai_json():
    return {
        "days": [
            {
                "day_number": 1,
                "title": "Arrival & Beaches",
                "activities": [
                    {"time": "Morning",   "name": "Calangute Beach", "description": "Popular beach",
                     "location": "Calangute", "cost": "Free", "tips": "Arrive early"},
                    {"time": "Afternoon", "name": "Baga Beach",      "description": "Lively beach",
                     "location": "Baga",      "cost": "Free", "tips": "Try water sports"},
                    {"time": "Evening",   "name": "Beach Shack",     "description": "Sunset dinner",
                     "location": "Baga",      "cost": "₹600", "tips": "Book ahead"},
                ],
                "estimated_cost": 1500,
                "notes": "Keep IDs ready for hotel check-in",
            },
            {
                "day_number": 2,
                "title": "North Goa Exploration",
                "activities": [
                    {"time": "Morning", "name": "Fort Aguada", "description": "17th-century fort",
                     "location": "Candolim", "cost": "₹50", "tips": "Good photo spot"},
                    {"time": "Afternoon", "name": "Anjuna Flea Market",
                     "description": "Local market", "location": "Anjuna",
                     "cost": "₹0 entry", "tips": "Bargain hard"},
                    {"time": "Evening", "name": "Tito's Street",
                     "description": "Nightlife", "location": "Baga", "cost": "₹500", "tips": ""},
                ],
                "estimated_cost": 2000,
                "notes": "Rent a scooter for ₹300/day",
            },
            {
                "day_number": 3,
                "title": "Departure Day",
                "activities": [
                    {"time": "Morning", "name": "Hotel Breakfast",
                     "description": "Leisurely morning", "location": "Hotel",
                     "cost": "Included", "tips": "Check out by 11AM"},
                ],
                "estimated_cost": 500,
                "notes": "Airport transfer ~₹800",
            },
        ]
    }


# ── Schema validation ──────────────────────────────────────────────────────────

class TestSchemas:
    def test_generate_request_valid(self):
        req = GenerateItineraryRequest(trip_id="trip-uuid-1")
        assert req.trip_id == "trip-uuid-1"

    def test_activity_schema(self):
        act = Activity(time="Morning", name="Beach", description="Nice beach")
        assert act.time == "Morning"

    def test_itinerary_day_parses_json_activities(self):
        activities = [{"time": "Morning", "name": "Beach", "description": "Test",
                       "location": None, "cost": None, "tips": None}]
        row = MagicMock()
        row.id             = "uuid-1"
        row.trip_id        = "trip-uuid"
        row.day_number     = 1
        row.title          = "Day 1"
        row.activities     = json.dumps(activities)
        row.estimated_cost = 1000
        row.notes          = "Test note"
        row.created_at     = __import__("datetime").datetime.utcnow()
        row.updated_at     = __import__("datetime").datetime.utcnow()

        result = ItineraryDayResponse.model_validate(row)
        assert len(result.activities) == 1
        assert result.activities[0].time == "Morning"

    def test_itinerary_day_handles_empty_activities(self):
        row = MagicMock()
        row.id             = "uuid-1"
        row.trip_id        = "trip-uuid"
        row.day_number     = 1
        row.title          = "Day 1"
        row.activities     = "[]"
        row.estimated_cost = 0
        row.notes          = ""
        row.created_at     = __import__("datetime").datetime.utcnow()
        row.updated_at     = __import__("datetime").datetime.utcnow()

        result = ItineraryDayResponse.model_validate(row)
        assert result.activities == []


# ── Budget rules ───────────────────────────────────────────────────────────────

class TestBudgetRules:
    def test_low_budget_rules_mention_free(self):
        assert "free" in BUDGET_RULES["low"].lower()

    def test_high_budget_rules_mention_premium(self):
        assert "premium" in BUDGET_RULES["high"].lower()

    def test_mid_budget_rules_exist(self):
        assert len(BUDGET_RULES["mid"]) > 10

    def test_all_budget_categories_present(self):
        assert set(BUDGET_RULES.keys()) == {"low", "mid", "high"}


# ── Context builders ───────────────────────────────────────────────────────────

class TestContextBuilders:
    def test_no_hotel_recs_returns_empty(self, mock_db):
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.limit.return_value.all.return_value = []
        result = ItineraryService._build_hotel_context(mock_db, "trip-uuid")
        assert result == ""

    def test_no_expense_returns_empty(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = ItineraryService._build_expense_context(mock_db, "trip-uuid")
        assert result == ""

    def test_expense_context_contains_costs(self, mock_db):
        expense = MagicMock()
        expense.transport_cost     = 4000
        expense.accommodation_cost = 4200
        expense.food_cost          = 2700
        expense.activity_cost      = 1650
        expense.miscellaneous_cost = 1050
        mock_db.query.return_value.filter.return_value.first.return_value = expense
        result = ItineraryService._build_expense_context(mock_db, "trip-uuid")
        assert "4,000" in result or "4000" in result
        assert "Transport" in result


# ── Save itinerary ─────────────────────────────────────────────────────────────

class TestSaveItinerary:
    def test_save_creates_correct_number_of_days(self, svc, mock_db, sample_ai_json):
        # Simulate no existing records
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add     = MagicMock()
        mock_db.flush   = MagicMock()
        mock_db.commit  = MagicMock()
        mock_db.refresh = MagicMock(side_effect=lambda x: None)

        # Mock refresh to populate fields
        def fake_refresh(obj):
            from datetime import datetime
            obj.id             = f"uuid-day-{obj.day_number}"
            obj.trip_id        = "trip-uuid"
            obj.created_at     = datetime.utcnow()
            obj.updated_at     = datetime.utcnow()

        mock_db.refresh.side_effect = fake_refresh
        records = svc.save_itinerary(mock_db, "trip-uuid", sample_ai_json, 15000)
        assert len(records) == 3

    def test_save_day_numbers_correct(self, svc, mock_db, sample_ai_json):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = MagicMock()
        mock_db.flush = MagicMock()
        mock_db.commit = MagicMock()

        from datetime import datetime
        def fake_refresh(obj):
            obj.id         = f"uuid-{obj.day_number}"
            obj.trip_id    = "trip-uuid"
            obj.created_at = datetime.utcnow()
            obj.updated_at = datetime.utcnow()

        mock_db.refresh.side_effect = fake_refresh
        records = svc.save_itinerary(mock_db, "trip-uuid", sample_ai_json, 15000)
        day_nums = [r.day_number for r in records]
        assert day_nums == [1, 2, 3]


# ── Trip ownership check ───────────────────────────────────────────────────────

class TestTripOwnership:
    def test_trip_not_found_raises_404(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc:
            ItineraryService._get_trip(mock_db, "bad-uuid", mock_user)
        assert exc.value.status_code == 404
