"""
Destination Research Agent

Narrow responsibility: given a TripRequest, produce DestinationNotes
(overview, areas to stay, attractions, local tips). This is the only
agent that reasons freely about "what is this place like" -- every
downstream agent treats its output as ground truth, so the itinerary
agent is told to use ONLY the attractions this agent returns.
"""

from agents import call_gemini, safe_json_loads
from shared_schema import DestinationNotes, TripRequest


def destination_agent(trip: TripRequest) -> DestinationNotes:
    prompt = f"""You are a travel research assistant. For {trip.destination},
provide:
- a 2-sentence overview
- 3 good areas to stay
- 5 top attractions matching these interests: {trip.interests or "general sightseeing"}
- 3 practical local tips

Respond ONLY with JSON matching this exact schema, no markdown fences, no preamble:
{{
  "overview": "string",
  "best_areas_to_stay": ["string", "string", "string"],
  "top_attractions": ["string", "string", "string", "string", "string"],
  "local_tips": ["string", "string", "string"]
}}"""

    raw = call_gemini(prompt)
    data = safe_json_loads(raw)
    return DestinationNotes(
        overview=data.get("overview", ""),
        best_areas_to_stay=data.get("best_areas_to_stay", []),
        top_attractions=data.get("top_attractions", []),
        local_tips=data.get("local_tips", []),
    )
