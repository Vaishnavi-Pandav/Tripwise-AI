import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.expenses import TripExpenses
from app.models.hotel import Hotel
from app.models.hotel_recommendation import HotelRecommendation
from app.models.itinerary import Itinerary
from app.models.trip import Trip
from app.models.user import User
from app.schemas.itinerary import ItineraryDayResponse, ItineraryResponse

logger = logging.getLogger("tripwise")

# ── Prompt templates ───────────────────────────────────────────────────────────

SYSTEM_ROLE = (
    "You are a professional travel planner creating detailed, realistic, "
    "and budget-aware travel itineraries. Always respond with valid JSON only. "
    "Never include markdown code fences or extra text outside the JSON."
)

ITINERARY_PROMPT = """
Generate a complete {days}-day travel itinerary for the following trip:

TRIP DETAILS:
- Destination: {destination}
- Departing From: {source}
- Duration: {days} days
- Travelers: {travelers}
- Total Budget: ₹{budget:,.0f}
- Travel Mode: {travel_mode}
- Budget Category: {budget_category}
{hotel_context}
{expense_context}

BUDGET CATEGORY RULES:
{budget_rules}

Return ONLY this JSON structure (no markdown, no extra text):
{{
  "days": [
    {{
      "day_number": 1,
      "title": "Arrival & Beach Exploration",
      "activities": [
        {{
          "time": "Morning",
          "name": "Activity name",
          "description": "Short description",
          "location": "Place name",
          "cost": "₹200–₹400",
          "tips": "Practical tip"
        }},
        {{
          "time": "Afternoon",
          "name": "Activity name",
          "description": "Short description",
          "location": "Place name",
          "cost": "₹300",
          "tips": "Tip"
        }},
        {{
          "time": "Evening",
          "name": "Activity name",
          "description": "Short description",
          "location": "Place name",
          "cost": "₹150",
          "tips": "Tip"
        }}
      ],
      "estimated_cost": 1200,
      "notes": "Practical tip for the day"
    }}
  ]
}}
"""

BUDGET_RULES = {
    "low": (
        "- Recommend free or low-cost attractions\n"
        "- Suggest local street food over restaurants\n"
        "- Use public transport, avoid taxis\n"
        "- Stay in budget guesthouses or hostels\n"
        "- Avoid paid theme parks or luxury experiences"
    ),
    "mid": (
        "- Mix free attractions with paid experiences\n"
        "- Suggest mid-range restaurants (₹300–₹600 per meal)\n"
        "- Include one or two paid activities per day\n"
        "- Use a mix of public and private transport"
    ),
    "high": (
        "- Include premium experiences (spa, boat tours, fine dining)\n"
        "- Suggest luxury restaurants and rooftop bars\n"
        "- Recommend private transfers and exclusive activities\n"
        "- Include experiences unique to the destination"
    ),
}


class ItineraryService:

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model  = settings.GEMINI_MODEL

    # ── Generate ──────────────────────────────────────────────────────────────

    def generate_itinerary(
        self,
        db: Session,
        trip_id: str,
        user: User,
    ) -> ItineraryResponse:
        """
        Fetch full trip context, call Gemini, parse JSON response,
        persist day-by-day records, return ItineraryResponse.
        """
        trip = self._get_trip(db, trip_id, user)

        # Build context blocks
        budget_per_day  = float(trip.budget) / max(trip.number_of_days, 1)
        budget_category = (
            "low"  if budget_per_day < 1500 else
            "mid"  if budget_per_day < 4000 else
            "high"
        )

        hotel_ctx   = self._build_hotel_context(db, trip_id)
        expense_ctx = self._build_expense_context(db, trip_id)

        prompt = ITINERARY_PROMPT.format(
            destination=trip.destination_location,
            source=trip.source_location,
            days=trip.number_of_days,
            travelers=trip.number_of_travelers,
            budget=float(trip.budget),
            travel_mode=trip.travel_mode or "Not specified",
            budget_category=budget_category.upper(),
            hotel_context=hotel_ctx,
            expense_context=expense_ctx,
            budget_rules=BUDGET_RULES[budget_category],
        )

        raw_json = self._call_gemini(prompt)
        day_records = self.save_itinerary(db, trip_id, raw_json, float(trip.budget))

        total_cost = sum(
            float(r.estimated_cost or 0) for r in day_records
        )

        return ItineraryResponse(
            trip_id=str(trip.id),
            destination=trip.destination_location,
            total_days=trip.number_of_days,
            total_cost=round(total_cost, 2),
            days=day_records,
            generated_at=datetime.utcnow(),
        )

    # ── Save ──────────────────────────────────────────────────────────────────

    def save_itinerary(
        self,
        db: Session,
        trip_id: str,
        raw_json: dict,
        total_budget: float,
    ) -> list[ItineraryDayResponse]:
        """Parse AI JSON and upsert one Itinerary row per day."""
        days_data = raw_json.get("days", [])
        records: list[ItineraryDayResponse] = []

        for day_data in days_data:
            day_num        = int(day_data.get("day_number", 0))
            title          = day_data.get("title", f"Day {day_num}")
            activities     = day_data.get("activities", [])
            estimated_cost = day_data.get("estimated_cost")
            notes          = day_data.get("notes", "")

            existing = db.query(Itinerary).filter(
                Itinerary.trip_id  == trip_id,
                Itinerary.day_number == day_num,
            ).first()

            act_json = json.dumps(activities)

            if existing:
                existing.title          = title
                existing.activities     = act_json
                existing.estimated_cost = estimated_cost
                existing.notes          = notes
                db.flush()
                record = existing
            else:
                record = Itinerary(
                    trip_id=trip_id,
                    day_number=day_num,
                    title=title,
                    activities=act_json,
                    estimated_cost=estimated_cost,
                    notes=notes,
                )
                db.add(record)
                db.flush()

            db.refresh(record)
            records.append(ItineraryDayResponse.model_validate(record))

        db.commit()
        logger.info(f"Itinerary saved: trip={trip_id}, days={len(records)}")
        return records

    # ── Get ───────────────────────────────────────────────────────────────────

    def get_itinerary(
        self,
        db: Session,
        trip_id: str,
        user: User,
    ) -> ItineraryResponse:
        """Return saved itinerary for a trip."""
        self._get_trip(db, trip_id, user)   # ownership check
        records = (
            db.query(Itinerary)
            .filter(Itinerary.trip_id == trip_id)
            .order_by(Itinerary.day_number)
            .all()
        )
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No itinerary found. Call POST /itinerary/generate first.",
            )
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        total_cost = sum(float(r.estimated_cost or 0) for r in records)

        return ItineraryResponse(
            trip_id=trip_id,
            destination=trip.destination_location,
            total_days=trip.number_of_days,
            total_cost=round(total_cost, 2),
            days=[ItineraryDayResponse.model_validate(r) for r in records],
            generated_at=records[0].created_at,
        )

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete_itinerary(self, db: Session, trip_id: str, user: User) -> None:
        """Delete all itinerary records for a trip."""
        self._get_trip(db, trip_id, user)
        deleted = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).delete()
        db.commit()
        if deleted == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No itinerary found for this trip",
            )
        logger.info(f"Itinerary deleted: trip={trip_id}, rows={deleted}")

    # ── Gemini call ───────────────────────────────────────────────────────────

    def _call_gemini(self, prompt: str) -> dict:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_ROLE,
                    temperature=0.6,
                    max_output_tokens=4000,
                ),
            )
            text = response.text.strip()
            # Strip markdown code fences if model adds them
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned non-JSON: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI returned an invalid response. Please try again.",
            )
        except Exception as e:
            err = str(e).lower()
            logger.error(f"Gemini itinerary error: {e}")
            if "quota" in err or "429" in err:
                raise HTTPException(status_code=429,
                                    detail="AI rate limit. Try again shortly.")
            raise HTTPException(status_code=502,
                                detail=f"AI service error: {str(e)}")

    # ── Context builders ──────────────────────────────────────────────────────

    @staticmethod
    def _build_hotel_context(db: Session, trip_id: str) -> str:
        recs = (
            db.query(HotelRecommendation)
            .filter(HotelRecommendation.trip_id == trip_id)
            .order_by(HotelRecommendation.recommendation_score.desc())
            .limit(3)
            .all()
        )
        if not recs:
            return ""
        hotels = []
        for r in recs:
            h: Hotel = r.hotel
            if h:
                hotels.append(
                    f"  - {h.hotel_name} ({h.hotel_category or 'standard'}) "
                    f"₹{h.price_per_night}/night, Rating: {h.rating or 'N/A'}"
                )
        if not hotels:
            return ""
        return "RECOMMENDED HOTELS:\n" + "\n".join(hotels)

    @staticmethod
    def _build_expense_context(db: Session, trip_id: str) -> str:
        expense: Optional[TripExpenses] = (
            db.query(TripExpenses)
            .filter(TripExpenses.trip_id == trip_id)
            .first()
        )
        if not expense:
            return ""
        return (
            f"BUDGET BREAKDOWN:\n"
            f"  - Transport:     ₹{expense.transport_cost:,.0f}\n"
            f"  - Accommodation: ₹{expense.accommodation_cost:,.0f}\n"
            f"  - Food:          ₹{expense.food_cost:,.0f}\n"
            f"  - Activities:    ₹{expense.activity_cost:,.0f}\n"
            f"  - Miscellaneous: ₹{expense.miscellaneous_cost:,.0f}"
        )

    @staticmethod
    def _get_trip(db: Session, trip_id: str, user: User) -> Trip:
        trip = db.query(Trip).filter(
            Trip.id == trip_id,
            Trip.user_id == user.id,
        ).first()
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found or does not belong to you",
            )
        return trip

    # ── Legacy alias ──────────────────────────────────────────────────────────

    @staticmethod
    def generate_and_save(db, trip_id, source, destination, days, travelers, budget, travel_mode=""):
        """Backwards-compat wrapper — returns markdown string."""
        from app.services.ai_service import AIService
        ai = AIService()
        markdown = ai.generate_itinerary(source, destination, days, travelers, budget)
        existing = db.query(Itinerary).filter(
            Itinerary.trip_id == trip_id, Itinerary.day_number == 0
        ).first()
        if existing:
            existing.activities = json.dumps({"markdown": markdown})
            existing.title = f"{destination} — {days} Day Itinerary"
        else:
            db.add(Itinerary(
                trip_id=trip_id, day_number=0,
                title=f"{destination} — {days} Day Itinerary",
                activities=json.dumps({"markdown": markdown}),
                estimated_cost=budget,
            ))
        db.commit()
        return markdown

    @staticmethod
    def get_for_trip(db, trip_id):
        records = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).all()
        if not records:
            raise HTTPException(status_code=404, detail="No itinerary found for this trip")
        return records
