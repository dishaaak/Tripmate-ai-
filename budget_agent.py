"""
Budget Agent

Deliberately has no LLM call. A percentage split is a formula, not
a reasoning task -- using an LLM here would just add latency and
non-determinism for zero benefit. This mirrors the "don't use an
LLM where a formula works better" principle from the reference
RepoAudit project's scoring engine.
"""

from shared_schema import BudgetPlan, TripRequest

# Standard travel-budget split. Documented here so it's easy to
# defend / tune in the capstone writeup.
SPLIT = {
    "accommodation": 0.35,
    "food": 0.25,
    "transport": 0.20,
    "activities": 0.15,
    "buffer": 0.05,
}


def budget_agent(trip: TripRequest) -> BudgetPlan:
    total = trip.budget_total
    return BudgetPlan(
        total=total,
        accommodation=round(total * SPLIT["accommodation"], 2),
        food=round(total * SPLIT["food"], 2),
        transport=round(total * SPLIT["transport"], 2),
        activities=round(total * SPLIT["activities"], 2),
        buffer=round(total * SPLIT["buffer"], 2),
        notes=(
            "Standard 35/25/20/15/5 split (accommodation/food/"
            "transport/activities/buffer). Adjust manually for "
            "luxury vs. budget travel style."
        ),
    )
