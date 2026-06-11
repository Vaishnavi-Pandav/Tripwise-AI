import logging

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger("tripwise")

SYSTEM_INSTRUCTION = (
    "You are TripWise AI, an expert travel planning assistant. "
    "Help users plan trips, estimate budgets, suggest destinations, "
    "find hidden gems, and answer all travel-related questions. "
    "Be concise, helpful, and friendly."
)


class AIService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model  = settings.GEMINI_MODEL

    def chat(self, message: str) -> str:
        """General-purpose AI travel assistant chat."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.7,
                    max_output_tokens=1000,
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            raise RuntimeError(f"Gemini API error: {str(e)}") from e

    def generate_itinerary(
        self,
        source: str,
        destination: str,
        days: int,
        travelers: int,
        budget: float,
    ) -> str:
        """Generate a detailed markdown travel itinerary using Gemini."""
        prompt = f"""
Create a detailed {days}-day itinerary for {travelers} traveler(s)
travelling from {source} to {destination} with a total budget of ₹{budget:,.0f}.

Format your response in **Markdown** and include:

## ✈️ Trip Overview
- Source, destination, duration, number of travelers, total budget

## 📅 Day-by-Day Itinerary
For each day include **Morning**, **Afternoon**, and **Evening** activities
with restaurant suggestions and any booking requirements.

## 🏨 Accommodation Suggestions
3 options across budget, mid-range, and luxury tiers with estimated nightly cost.

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
                    system_instruction="You are a travel planning assistant. Respond in well-structured Markdown.",
                    temperature=0.7,
                    max_output_tokens=3000,
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini itinerary error: {e}")
            raise RuntimeError(f"Gemini API error: {str(e)}") from e
