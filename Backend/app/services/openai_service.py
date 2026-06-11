from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_itinerary(
    destination: str,
    duration_days: int,
    budget: str,
    travel_style: str | None,
    num_travelers: int,
) -> str:
    """
    Calls OpenAI to generate a day-by-day travel itinerary.
    Returns the raw text/JSON string from the model.
    """
    style_note = f"Travel style: {travel_style}." if travel_style else ""

    prompt = f"""
You are an expert travel planner. Create a detailed {duration_days}-day itinerary for {num_travelers} traveler(s) 
visiting {destination} with a budget of {budget}. {style_note}

Return ONLY valid JSON in exactly this structure (no extra text):
{{
  "destination": "{destination}",
  "duration_days": {duration_days},
  "budget": "{budget}",
  "summary": "<2-sentence overview>",
  "days": [
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
            {"role": "system", "content": "You are a helpful travel planning assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=3000,
    )

    return response.choices[0].message.content
