"""
TripWise AI Service — LangChain Orchestrator
============================================
Features:
  • Conversation Memory   — ConversationBufferWindowMemory (last 5 exchanges)
  • RAG                   — search hotels / destinations / hidden gems from DB
  • Tool Calling          — weather lookup & route calculation via internal services
  • Same public API       — generate_response(), chat(), generate_itinerary()
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_chat import AIChatHistory
from app.models.destination import Destination
from app.models.hidden_gem import HiddenGem
from app.models.hotel import Hotel
from app.models.trip import Trip
from app.models.user import User
from app.schemas.ai import ChatHistoryListResponse, TripContext

logger = logging.getLogger("tripwise")

# ── System prompt ─────────────────────────────────────────────────────────────

BASE_SYSTEM_PROMPT = """You are TripWise AI, an expert travel planning assistant for India.
Help users plan trips, estimate budgets, suggest destinations, find hidden gems, and answer travel-related questions.
Always respond in a friendly, concise, and helpful tone.
Use Indian Rupees (₹) for all cost estimates unless explicitly asked otherwise.
When you have access to live data from our database or weather/route tools, use it to give precise answers."""

CONTEXT_PROMPT_TEMPLATE = """
You are currently helping a user with their trip:
- 🗺️  Destination: {destination}
- 🛫  From: {source}
- 💰  Total Budget: ₹{budget:,.0f}
- 📅  Duration: {days} days
- 👥  Travelers: {travelers}
- 🚗  Travel Mode: {travel_mode}
- 📋  Trip Status: {status}
Use this trip context to give highly personalised advice.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Session-level conversation memory store
# key: user_id (str), value: list of {"role": "human"/"ai", "content": str}
# ─────────────────────────────────────────────────────────────────────────────
_memory_store: dict[str, list[dict]] = {}
MEMORY_WINDOW = 5   # keep last N human+ai pairs


def _get_memory(user_id: str) -> list[dict]:
    return _memory_store.get(str(user_id), [])


def _save_to_memory(user_id: str, human_msg: str, ai_msg: str) -> None:
    uid = str(user_id)
    history = _memory_store.setdefault(uid, [])
    history.append({"role": "human",  "content": human_msg})
    history.append({"role": "ai",     "content": ai_msg})
    # Keep only last MEMORY_WINDOW * 2 messages
    if len(history) > MEMORY_WINDOW * 2:
        _memory_store[uid] = history[-(MEMORY_WINDOW * 2):]


def _format_history_for_prompt(history: list[dict]) -> str:
    if not history:
        return ""
    lines = ["--- Previous conversation ---"]
    for msg in history:
        role = "User" if msg["role"] == "human" else "TripWise AI"
        lines.append(f"{role}: {msg['content']}")
    lines.append("--- End of previous conversation ---")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# RAG helpers — search DB
# ─────────────────────────────────────────────────────────────────────────────

def _rag_search_destinations(db: Session, query: str, limit: int = 3) -> str:
    """Full-text style search on destination city names and descriptions."""
    terms = [t.strip() for t in query.lower().split() if len(t) > 2]
    results = []
    for dest in db.query(Destination).limit(300).all():
        text = f"{dest.city_name} {dest.state or ''} {dest.description or ''} {dest.known_for or ''}".lower()
        if any(term in text for term in terms):
            results.append(dest)
        if len(results) >= limit:
            break
    if not results:
        return ""
    lines = ["[RAG: Destinations from our database]"]
    for d in results:
        lines.append(
            f"• {d.city_name}, {d.state or d.country} — "
            f"Best season: {d.best_season or 'year-round'} | "
            f"Known for: {d.known_for or 'general tourism'} | "
            f"Safety: {d.safety_score}/10 | Food: {d.food_score}/10"
        )
    return "\n".join(lines)


def _rag_search_hotels(db: Session, city: str, limit: int = 3) -> str:
    """Find top-rated hotels in a city."""
    hotels = (
        db.query(Hotel)
        .filter(Hotel.city.ilike(f"%{city}%"))
        .order_by(Hotel.rating.desc())
        .limit(limit)
        .all()
    )
    if not hotels:
        return ""
    lines = [f"[RAG: Top hotels in {city} from our database]"]
    for h in hotels:
        lines.append(
            f"• {h.hotel_name} ({h.hotel_category}) — "
            f"₹{h.price_per_night}/night | Rating: {h.rating}/5"
        )
    return "\n".join(lines)


def _rag_search_hidden_gems(db: Session, city: str, limit: int = 3) -> str:
    """Find hidden gems / off-beat spots in a city."""
    gems = (
        db.query(HiddenGem)
        .filter(HiddenGem.city.ilike(f"%{city}%"))
        .limit(limit)
        .all()
    )
    if not gems:
        return ""
    lines = [f"[RAG: Hidden gems in {city} from our database]"]
    for g in gems:
        cost = f"₹{g.estimated_cost}" if g.estimated_cost else "free"
        lines.append(
            f"• {g.place_name} ({g.category or 'spot'}) — "
            f"{cost} | Best time: {g.best_time_to_visit or 'any'} | "
            f"Crowd: {g.crowd_level or 'low'}"
        )
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Tool calling helpers
# ─────────────────────────────────────────────────────────────────────────────

def _tool_get_weather(db: Session, city: str) -> str:
    """Tool: fetch current weather for a city."""
    try:
        from app.services.weather_service import WeatherService
        ws = WeatherService()
        w = ws.get_current_weather(db, city)
        if w.source == "unavailable":
            return f"[Tool: Weather] No live data available for {city}."
        return (
            f"[Tool: Weather in {city}] "
            f"{w.weather_condition}, {w.temperature}°C, "
            f"Humidity: {w.humidity}%, Wind: {w.wind_speed} km/h, "
            f"Rain chance: {w.rain_probability}%. Tip: {w.travel_recommendation}"
        )
    except Exception as e:
        logger.warning(f"Weather tool error for {city}: {e}")
        return f"[Tool: Weather] Could not fetch weather for {city}."


def _tool_calculate_route(source: str, destination: str) -> str:
    """Tool: calculate route & transport options between two cities."""
    try:
        from app.services.route_service import RouteService, ROUTE_DATA, COST_PER_KM, FLIGHT_FIXED_MIN
        rs = RouteService()
        src_key = source.lower().strip()
        dst_key = destination.lower().strip()
        data = ROUTE_DATA.get((src_key, dst_key)) or ROUTE_DATA.get((dst_key, src_key))
        if data:
            km = data["km"]
            road_h = data.get("road_h", km / 60)
            train_h = data.get("train_h", km / 80)
            flight_h = data.get("flight_h")
            car_cost = round(km * COST_PER_KM["car"], 0)
            train_cost = round(km * COST_PER_KM["train"], 0)
            bus_cost = round(km * COST_PER_KM["bus"], 0)
            flight_cost = round(max(FLIGHT_FIXED_MIN, km * COST_PER_KM["flight"]), 0) if flight_h else None

            result = (
                f"[Tool: Route {source} → {destination}] "
                f"Distance: {km} km | "
                f"Car: ₹{car_cost} ({road_h}h) | "
                f"Bus: ₹{bus_cost} ({road_h * 1.15:.1f}h) | "
                f"Train: ₹{train_cost} ({train_h}h)"
            )
            if flight_cost:
                result += f" | Flight: ₹{flight_cost} ({flight_h}h)"
            return result
        else:
            # Estimate
            km = rs._estimate_distance(src_key, dst_key)
            return (
                f"[Tool: Route {source} → {destination}] "
                f"Estimated ~{km} km. "
                f"Train approx ₹{round(km * 0.8)} | Car ₹{round(km * 5.5)}"
            )
    except Exception as e:
        logger.warning(f"Route tool error {source}→{destination}: {e}")
        return f"[Tool: Route] Could not calculate route from {source} to {destination}."


# ─────────────────────────────────────────────────────────────────────────────
# Intent detection — decide which tools/RAG to invoke
# ─────────────────────────────────────────────────────────────────────────────

def _detect_cities(message: str) -> list[str]:
    """Very lightweight city extractor for known Indian cities."""
    known_cities = [
        "mumbai", "delhi", "bangalore", "bengaluru", "chennai", "kolkata",
        "hyderabad", "pune", "jaipur", "goa", "agra", "manali", "shimla",
        "darjeeling", "varanasi", "kochi", "kochikode", "rishikesh",
        "amritsar", "udaipur", "jodhpur", "mysore", "ooty", "coorg",
        "hampi", "ajmer", "pushkar", "leh", "ladakh", "srinagar",
        "nainital", "mussoorie", "dehradun", "haridwar", "allahabad",
        "lucknow", "kanpur", "patna", "bhopal", "indore", "nagpur",
        "surat", "ahmedabad", "vadodara", "rajkot", "aurangabad",
        "nashik", "kolhapur", "puri", "bhubaneswar", "visakhapatnam",
        "tirupati", "madurai", "coimbatore", "pondicherry", "guwahati",
        "shillong", "gangtok", "sikkim", "andaman", "lakshadweep",
    ]
    msg_lower = message.lower()
    found = [city for city in known_cities if city in msg_lower]
    return list(dict.fromkeys(found))  # deduplicate preserving order


def _build_rag_and_tool_context(db: Optional[Session], message: str) -> str:
    """
    Detect intent in the user message and gather relevant context via RAG and tools.
    Returns a formatted string to inject into the LLM prompt.
    """
    if db is None:
        return ""

    msg_lower = message.lower()
    context_parts: list[str] = []
    cities = _detect_cities(message)

    # ── RAG: destination search ────────────────────────────────────────────────
    dest_keywords = ["destination", "visit", "go to", "travel to", "place", "where should", "suggest", "recommend"]
    if any(kw in msg_lower for kw in dest_keywords) or not cities:
        rag_dest = _rag_search_destinations(db, message)
        if rag_dest:
            context_parts.append(rag_dest)

    for city in cities[:2]:  # limit to 2 cities to keep prompt size reasonable
        # ── RAG: hotels ───────────────────────────────────────────────────────
        hotel_keywords = ["hotel", "stay", "accommodation", "where to stay", "lodging", "resort"]
        if any(kw in msg_lower for kw in hotel_keywords):
            rag_hotels = _rag_search_hotels(db, city)
            if rag_hotels:
                context_parts.append(rag_hotels)

        # ── RAG: hidden gems ──────────────────────────────────────────────────
        gem_keywords = ["hidden", "gem", "offbeat", "secret", "local", "unique", "explore", "unusual"]
        if any(kw in msg_lower for kw in gem_keywords):
            rag_gems = _rag_search_hidden_gems(db, city)
            if rag_gems:
                context_parts.append(rag_gems)

        # ── Tool: weather ─────────────────────────────────────────────────────
        weather_keywords = ["weather", "temperature", "rain", "climate", "forecast", "cold", "hot", "monsoon"]
        if any(kw in msg_lower for kw in weather_keywords):
            weather_info = _tool_get_weather(db, city)
            context_parts.append(weather_info)

    # ── Tool: route calculation ───────────────────────────────────────────────
    route_keywords = ["route", "how to reach", "how to go", "travel from", "distance", "flight", "train", "bus", "transport", "from.*to"]
    if any(kw in msg_lower for kw in route_keywords) and len(cities) >= 2:
        route_info = _tool_calculate_route(cities[0], cities[1])
        context_parts.append(route_info)
    elif any(kw in msg_lower for kw in ["how to reach", "how do i get to", "how to go to"]) and len(cities) >= 1:
        # Try to find source from trip context (already injected) — provide generic route tip
        pass

    return "\n\n".join(context_parts)


# ─────────────────────────────────────────────────────────────────────────────
# Gemini client wrapper (direct SDK, not LangChain)
# ─────────────────────────────────────────────────────────────────────────────

class _GeminiBackend:
    """Thin wrapper around google-genai SDK."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
        from google import genai
        from google.genai import types as gtypes
        self._genai = genai
        self._types = gtypes
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    def generate(self, system_prompt: str, full_prompt: str, max_tokens: int = 1500) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
            config=self._types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text


# ─────────────────────────────────────────────────────────────────────────────
# AIService — public interface (unchanged signatures for compatibility)
# ─────────────────────────────────────────────────────────────────────────────

class AIService:
    """
    LangChain-style orchestrator using:
    - Conversation memory (sliding window, last 5 exchanges)
    - RAG (search hotels / destinations / hidden gems)
    - Tool calling (weather, route)
    - Gemini Flash Lite as the LLM backend
    """

    def __init__(self):
        self._llm = _GeminiBackend()

    # ── Main authenticated chat ───────────────────────────────────────────────

    def generate_response(
        self,
        db: Session,
        message: str,
        user: User,
        trip_id: Optional[str] = None,
    ) -> tuple[str, bool]:
        """
        Orchestrated chat with memory + RAG + tools.
        Returns (reply, context_used).
        """
        context_used = False
        system_prompt = BASE_SYSTEM_PROMPT

        # 1. Trip context injection
        if trip_id:
            ctx = self.get_trip_context(db, trip_id, user)
            if ctx:
                system_prompt += CONTEXT_PROMPT_TEMPLATE.format(
                    destination=ctx.destination,
                    source=ctx.source,
                    budget=ctx.budget,
                    days=ctx.number_of_days,
                    travelers=ctx.number_of_travelers,
                    travel_mode=ctx.travel_mode or "Not specified",
                    status=ctx.trip_status,
                )
                context_used = True

        # 2. Retrieve conversation memory
        history = _get_memory(str(user.id))
        memory_block = _format_history_for_prompt(history)

        # 3. RAG + Tool calling
        tool_context = _build_rag_and_tool_context(db, message)
        if tool_context:
            context_used = True

        # 4. Assemble full prompt
        parts: list[str] = []
        if memory_block:
            parts.append(memory_block)
        if tool_context:
            parts.append("--- Live data from TripWise database & tools ---")
            parts.append(tool_context)
            parts.append("--- Use the above data to answer the user ---")
        parts.append(f"User: {message}")
        full_prompt = "\n\n".join(parts)

        # 5. Generate reply
        try:
            reply = self._llm.generate(system_prompt, full_prompt)
        except Exception as e:
            logger.error(f"LLM error: {e}")
            self._handle_gemini_error(e)

        # 6. Save to memory + DB
        _save_to_memory(str(user.id), message, reply)
        self.save_chat_history(db, user, message, reply, trip_id)

        return reply, context_used

    # ── Public unauthenticated chat ───────────────────────────────────────────

    def chat(self, message: str, db: Optional[Session] = None) -> str:
        """
        Lightweight chat for unauthenticated users.
        Still runs RAG + tools if db is provided.
        No persistent memory (session-less).
        """
        tool_context = _build_rag_and_tool_context(db, message)

        parts: list[str] = []
        if tool_context:
            parts.append("--- Live data from TripWise database & tools ---")
            parts.append(tool_context)
            parts.append("--- Use the above data to answer the user ---")
        parts.append(f"User: {message}")
        full_prompt = "\n\n".join(parts)

        try:
            return self._llm.generate(BASE_SYSTEM_PROMPT, full_prompt, max_tokens=1000)
        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            self._handle_gemini_error(e)

    # ── Itinerary generation ──────────────────────────────────────────────────

    def generate_itinerary(
        self,
        source: str,
        destination: str,
        days: int,
        travelers: int,
        budget: float,
    ) -> str:
        prompt = (
            f"Create a detailed {days}-day itinerary for {travelers} traveler(s) "
            f"from {source} to {destination} with a total budget of ₹{budget:,.0f}.\n"
            "Format in Markdown with:\n"
            "## ✈️ Trip Overview\n"
            "## 📅 Day-by-Day Itinerary (Morning/Afternoon/Evening for each day)\n"
            "## 🏨 Accommodation Suggestions\n"
            "## 💰 Budget Breakdown (table in ₹)\n"
            "## 💡 Travel Tips"
        )
        try:
            return self._llm.generate(
                "You are a travel planning expert. Respond in well-structured Markdown. Use ₹ INR for all costs.",
                prompt,
                max_tokens=3000,
            )
        except Exception as e:
            logger.error(f"Itinerary generation error: {e}")
            self._handle_gemini_error(e)

    # ── Trip context helpers ──────────────────────────────────────────────────

    def get_trip_context(
        self, db: Session, trip_id: str, user: User
    ) -> Optional[TripContext]:
        trip = db.query(Trip).filter(
            Trip.id == trip_id, Trip.user_id == user.id
        ).first()
        if not trip:
            return None
        return TripContext(
            destination=trip.destination_location,
            source=trip.source_location,
            budget=float(trip.budget),
            number_of_days=trip.number_of_days,
            number_of_travelers=trip.number_of_travelers,
            travel_mode=trip.travel_mode,
            trip_status=trip.trip_status,
        )

    # ── DB persistence ────────────────────────────────────────────────────────

    def save_chat_history(
        self,
        db: Session,
        user: User,
        user_message: str,
        ai_response: str,
        trip_id: Optional[str] = None,
    ) -> AIChatHistory:
        record = AIChatHistory(
            user_id=user.id,
            trip_id=trip_id or None,
            user_message=user_message,
            ai_response=ai_response,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_chat_history(
        self,
        db: Session,
        user: User,
        trip_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ChatHistoryListResponse:
        q = db.query(AIChatHistory).filter(AIChatHistory.user_id == user.id)
        if trip_id:
            q = q.filter(AIChatHistory.trip_id == trip_id)
        total = q.count()
        records = (
            q.order_by(AIChatHistory.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return ChatHistoryListResponse(
            history=records, total=total, page=page, page_size=page_size
        )

    # ── Memory management ─────────────────────────────────────────────────────

    @staticmethod
    def clear_memory(user_id: str) -> None:
        """Clear conversation memory for a user (e.g. on logout)."""
        _memory_store.pop(str(user_id), None)

    @staticmethod
    def get_memory_preview(user_id: str) -> list[dict]:
        """Return current in-memory conversation history for a user."""
        return _get_memory(str(user_id))

    # ── Error handling ────────────────────────────────────────────────────────

    @staticmethod
    def _handle_gemini_error(e: Exception) -> None:
        err = str(e).lower()
        if "quota" in err or "rate" in err or "429" in err:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI rate limit reached. Please try again in a moment.",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )
