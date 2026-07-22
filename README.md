# TripMate AI

A small, beginner-friendly multi-agent travel planner built with Streamlit and Google Gemini.

Given a plain-language trip request, TripMate AI runs a short pipeline of narrow-responsibility
agents — each with a single job, passing structured output to the next — and produces a
destination overview, a budget breakdown, a weather-aware day-by-day itinerary, and a packing
checklist.

## Why "multi-agent" and not one big prompt

Each stage below is a separate function with a single responsibility and a structured
input/output contract (`shared_schema.py`). No agent invents fields outside that schema. This is
what makes the system multi-agent rather than "one LLM call with a long prompt" — it also makes
each stage independently testable and keeps hallucination risk contained to the stage it
originates in (e.g. the itinerary agent is restricted to only using attractions the destination
agent already found).

```
User input (plain language trip request)
        |
   TripRequest (parsed)
        |
  +-----------------------------------------------+
  |               Orchestrator (sequential)         |
  +-----------------------------------------------+
        |                |                 |
Destination Agent   Budget Agent      Weather Service
 (LLM: research)    (deterministic     (real API call,
                      math, no LLM)      not LLM-guessed)
        |                |                 |
        +--------> Itinerary Agent <-------+
                (LLM: synthesizes day-wise
                 plan from destination facts
                 + budget + real weather)
                          |
                  Packing Checklist Agent
                  (LLM, grounded in weather
                   + trip length)
                          |
                  TripPlan -> Streamlit UI
```

## Tech stack

| Component | Tool |
|---|---|
| LLM | Google Gemini `gemini-3.5-flash`, called via plain REST (`requests`), free tier |
| Orchestration | Hand-rolled sequential Python (no framework — the flow is linear, so LangGraph/CrewAI would add complexity without adding capability) |
| Weather | OpenWeatherMap free-tier forecast API (real data, not LLM-guessed) |
| Frontend | Streamlit |
| Shared contract | `shared_schema.py` dataclasses |

## Repo structure

```
tripmate-ai/
├── shared_schema.py           # TripRequest, DestinationNotes, BudgetPlan, DayPlan, TripPlan
├── agents/
│   ├── destination_agent.py   # LLM: destination research, grounded in interests
│   ├── budget_agent.py        # deterministic % split, no LLM
│   ├── itinerary_agent.py     # LLM: synthesizes day plan from prior agents' output
│   └── packing_agent.py       # LLM: grounded in weather + trip length
├── services/
│   └── weather_service.py     # real OpenWeatherMap API call, not an agent
├── orchestrator/
│   └── trip_pipeline.py       # runs agents in sequence, times each stage
├── ui/
│   └── app.py                 # Streamlit interface
├── tests/
│   └── test_pipeline.py       # end-to-end test with mocked LLM/weather calls
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. Clone the repo and `cd tripmate-ai`
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate     # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your keys:
   ```
   GEMINI_API_KEY=your_key_here   # free at https://aistudio.google.com/apikey
   OWM_API_KEY=your_key_here      # optional — falls back gracefully without it
   ```
5. Run the app:
   ```bash
   streamlit run ui/app.py
   ```

## Running tests

```bash
python -m pytest tests/
```

The test mocks both external calls (Gemini, OpenWeatherMap) so it runs offline without API keys —
it validates the pipeline wiring, not the LLM's output quality.

## Known limitations

- **Weather coverage**: OpenWeatherMap's free-tier forecast only covers ~5 days out. Trips (or
  trip days) beyond that window show "outside 5-day forecast window" rather than a guessed
  forecast.
- **Nearby attractions**: sourced from the Destination Agent's own knowledge, not a live places
  API. Flag this as a limitation rather than presenting it as verified data.
- **No persistence**: each planning run is stateless; nothing is saved between sessions.
- **Cost/latency**: three sequential LLM calls (destination, itinerary, packing) means total
  latency is additive — report this honestly in an evaluation section rather than only reporting
  best-case timing.

##TEAM MEMBERS

Project Link: https://github.com/dishaaak/Tripmate-AI

Team: [Shashwat] · [Ritika] · [Harshita]· [Mayuri] · [Dishaa]


<p align="right">(<a href="#readme-top">back to top</a>)</p>
