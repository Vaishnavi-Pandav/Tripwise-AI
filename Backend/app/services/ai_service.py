import logging
import math
from typing import Optional

from fastapi import HTTPException, status
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_chat import AIChatHistory
from app.models.trip import Trip
from app.models.user import User
from app.schemas.ai import ChatHistoryListResponse, TripContext

logger = logging.getLogger("tripwise")

# ── System prompt ──────────────────────────────────────────────────────────────

BASE_SYSTEM_PROMPT = """You are TripWise AI, an expert travel planning assistant.

Your capabilities:
- Suggest and compare travel destinations
- Plan day-wise itineraries
- Estimate budgets and costs
- Recommend hotels, restaurants, and attractions
- Advise on transportation options
- Share weather insights and best travel seasons
- Highlight hidden gems and local experiences
- Provide safety tips and cultural etiquette
- Answer questions about food, shopping, and nightlife

Rules:
- Always respond in a friendly, concise, and helpful tone
- Use Indian Rupees (₹) for cost estimates unless asked otherwise
- If a budget is tight, suggest cost-saving alternatives
- Format longer responses with clear sections and bullet points
- Never make up specific prices — use reasonable ranges
"""

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


class AIService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model  = settings.GEMINI_MODEL

    # ── Core generation ───────────────────────────────────────────────────────

    def generate_response(
        self,
        db: Session,
        message: str,
        user: User,
        trip_id: Optional[str] = None,
    ) -> tuple[str, bool]:
        """
        Generate an AI response, optionally enriched with trip context.
        Returns (reply_text, trip_context_used).
        """
        context_used = False
        system_prompt = BASE_SYSTEM_PROMPT

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

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=1500,
                ),
            )
            reply = response.text
        except Exception as e:
            logger.error(f"Gemini generate_response error: {e}")
            self._handle_gemini_error(e)

        # Save to chat history
        self.save_chat_history(db, user, message, reply, trip_id)
        return reply, context_used

    # ── Trip context ──────────────────────────────────────────────────────────

    def get_trip_context(
        self,
        db: Session,
        trip_id: str,
        user: User,
    ) -> Optional[TripContext]:
        """Fetch trip and return as TripContext. Returns None if not found."""
        trip = db.query(Trip).filter(
            Trip.id == trip_id,
            Trip.user_id == user.id,
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

    # ── Chat history ──────────────────────────────────────────────────────────

    def save_chat_history(
        self,
        db: Session,
        user: User,
        user_message: str,
        ai_response: str,
        trip_id: Optional[str] = None,
    ) -> AIChatHistory:
        """Persist a chat turn to the database."""
        record = AIChatHistory(
            user_id=user.id,
            trip_id=trip_id or None,
            user_message=user_message,
            ai_response=ai_response,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(f"Chat saved: user={user.id} trip={trip_id}")
        return record

    def get_chat_history(
        self,
        db: Session,
        user: User,
        trip_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ChatHistoryListResponse:
        """Return paginated chat history for a user, optionally filtered by trip."""
        q = db.query(AIChatHistory).filter(AIChatHistory.user_id == user.id)
        if trip_id:
            q = q.filter(AIChatHistory.trip_id == trip_id)

        total      = q.count()
        total_pages = max(1, math.ceil(total / page_size))
        records    = (
            q.order_by(AIChatHistory.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return ChatHistoryListResponse(
            history=records,
            total=total,
            page=page,
            page_size=page_size,
        )

    # ── Itinerary generation ──────────────────────────────────────────────────

    def generate_itinerary(
        self,
        source: str,
        destination: str,
        days: int,
        travelers: int,
        budget: float,
    ) -> str:
        """Generate a full markdown day-wise itinerary."""
        prompt = f"""
Create a detailed {days}-day itinerary for {travelers} traveler(s)
travelling from {source} to {destination} with a total budget of ₹{budget:,.0f}.

Format in **Markdown** with:

## ✈️ Trip Overview
- Source, destination, duration, number of travelers, total budget

## 📅 Day-by-Day Itinerary
For each day include **Morning**, **Afternoon**, and **Evening** activities
with restaurant suggestions and booking requirements.

## 🏨 Accommodation Suggestions
3 options (budget / mid-range / luxury) with estimated nightly cost.

## 💰 Budget Breakdown
| Category        | Estimated Cost (₹) |
|-----------------|-------------------|
| Transport       | ₹xxx              |
| Accommodation   | ₹xxx              |
| Food & Dining   | ₹xxx              |
| Activities      | ₹xxx              |
| Local Transport | ₹xxx              |
| Miscellaneous   | ₹xxx              |
| **Total**       | **₹xxx**          |

## 💡 Travel Tips
3–5 practical tips for this destination.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a travel planning expert. Respond in well-structured Markdown.",
                    temperature=0.7,
                    max_output_tokens=3000,
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini itinerary error: {e}")
            self._handle_gemini_error(e)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _handle_gemini_error(e: Exception) -> None:
        """Convert Gemini errors to appropriate HTTP exceptions."""
        err = str(e).lower()
        if "quota" in err or "rate" in err or "429" in err:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI service rate limit reached. Please try again in a moment.",
            )
        if "invalid" in err and "key" in err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service configuration error. Contact support.",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )

    # ── Legacy alias ─────────────────────────────────────────────────────────

    def chat(self, message: str) -> str:
        """Simple chat without DB persistence (used by public /ai/generate)."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=BASE_SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=1000,
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            self._handle_gemini_error(e)
