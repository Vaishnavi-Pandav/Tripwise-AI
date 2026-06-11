from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_itinerary(
    source: str,
    destination: str,
    days: int,
    travelers: int,
    budget: float,
) -> str:
    """
    Calls OpenAI to generate a day-by-day travel itinerary.
    Returns a JSON string from the model.
    """
    prompt = f"""
You are an expert travel planner. Create a detailed {days}-day itinerary for {travelers} traveler(s)
travelling from {source} to {destination} with a total budget of ${budget:.0f} USD.

Return ONLY valid JSON in exactly this structure (no extra text):
{{
  "source": "{source}",
  "destination": "{destination}",
  "days": {days},
  "travelers": {travelers},
  "budget": {budget},
  "summary": "<2-sentence overview>",
  "days_plan": [
    {{
      "day": 1,
      "title": "<Day title>",
      "activities": [
        {{
          "time": "Morning",
          "activity": "<activity name>",
          "description": "<short description>",
          "estimated_cost": "<cost in USD>"
        }}
      ],
      "accommodation": "<hotel/hostel suggestion>",
      "meals": {{
        "breakfast": "<suggestion>",
        "lunch": "<suggestion>",
        "dinner": "<suggestion>"
      }}
    }}
  ],
  "tips": ["<tip1>", "<tip2>", "<tip3>"]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful travel planning assistant. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=3000,
    )

    return response.choices[0].message.content
