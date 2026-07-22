"""
Streamlit frontend for TripMate AI.

Run with: streamlit run ui/app.py   (from the repo root)
"""

import os
import sys

import streamlit as st

# allow `import shared_schema`, `import agents...` etc. when run
# directly as a script rather than as a module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from orchestrator.trip_pipeline import run_trip_pipeline
from shared_schema import TripRequest

load_dotenv()

st.set_page_config(page_title="TripMate AI", page_icon="🧳", layout="wide")

st.title("🧳 TripMate AI")
st.caption("A small multi-agent travel planner: destination research → budget → weather-aware itinerary → packing list.")

# --- session state: persist the plan across reruns (e.g. when a checkbox is clicked) ---
if "plan" not in st.session_state:
    st.session_state.plan = None
if "timings" not in st.session_state:
    st.session_state.timings = None
if "destination" not in st.session_state:
    st.session_state.destination = None

with st.sidebar:
    st.header("Trip details")
    destination = st.text_input("Destination", placeholder="e.g. Jaipur, India")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date")
    with col2:
        end_date = st.date_input("End date")
    budget_total = st.number_input("Total budget", min_value=0.0, value=50000.0, step=1000.0)
    num_travelers = st.number_input("Travelers", min_value=1, value=2, step=1)
    interests_raw = st.text_input("Interests (comma-separated)", placeholder="history, food, nightlife")
    go = st.button("Plan my trip", type="primary", use_container_width=True)

# --- only recompute the plan when the button is actually clicked ---
if go:
    if not destination:
        st.error("Please enter a destination.")
        st.stop()
    if end_date < start_date:
        st.error("End date must be on or after the start date.")
        st.stop()

    trip = TripRequest(
        destination=destination,
        start_date=str(start_date),
        end_date=str(end_date),
        budget_total=budget_total,
        num_travelers=int(num_travelers),
        interests=[i.strip() for i in interests_raw.split(",") if i.strip()],
    )

    with st.spinner(f"Planning {trip.num_days}-day trip to {destination}..."):
        try:
            plan, timings = run_trip_pipeline(trip)
        except RuntimeError as e:
            st.error(str(e))
            st.stop()

    # save to session_state so it survives reruns triggered by later widget clicks
    st.session_state.plan = plan
    st.session_state.timings = timings
    st.session_state.destination = destination

# --- render from session_state, not from the button/local variables ---
if st.session_state.plan is not None:
    plan = st.session_state.plan
    timings = st.session_state.timings
    destination = st.session_state.destination

    st.success(f"Done in {timings['total']:.1f}s")

    st.subheader("📍 Destination overview")
    st.write(plan.destination_notes.overview)
    c1, c2, c3 = st.columns(3)
    c1.markdown("**Best areas to stay**\n\n" + "\n".join(f"- {a}" for a in plan.destination_notes.best_areas_to_stay))
    c2.markdown("**Top attractions**\n\n" + "\n".join(f"- {a}" for a in plan.destination_notes.top_attractions))
    c3.markdown("**Local tips**\n\n" + "\n".join(f"- {t}" for t in plan.destination_notes.local_tips))

    st.subheader("💰 Budget breakdown")
    b = plan.budget
    bc1, bc2, bc3, bc4, bc5 = st.columns(5)
    bc1.metric("Accommodation", f"{b.accommodation:,.0f}")
    bc2.metric("Food", f"{b.food:,.0f}")
    bc3.metric("Transport", f"{b.transport:,.0f}")
    bc4.metric("Activities", f"{b.activities:,.0f}")
    bc5.metric("Buffer", f"{b.buffer:,.0f}")
    st.caption(b.notes)

    st.subheader("🗓️ Day-wise itinerary")
    for day in plan.itinerary:
        with st.expander(f"Day {day.day_number} — {day.date}  ({day.weather_summary})"):
            st.markdown(f"**Morning:** {day.morning}")
            st.markdown(f"**Afternoon:** {day.afternoon}")
            st.markdown(f"**Evening:** {day.evening}")
            st.caption(f"Estimated cost: {day.estimated_cost:,.0f}")

    st.subheader("🎒 Packing checklist")
    for item in plan.packing_checklist:
        st.checkbox(item, key=item)

    with st.expander("Pipeline timing (debug)"):
        st.json(timings)
else:
    st.info("Fill in trip details in the sidebar and click **Plan my trip**.")
