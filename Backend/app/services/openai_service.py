import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()


class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
        self.client = OpenAI(api_key=api_key)

    def generate_itinerary(
        self,
        source: str,
        destination: str,
        days: int,
        travelers: int,
        budget: float,
    ) -> str:
        """
        Crafts a structured travel prompt and calls gpt-4o-mini.
        Returns a detailed markdown itinerary including a budget layout.
        """
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
Provide an estimated breakdown as a table:
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
