# multi_tool_agent/agent.py
import os, logging, datetime as _dt
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

os.environ.setdefault("ADK_DEFAULT_BACKEND", "bedrock")
os.environ.setdefault("AWS_REGION", "us-west-2")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger(__name__)


# ✅ Use primitive parameters
def get_weather(city: str) -> dict:
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "The weather in New York is totally sunny with a temperature of 25 °C / 77 °F.",
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
    now = _dt.datetime.now(ZoneInfo("America/New_York"))
    return {
        "status": "success",
        "report": f"The current time in {city} is {now:%Y-%m-%d %H:%M:%S %Z%z}.",
    }


root_agent = Agent(
    name="weather_and_time_assistant",
    description="Answers questions about time and weather in a city.",
    instruction="Be helpful, accurate, and concise.",
    model="bedrock:foundation-model/mistral.mistral-7b-instruct-v0:0",
    tools=[get_weather, get_current_time],
)
