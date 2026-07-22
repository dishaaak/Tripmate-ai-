"""
Itinerary Agent

The synthesis step. It is told to use ONLY the attractions the
Destination Agent already found -- this is the hallucination
guardrail: the itinerary can never invent a place that wasn't
independently researched. It is also handed real weather (not
LLM-guessed weather) so it can move outdoor activities on rainy
days.
"""

from agents import call_gemini, safe_json_loads
from shared_schema import BudgetPlan, DayPlan, DestinationNotes, TripRequest


def itinerary_agent(
    trip: TripRequest,
    dest_notes: DestinationNotes,
    budget: BudgetPlan,
    weather_by_day: dict[str, str],
) -> list[DayPlan]:
    num_days = trip.num_days
    daily_activity_budget = budget.activities / num_days if num_days else 0

    prompt = f"""Create a day-wise itinerary for {trip.destination} from
{trip.start_date} to {trip.end_date} ({num_days} days).

Use ONLY these attractions -- do not invent any others:
{dest_notes.top_attractions}

Daily activity budget: approximately {daily_activity_budget:.0f} (local currency).
Weather per day: {weather_by_day}

Adjust indoor/outdoor activities based on the weather for each day.

Respond ONLY with a JSON object of this exact shape, no markdown fences, no preamble:
{{
  "days": [
    {{
      "day_number": 1,
      "date": "YYYY-MM-DD",
      "weather_summary": "string",
      "morning": "string",
      "afternoon": "string",
      "evening": "string",
      "estimated_cost": 0
    }}
  ]
}}"""

    raw = call_gemini(prompt)
    data = safe_json_loads(raw)

    return [
        DayPlan(
            day_number=d.get("day_number", i + 1),
            date=d.get("date", ""),
            weather_summary=d.get("weather_summary", ""),
            morning=d.get("morning", ""),
            afternoon=d.get("afternoon", ""),
            evening=d.get("evening", ""),
            estimated_cost=float(d.get("estimated_cost", 0) or 0),
        )
        for i, d in enumerate(data.get("days", []))
    ]
