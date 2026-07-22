
"""
Trip pipeline

Sequential orchestrator: this is the piece that makes the system
"multi-agent" rather than one long prompt. Each agent has a single
responsibility and hands structured output (never raw text) to the
next stage. A hand-rolled function is enough here -- the flow is
strictly linear (no branching / retries based on agent output), so
a framework like LangGraph would add complexity without adding
capability.
"""

import logging
import time

from agents.budget_agent import budget_agent
from agents.destination_agent import destination_agent
from agents.itinerary_agent import itinerary_agent
from agents.packing_agent import packing_agent
from services.weather_service import get_weather_by_day
from shared_schema import TripPlan, TripRequest

logger = logging.getLogger("tripmate.pipeline")


def run_trip_pipeline(trip: TripRequest) -> tuple[TripPlan, dict]:
    """Runs the full pipeline and returns (TripPlan, timing_info).

    timing_info is returned separately (not part of TripPlan) since
    it's operational/debug data, not something a user-facing trip
    plan should carry.
    """
    timings = {}

    t0 = time.perf_counter()
    dest_notes = destination_agent(trip)
    timings["destination_agent"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    budget = budget_agent(trip)
    timings["budget_agent"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    weather_by_day = get_weather_by_day(trip.destination, trip.start_date, trip.end_date)
    timings["weather_service"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    itinerary = itinerary_agent(trip, dest_notes, budget, weather_by_day)
    timings["itinerary_agent"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    packing_checklist = packing_agent(weather_by_day, trip.num_days)
    timings["packing_agent"] = time.perf_counter() - t0

    timings["total"] = sum(timings.values())
    logger.info("Pipeline timings: %s", timings)

    plan = TripPlan(
        destination_notes=dest_notes,
        budget=budget,
        itinerary=itinerary,
        packing_checklist=packing_checklist,
    )
    return plan, timings
