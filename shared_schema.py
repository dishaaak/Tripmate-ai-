"""
shared_schema.py

Single source of truth for the data that flows between agents.
No agent should invent fields outside these dataclasses -- that
constraint is what keeps the pipeline hallucination-resistant.
"""

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class TripRequest:
    destination: str
    start_date: str          # ISO format YYYY-MM-DD
    end_date: str             # ISO format YYYY-MM-DD
    budget_total: float
    num_travelers: int
    interests: list[str] = field(default_factory=list)

    @property
    def num_days(self) -> int:
        start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        return max((end - start).days + 1, 1)


@dataclass
class DestinationNotes:
    overview: str
    best_areas_to_stay: list[str] = field(default_factory=list)
    top_attractions: list[str] = field(default_factory=list)
    local_tips: list[str] = field(default_factory=list)


@dataclass
class BudgetPlan:
    total: float
    accommodation: float
    food: float
    transport: float
    activities: float
    buffer: float
    notes: str = ""


@dataclass
class DayPlan:
    day_number: int
    date: str
    weather_summary: str
    morning: str
    afternoon: str
    evening: str
    estimated_cost: float = 0.0


@dataclass
class TripPlan:
    destination_notes: DestinationNotes
    budget: BudgetPlan
    itinerary: list[DayPlan] = field(default_factory=list)
    packing_checklist: list[str] = field(default_factory=list)
