from openai import OpenAI, OpenAIError

from app.core.config import settings


class AIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def chat(self, message: str) -> str:
        """General-purpose AI travel assistant chat."""
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are TripWise AI, an expert travel planning assistant. "
                            "Help users plan trips, estimate budgets, suggest destinations, "
                            "find hidden gems, and answer all travel-related questions. "
                            "Be concise, helpful, and friendly."
                        ),
                    },
                    {"role": "user", "content": message},
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e

    def generate_itinerary(
        self,
        source: str,
        destination: str,
        days: int,
        travelers: int,
        budget: float,
    ) -> str:
        prompt = f"""
You are an expert travel planner. Create a detailed {days}-day itinerary for {travelers} traveler(s)
from {source} to {destination} with a total budget of ${budget:,.0f} USD.

Format in **Markdown** with:
## ✈️ Trip Overview
## 📅 Day-by-Day Itinerary (Morning / Afternoon / Evening for each day)
## 🏨 Accommodation Suggestions (budget / mid-range / luxury with prices)
## 💰 Budget Breakdown (as a table)
## 💡 Travel Tips (3-5 tips)
"""
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a travel planning assistant. Respond in Markdown."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=3000,
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e
