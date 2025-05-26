"""
Agent definition and tool functions.

This module is imported by main.py, so keep side‑effects (env‑vars, logging)
near the top to guarantee they run before any Bedrock / ADK code loads.
"""

from __future__ import annotations

import os
import datetime as _dt
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# --------------------------------------------------------------------------- #
#  Runtime configuration
# --------------------------------------------------------------------------- #
# Tell ADK to use Amazon Bedrock and pin a region before the SDK initialises.
os.environ.setdefault("ADK_DEFAULT_BACKEND", "bedrock")
os.environ.setdefault(
    "AWS_REGION", "us-west-2"
)  # change if your Bedrock lives elsewhere

# Basic structured logging (CloudWatch will merge JSON nicely if you want to
# switch to python-json-logger later).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

# ADK import happens *after* env‑vars are set
from google.adk.agents import Agent  # noqa: E402  (import after env vars)


# --------------------------------------------------------------------------- #
#  Tool definitions
# --------------------------------------------------------------------------- #
def get_weather(city: str) -> dict:
    """
    Demo weather tool – replace with a real provider later.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is totally sunny with a temperature "
                "of 25 °C / 77 °F."
            ),
        }

    return {
        "status": "error",
        "error_message": f"Weather information for '{city}' is not available.",
    }


def get_current_time(city: str) -> dict:
    """
    Returns the local time for supported cities (only New York in this demo).
    Falls back to UTC if the tz database is missing in the container.
    """
    if city.lower() != "new york":
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have timezone information for {city}.",
        }

    try:
        tz = ZoneInfo("America/New_York")
    except ZoneInfoNotFoundError as exc:
        log.warning("tzdata missing, using UTC fallback: %s", exc)
        tz = ZoneInfo("UTC")

    now = _dt.datetime.now(tz)
    return {
        "status": "success",
        "report": f"The current time in {city} is {now:%Y-%m-%d %H:%M:%S %Z%z}.",
    }


# --------------------------------------------------------------------------- #
#  Root agent
# --------------------------------------------------------------------------- #
root_agent = Agent(
    name="weather_time_agent",
    description="Answers questions about time and weather in a city.",
    instruction="Be helpful, accurate, and concise.",
    model="bedrock:foundation-model/mistral.mistral-7b-instruct-v0:0",
    tools=[get_weather, get_current_time],
)
