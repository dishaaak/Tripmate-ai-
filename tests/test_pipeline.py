"""
Integration test for the trip pipeline.

"""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared_schema import TripRequest

DEST_JSON = (
    '{"overview": "A test city.", "best_areas_to_stay": ["Old Town"], '
    '"top_attractions": ["Fort", "Museum"], "local_tips": ["Carry water"]}'
)
ITIN_JSON = (
    '{"days": [{"day_number": 1, "date": "2026-08-01", '
    '"weather_summary": "unavailable", "morning": "Visit Fort", '
    '"afternoon": "Museum", "evening": "Dinner", "estimated_cost": 1000}]}'
)
PACKING_JSON = '{"packing_checklist": ["Water bottle", "Comfortable shoes"]}'


@patch("agents.call_gemini")
@patch("services.weather_service.requests.get")
def test_pipeline_runs_end_to_end(mock_weather_get, mock_call_gemini):
    from orchestrator.trip_pipeline import run_trip_pipeline

    # destination_agent -> itinerary_agent -> packing_agent, in call order
    mock_call_gemini.side_effect = [DEST_JSON, ITIN_JSON, PACKING_JSON]

    # No OWM_API_KEY set in test env -> weather_service falls back
    # cleanly without ever hitting requests.get, so mock is unused
    # but present in case that changes.
    os.environ.pop("OWM_API_KEY", None)

    trip = TripRequest(
        destination="Test City",
        start_date="2026-08-01",
        end_date="2026-08-01",
        budget_total=10000,
        num_travelers=2,
        interests=["history"],
    )

    plan, timings = run_trip_pipeline(trip)

    assert plan.destination_notes.overview == "A test city."
    assert len(plan.itinerary) == 1
    assert plan.itinerary[0].morning == "Visit Fort"
    assert plan.packing_checklist == ["Water bottle", "Comfortable shoes"]
    assert plan.budget.total == 10000
    assert plan.budget.accommodation == 3500  # 35% split
    assert "total" in timings


if __name__ == "__main__":
    test_pipeline_runs_end_to_end()
    print("OK")
