from openai import OpenAI, OpenAIError

from app.config import settings


class AIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_itinerary(
        self,
        source: str,
        destination: str,
        days: int,
        travelers: int,
        budget: float,
    ) -> str:
        """Generate a detailed markdown itinerary via GPT-4o-mini."""
        prompt = f"""
You are an expert travel planner. Create a detailed {days}-day travel itinerary for {travelers} traveler(s)
travelling from {source} to {destination} with a total budget of ${budget:,.0f} USD.

Format your response in **Markdown** and include the following sections:

## ✈️ Trip Overview
- Source, destination, duration, number of travelers, total budget

## 📅 Day-by-Day Itinerary
For each day include:
- **Morning**, **Afternoon**, and **Evening** activities
- Recommended restaurants for meals
- Any tickets/bookings required

## 🏨 Accommodation Suggestions
- 3 options across budget, mid-range, and luxury tiers with estimated nightly cost

## 💰 Budget Breakdown
| Category        | Estimated Cost (USD) |
|-----------------|----------------------|
| Flights         | $xxx                 |
| Accommodation   | $xxx                 |
| Food & Dining   | $xxx                 |
| Activities      | $xxx                 |
| Local Transport | $xxx                 |
| Miscellaneous   | $xxx                 |
| **Total**       | **$xxx**             |

## 💡 Travel Tips
- 3–5 practical tips for this destination
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a knowledgeable and friendly travel planning assistant. "
                            "Always respond in well-structured Markdown."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=3000,
            )
            return response.choices[0].message.content

        except OpenAIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e
