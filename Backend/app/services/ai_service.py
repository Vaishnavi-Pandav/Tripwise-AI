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

BASE_SYSTEM_PROMPT = """You are TripWise AI, an expert travel planning assistant.
Help users plan trips, estimate budgets, suggest destinations, find hidden gems, and answer all travel-related questions.
Always respond in a friendly, concise, and helpful tone. Use Indian Rupees (₹) for cost estimates unless asked otherwise."""

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

    def generate_response(self, db: Session, message: str, user: User, trip_id: Optional[str] = None) -> tuple[str, bool]:
        context_used = False
        system_prompt = BASE_SYSTEM_PROMPT
        if trip_id:
            ctx = self.get_trip_context(db, trip_id, user)
            if ctx:
                system_prompt += CONTEXT_PROMPT_TEMPLATE.format(
                    destination=ctx.destination, source=ctx.source, budget=ctx.budget,
                    days=ctx.number_of_days, travelers=ctx.number_of_travelers,
                    travel_mode=ctx.travel_mode or "Not specified", status=ctx.trip_status,
                )
                context_used = True
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=message,
                config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.7, max_output_tokens=1500),
            )
            reply = response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            self._handle_gemini_error(e)
        self.save_chat_history(db, user, message, reply, trip_id)
        return reply, context_used

    def get_trip_context(self, db: Session, trip_id: str, user: User) -> Optional[TripContext]:
        trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user.id).first()
        if not trip:
            return None
        return TripContext(destination=trip.destination_location, source=trip.source_location,
                           budget=float(trip.budget), number_of_days=trip.number_of_days,
                           number_of_travelers=trip.number_of_travelers,
                           travel_mode=trip.travel_mode, trip_status=trip.trip_status)

    def save_chat_history(self, db: Session, user: User, user_message: str, ai_response: str, trip_id: Optional[str] = None) -> AIChatHistory:
        record = AIChatHistory(user_id=user.id, trip_id=trip_id or None, user_message=user_message, ai_response=ai_response)
        db.add(record); db.commit(); db.refresh(record)
        return record

    def get_chat_history(self, db: Session, user: User, trip_id: Optional[str] = None, page: int = 1, page_size: int = 20) -> ChatHistoryListResponse:
        q = db.query(AIChatHistory).filter(AIChatHistory.user_id == user.id)
        if trip_id:
            q = q.filter(AIChatHistory.trip_id == trip_id)
        total = q.count()
        records = q.order_by(AIChatHistory.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
        return ChatHistoryListResponse(history=records, total=total, page=page, page_size=page_size)

    def generate_itinerary(self, source: str, destination: str, days: int, travelers: int, budget: float) -> str:
        prompt = f"""Create a detailed {days}-day itinerary for {travelers} traveler(s) from {source} to {destination} with a total budget of ₹{budget:,.0f}.
Format in Markdown with: ## ✈️ Trip Overview, ## 📅 Day-by-Day Itinerary (Morning/Afternoon/Evening), ## 🏨 Accommodation Suggestions, ## 💰 Budget Breakdown (table), ## 💡 Travel Tips"""
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a travel planning expert. Respond in well-structured Markdown.",
                    temperature=0.7, max_output_tokens=3000,
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini itinerary error: {e}")
            self._handle_gemini_error(e)

    def chat(self, message: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=message,
                config=types.GenerateContentConfig(system_instruction=BASE_SYSTEM_PROMPT, temperature=0.7, max_output_tokens=1000),
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            self._handle_gemini_error(e)

    @staticmethod
    def _handle_gemini_error(e: Exception) -> None:
        err = str(e).lower()
        if "quota" in err or "rate" in err or "429" in err:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="AI rate limit reached. Please try again in a moment.")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"AI service error: {str(e)}")
