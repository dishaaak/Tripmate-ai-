"""
agents package

Each module here is one narrow-responsibility agent: it takes a
piece of TripRequest / prior agent output and returns a piece of
TripPlan. No agent talks to another agent directly -- the
orchestrator wires them together (see orchestrator/trip_pipeline.py).

LLM calls go through Google Gemini's REST API directly (via
`requests`) rather than a heavier SDK, to keep dependencies minimal
and match the plain-`requests` style already used in
services/weather_service.py.
"""

import json
import os

import requests

GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


def call_gemini(prompt: str) -> str:
    """Single place all agents call into Gemini, so API-key
    handling and error handling only have to be right in one spot."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env "
            "and fill in your key (get one free at "
            "https://aistudio.google.com/apikey)."
        )

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"},
    }

    resp = requests.post(
        GEMINI_URL,
        params={"key": api_key},
        json=body,
        timeout=30,
    )

    if resp.status_code == 429:
        raise RuntimeError(
            "Gemini API rate limit / quota hit. Free tier has request "
            "limits per minute -- wait a bit and try again."
        )
    if resp.status_code == 404:
        raise RuntimeError(
            f"Gemini model '{GEMINI_MODEL}' was not found (it may have "
            "been retired). Check https://ai.google.dev/gemini-api/docs/models "
            "for the current model name and update GEMINI_MODEL in "
            "agents/__init__.py."
        )
    resp.raise_for_status()

    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Gemini response shape: {data}") from e


def safe_json_loads(raw: str) -> dict:
    """LLMs occasionally wrap JSON in markdown fences even when
    asked not to -- strip that defensively before parsing."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())
