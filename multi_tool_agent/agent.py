import os
import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

# Tell ADK to use the Bedrock backend
os.environ["ADK_DEFAULT_BACKEND"] = "bedrock"

# Optional: explicitly configure region
os.environ["AWS_REGION"] = "us-west-2"  # or your preferred Bedrock region


def get_weather(city: str) -> dict:
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is totally sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    return {
        "status": "error",
        "error_message": f"Weather information for '{city}' is not available.",
    }


def get_current_time(city: str) -> dict:
    if city.lower() != "new york":
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have timezone information for {city}.",
        }
    now = datetime.datetime.now(ZoneInfo("America/New_York"))
    return {
        "status": "success",
        "report": f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}",
    }


root_agent = Agent(
    name="weather_time_agent",
    model="bedrock:foundation-model/mistral.mistral-7b-instruct-v0:0",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="Be helpful, accurate, and concise.",
    tools=[get_weather, get_current_time],
)
