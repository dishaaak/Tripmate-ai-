"""
Weather service

Deliberately NOT an LLM call. Weather is a real, checkable fact,
so it comes from OpenWeatherMap's free-tier forecast endpoint.
This is what lets the Itinerary Agent make weather-aware decisions
instead of guessing ("probably sunny in spring") the way a naive
single-prompt tool would.

Limitation (worth stating honestly in your docs): the free-tier
forecast endpoint only covers ~5 days out in 3-hour steps, so a day
outside that window falls back to a generic "forecast unavailable"
placeholder rather than a fabricated guess.
"""

import os
from collections import defaultdict
from datetime import datetime

import requests

OWM_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"


def get_weather_by_day(city: str, start_date: str, end_date: str) -> dict[str, str]:
    """Returns {date_str: weather_summary} for each day in range.
    Falls back to a clearly-labeled placeholder for days the free
    forecast API can't reach, or if no API key is configured --
    it never invents a plausible-sounding forecast."""
    api_key = os.environ.get("OWM_API_KEY")
    dates = _date_range(start_date, end_date)

    if not api_key:
        return {d: "forecast unavailable (no OWM_API_KEY configured)" for d in dates}

    try:
        resp = requests.get(
            OWM_BASE_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException:
        return {d: "forecast unavailable (weather API error)" for d in dates}

    by_day = defaultdict(list)
    for entry in payload.get("list", []):
        day = entry["dt_txt"].split(" ")[0]
        desc = entry["weather"][0]["description"]
        temp = entry["main"]["temp"]
        by_day[day].append(f"{desc}, {temp:.0f}°C")

    summaries = {}
    for d in dates:
        readings = by_day.get(d)
        if readings:
            # midday reading (roughly index 4 of 8x 3-hour slots) is
            # the most representative single number for the day
            summaries[d] = readings[min(4, len(readings) - 1)]
        else:
            summaries[d] = "outside 5-day forecast window"
    return summaries


def _date_range(start_date: str, end_date: str) -> list[str]:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    days = (end - start).days + 1
    return [str(start.fromordinal(start.toordinal() + i)) for i in range(max(days, 1))]
