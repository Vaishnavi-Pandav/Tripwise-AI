"""
Unit tests for AIService (no real Gemini calls — fully mocked).
Run with: pytest tests/test_ai_service.py -v
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from app.services.ai_service import AIService, BASE_SYSTEM_PROMPT, CONTEXT_PROMPT_TEMPLATE
from app.schemas.ai import TripContext
from fastapi import HTTPException


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr("app.services.ai_service.settings.GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr("app.services.ai_service.settings.GEMINI_MODEL",   "gemini-1.5-flash")


@pytest.fixture
def ai_service(mock_settings):
    with patch("app.services.ai_service.genai.Client"):
        svc = AIService()
        svc.client = MagicMock()
        return svc


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    u = MagicMock()
    u.id = "user-uuid-1"
    return u


# ── Schema validation ──────────────────────────────────────────────────────────

class TestChatRequestSchema:
    def test_valid_message(self):
        from app.schemas.ai import ChatRequest
        req = ChatRequest(message="Suggest Goa trip")
        assert req.message == "Suggest Goa trip"

    def test_empty_message_raises(self):
        from app.schemas.ai import ChatRequest
        with pytest.raises(Exception):
            ChatRequest(message="   ")

    def test_trip_id_optional(self):
        from app.schemas.ai import ChatRequest
        req = ChatRequest(message="Hello", trip_id=None)
        assert req.trip_id is None

    def test_message_stripped(self):
        from app.schemas.ai import ChatRequest
        req = ChatRequest(message="  Hello  ")
        assert req.message == "Hello"


# ── Trip context ───────────────────────────────────────────────────────────────

class TestTripContext:
    def test_get_trip_context_not_found(self, ai_service, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = ai_service.get_trip_context(mock_db, "bad-uuid", mock_user)
        assert result is None

    def test_get_trip_context_found(self, ai_service, mock_db, mock_user):
        trip = MagicMock()
        trip.destination_location = "Goa"
        trip.source_location      = "Mumbai"
        trip.budget               = 15000
        trip.number_of_days       = 4
        trip.number_of_travelers  = 2
        trip.travel_mode          = "flight"
        trip.trip_status          = "planned"
        mock_db.query.return_value.filter.return_value.first.return_value = trip

        ctx = ai_service.get_trip_context(mock_db, "trip-uuid", mock_user)
        assert ctx is not None
        assert ctx.destination == "Goa"
        assert ctx.budget == 15000
        assert ctx.number_of_days == 4


# ── Chat history ───────────────────────────────────────────────────────────────

class TestChatHistory:
    def test_save_chat_history(self, ai_service, mock_db, mock_user):
        mock_db.add     = MagicMock()
        mock_db.commit  = MagicMock()
        mock_db.refresh = MagicMock()
        ai_service.save_chat_history(mock_db, mock_user, "Hi", "Hello!", None)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_get_chat_history_empty(self, ai_service, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.order_by.return_value \
            .offset.return_value.limit.return_value.all.return_value = []
        result = ai_service.get_chat_history(mock_db, mock_user)
        assert result.total == 0
        assert result.history == []


# ── Error handling ─────────────────────────────────────────────────────────────

class TestErrorHandling:
    def test_rate_limit_raises_429(self):
        with pytest.raises(HTTPException) as exc:
            AIService._handle_gemini_error(Exception("429 quota exceeded"))
        assert exc.value.status_code == 429

    def test_invalid_key_raises_503(self):
        with pytest.raises(HTTPException) as exc:
            AIService._handle_gemini_error(Exception("invalid api key"))
        assert exc.value.status_code == 503

    def test_generic_error_raises_502(self):
        with pytest.raises(HTTPException) as exc:
            AIService._handle_gemini_error(Exception("some random error"))
        assert exc.value.status_code == 502


# ── System prompt ──────────────────────────────────────────────────────────────

class TestPromptEngineering:
    def test_base_prompt_contains_capabilities(self):
        assert "destination" in BASE_SYSTEM_PROMPT.lower()
        assert "budget" in BASE_SYSTEM_PROMPT.lower()
        assert "hotel" in BASE_SYSTEM_PROMPT.lower()

    def test_context_template_has_all_fields(self):
        rendered = CONTEXT_PROMPT_TEMPLATE.format(
            destination="Goa", source="Mumbai",
            budget=15000, days=4, travelers=2,
            travel_mode="flight", status="planned",
        )
        assert "Goa" in rendered
        assert "₹15,000" in rendered
        assert "4 days" in rendered
