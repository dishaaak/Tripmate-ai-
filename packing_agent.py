"""
Packing Checklist Agent

Cheapest agent in the pipeline: one short LLM call, grounded only
in weather conditions and trip length. Runs last since it depends
on nothing but facts already gathered.
"""

from agents import call_gemini, safe_json_loads


def packing_agent(weather_by_day: dict[str, str], trip_length: int) -> list[str]:
    prompt = f"""Generate a packing checklist for a {trip_length}-day trip
with this weather forecast: {weather_by_day}

Respond ONLY with JSON of this exact shape, no markdown fences, no preamble:
{{"packing_checklist": ["item 1", "item 2", "..."]}}"""

    raw = call_gemini(prompt)
    data = safe_json_loads(raw)
    return data.get("packing_checklist", [])
