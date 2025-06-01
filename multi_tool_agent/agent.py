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


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time in a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string"},
                },
                "required": ["city"],
            },
        },
    },
]

root_agent = Agent(
    model=LiteLlm(
        model="bedrock/mistral.mistral-7b-instruct-v0:2",
        tools=tools,
        tool_choice="auto",
    ),
)
